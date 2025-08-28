from utility_pack.rotational_quantization import RotationalQuantization, BinaryRotationalQuantization
import numpy as np, faiss, pickle, os, threading, copy, duckdb, json
from utility_pack.vector_storage_helper import ShardedLmdbStorage
from operator import gt, ge, lt, le, ne
import traceback, math, pymongo, heapq
from collections import defaultdict
import scipy.sparse as sp

class MiniVectorDB:
    def __init__(self, storage_file='db.pkl'):
        self.embedding_size = None
        self.storage_file = storage_file
        self.embeddings = None
        self.metadata = []  # Stores dictionaries of metadata
        self.id_map = {}  # Maps embedding row number to unique id
        self.inverse_id_map = {}  # Maps unique id to embedding row number
        self.inverted_index = defaultdict(set)  # Inverted index for metadata
        self.index = None
        self._embeddings_changed = False
        self.lock = threading.Lock()
        self._load_database()

    def _convert_ndarray_float32(self, ndarray):
        return np.array(ndarray, dtype=np.float32)

    def _convert_ndarray_float32_batch(self, ndarrays):
        return [np.array(arr, dtype=np.float32) for arr in ndarrays]

    def _load_database(self):
        if os.path.exists(self.storage_file):
            with self.lock:
                with open(self.storage_file, 'rb') as f:
                    data = pickle.load(f)
                    self.embeddings = data['embeddings']
                    self.embedding_size = data['embeddings'].shape[1] if data['embeddings'] is not None else None
                    self.metadata = data['metadata']
                    self.id_map = data['id_map']
                    self.inverse_id_map = data['inverse_id_map']
                    self.inverted_index = data.get('inverted_index', defaultdict(set))
                if self.embedding_size is not None:
                    self._build_index()

    def _build_index(self):
        self.index = faiss.IndexFlatIP(self.embedding_size)
        if self.embeddings.shape[0] > 0:
            faiss.normalize_L2(self.embeddings)  # Normalize for cosine similarity
            self.index.add(self.embeddings)
            self._embeddings_changed = False

    def get_vector(self, unique_id):
        with self.lock:
            if unique_id not in self.inverse_id_map:
                raise ValueError("Unique ID does not exist.")
            
            row_num = self.inverse_id_map[unique_id]
            return self.embeddings[row_num]

    def store_embedding(self, unique_id, embedding, metadata_dict={}):
        with self.lock:
            if unique_id in self.inverse_id_map:
                raise ValueError("Unique ID already exists.")

            embedding = self._convert_ndarray_float32(embedding)

            if self.embedding_size is None:
                self.embedding_size = embedding.shape[0]

            if self.embeddings is None:
                self.embeddings = np.zeros((0, self.embedding_size), dtype=np.float32)

            row_num = self.embeddings.shape[0]

            self.embeddings = np.vstack([self.embeddings, embedding])
            self.metadata.append(metadata_dict)
            self.id_map[row_num] = unique_id
            self.inverse_id_map[unique_id] = row_num

            # Update the inverted index
            for key, _ in metadata_dict.items():
                self.inverted_index[key].add(unique_id)

            self._embeddings_changed = True

    def store_embeddings_batch(self, unique_ids, embeddings, metadata_dicts=[]):
        with self.lock:
            for uid in unique_ids:
                if uid in self.inverse_id_map:
                    raise ValueError("Unique ID already exists.")
            
            # Convert all embeddings to float32
            embeddings = self._convert_ndarray_float32_batch(embeddings)

            if self.embedding_size is None:
                self.embedding_size = embeddings[0].shape[0]
            
            if self.embeddings is None:
                self.embeddings = np.zeros((0, self.embedding_size), dtype=np.float32)
            
            if len(metadata_dicts) < len(unique_ids) and len(metadata_dicts) > 0:
                raise ValueError("Metadata dictionaries must be provided for all unique IDs.")

            if metadata_dicts == []:
                metadata_dicts = [{} for _ in range(len(unique_ids))]

            row_nums = list(range(self.embeddings.shape[0], self.embeddings.shape[0] + len(embeddings)))
            
            # Stack the embeddings with a single operation
            self.embeddings = np.vstack([self.embeddings, embeddings])
            self.metadata.extend(metadata_dicts)
            self.id_map.update({row_num: unique_id for row_num, unique_id in zip(row_nums, unique_ids)})
            self.inverse_id_map.update({unique_id: row_num for row_num, unique_id in zip(row_nums, unique_ids)})

            # Update the inverted index
            for i, metadata_dict in enumerate(metadata_dicts):
                for key, _ in metadata_dict.items():
                    self.inverted_index[key].add(unique_ids[i])

            self._embeddings_changed = True

    def delete_embedding(self, unique_id):
        if unique_id not in self.inverse_id_map:
            raise ValueError("Unique ID does not exist.")

        with self.lock:
            row_num = self.inverse_id_map[unique_id]
            # Delete the embedding and metadata
            self.embeddings = np.delete(self.embeddings, row_num, 0)
            metadata_to_delete = self.metadata.pop(row_num)

            # Update the inverted index
            for key, _ in metadata_to_delete.items():
                self.inverted_index[key].discard(unique_id)
                if not self.inverted_index[key]:  # If the set is empty, remove the key
                    del self.inverted_index[key]

            # Delete from inverse_id_map
            del self.inverse_id_map[unique_id]

            # Re-index id_map and inverse_id_map
            new_id_map = {}
            new_inverse_id_map = {}

            current_index = 0
            for old_index in sorted(self.id_map.keys()):
                uid = self.id_map[old_index]
                if uid == unique_id:
                    continue  # Skip the deleted unique_id
                new_id_map[current_index] = uid
                new_inverse_id_map[uid] = current_index
                current_index += 1

            self.id_map = new_id_map
            self.inverse_id_map = new_inverse_id_map

            # Since we've modified the embeddings, we must rebuild the index before the next search
            self._embeddings_changed = True

    def _apply_or_filter(self, or_filters):
        result_indices = set()
        for filter in or_filters:
            key_indices = set()
            for key, value in filter.items():
                # Check if the value is a dictionary containing operators
                if isinstance(value, dict):
                    op = next(iter(value))  # Get the operator
                    op_value = value[op]  # Get the value for the operator
                    op_func = {
                        "$gt": gt,
                        "$gte": ge,
                        "$lt": lt,
                        "$lte": le,
                        "$ne": ne,
                        "$in": lambda x, y: y in x,
                    }.get(op, None)
                    if op_func is None:
                        raise ValueError(f"Invalid operator: {op}")

                    try:
                        # Create a copy of the set for iteration
                        inverted_index_copy = self.inverted_index.get(key, set()).copy()

                        key_indices_update = set()

                        # Iterate over each user ID in the inverted index copy
                        for uid in inverted_index_copy:
                            # Get the corresponding index for the user ID from the inverse_id_map
                            if uid not in self.inverse_id_map:
                                continue

                            inverse_id = self.inverse_id_map[uid]

                            metadata = self.metadata[inverse_id]

                            # Get the value for the key from the metadata, if it doesn't exist, return None
                            metadata_value = metadata.get(key, None)

                            # Check if the operation function returns True when applied to the metadata value and the operation value
                            if op_func(metadata_value, op_value):
                                # If it does, add the index to the key_indices_update set
                                key_indices_update.add(inverse_id)

                        # Update the key_indices set with the key_indices_update set
                        key_indices.update(key_indices_update)
                    except KeyError:
                        continue
                else:
                    try:
                        # Create a copy of the set for iteration
                        inverted_index_copy = self.inverted_index.get(key, set()).copy()

                        key_indices_update = set()

                        # Iterate over each user ID in the inverted index copy
                        for uid in inverted_index_copy:
                            # Get the corresponding index for the user ID from the inverse_id_map
                            if uid not in self.inverse_id_map:
                                continue

                            inverse_id = self.inverse_id_map[uid]

                            metadata = self.metadata[inverse_id]

                            # Get the value for the key from the metadata, if it doesn't exist, return None
                            metadata_value = metadata.get(key, None)

                            # Check if the metadata value matches the given value
                            if metadata_value == value:
                                # If it does, add the index to the key_indices_update set
                                key_indices_update.add(inverse_id)

                        # Update the key_indices set with the key_indices_update set
                        key_indices.update(key_indices_update)
                    except KeyError:
                        continue
            result_indices |= key_indices

        return result_indices

    def _apply_and_filter(self, and_filters, filtered_indices):
        for metadata_filter in and_filters:
            for key, value in metadata_filter.items():
                # Check if the value is a dictionary containing operators
                if isinstance(value, dict):
                    op = next(iter(value))  # Get the operator
                    op_value = value[op]  # Get the value for the operator
                    op_func = {
                        "$gt": gt,
                        "$gte": ge,
                        "$lt": lt,
                        "$lte": le,
                        "$ne": ne,
                        "$in": lambda x, y: y in x,
                    }.get(op, None)
                    if op_func is None:
                        raise ValueError(f"Invalid operator: {op}")

                    try:
                        indices = set()

                        # Get the set of user IDs from the inverted index for the given key. If the key is not present, return an empty set.
                        uids = self.inverted_index.get(key, set())

                        # Iterate over each user ID in the set
                        for uid in uids:
                            # Get the corresponding index for the user ID from the inverse_id_map
                            if uid not in self.inverse_id_map:
                                continue

                            inverse_id = self.inverse_id_map[uid]

                            metadata = self.metadata[inverse_id]

                            # Get the value for the key from the metadata, if it doesn't exist, return None
                            metadata_value = metadata.get(key, None)

                            # Check if the operation function returns True when applied to the metadata value and the operation value
                            if op_func(metadata_value, op_value):
                                # If it does, add the index to the indices set
                                indices.add(inverse_id)
                    except KeyError:
                        indices = set()
                else:
                    try:
                        indices = set()

                        # Get the set of user IDs from the inverted index for the given key. If the key is not present, return an empty set.
                        uids = self.inverted_index.get(key, set())

                        # Iterate over each user ID in the set
                        for uid in uids:

                            # Get the corresponding index for the user ID from the inverse_id_map
                            if uid not in self.inverse_id_map:
                                continue

                            inverse_id = self.inverse_id_map[uid]

                            metadata = self.metadata[inverse_id]

                            # Check if the key exists in the metadata and if its value matches the given value
                            if metadata.get(key, None) == value:
                                # If it does, add the index to the indices set
                                indices.add(inverse_id)

                    except KeyError:
                        indices = set()

                if filtered_indices is None:
                    filtered_indices = indices
                else:
                    # Create a copy of filtered_indices for iteration
                    for index in filtered_indices.copy():
                        if index not in indices:
                            filtered_indices.remove(index)

                if not filtered_indices:
                    break
        
        return filtered_indices
    
    def _apply_exclude_filter(self, exclude_filter, filtered_indices):
        for exclude in exclude_filter:
            for key, value in exclude.items():
                try:
                    # Create a copy of the set for iteration
                    inverted_index_copy = self.inverted_index.get(key, set()).copy()

                    exclude_indices = set()

                    # Iterate over each user ID in the inverted index copy
                    for uid in inverted_index_copy:
                        # Get the corresponding index for the user ID from the inverse_id_map
                        if uid not in self.inverse_id_map:
                            continue

                        inverse_id = self.inverse_id_map[uid]

                        metadata = self.metadata[inverse_id]

                        # Get the value for the key from the metadata, if it doesn't exist, return None
                        metadata_value = metadata.get(key, None)

                        # Check if the metadata value matches the given value
                        if metadata_value == value:
                            # If it does, add the index to the exclude_indices set
                            exclude_indices.add(inverse_id)
                except KeyError:
                    exclude_indices = set()
                filtered_indices -= exclude_indices
                if not filtered_indices:
                    break

        return filtered_indices

    def _get_filtered_indices(self, metadata_filters, exclude_filter, or_filters):
        # Initialize filtered_indices with all indices if metadata_filters is not provided
        filtered_indices = set(self.inverse_id_map.values()) if not metadata_filters else None

        # Check if metadata_filters is a dict, if so, convert to list of dicts
        if isinstance(metadata_filters, dict):
            metadata_filters = [metadata_filters]

        # Apply metadata_filters (AND)
        if metadata_filters:
            filtered_indices = self._apply_and_filter(metadata_filters, filtered_indices)

        # Apply OR filters
        if or_filters:
            # Remove all empty dictionaries from or_filters
            if isinstance(or_filters, dict):
                or_filters = [or_filters]
            or_filters = [or_filter for or_filter in or_filters if or_filter]
            if or_filters:
                temp_indices = self._apply_or_filter(or_filters)
                if filtered_indices is None:
                    filtered_indices = temp_indices
                else:
                    filtered_indices &= temp_indices

        # Apply exclude_filter
        if exclude_filter:
            # Check if exclude_filter is a dict, if so, convert to list of dicts
            if isinstance(exclude_filter, dict):
                exclude_filter = [exclude_filter]
            filtered_indices = self._apply_exclude_filter(exclude_filter, filtered_indices)

        return filtered_indices if filtered_indices is not None else set()

    def find_most_similar(self, embedding, metadata_filter=None, exclude_filter=None, or_filters=None, k=5, autocut=False):
        """ or_filters could be a list of dictionaries, where each dictionary contains key-value pairs for OR filters.
        or it could be a single dictionary, which will be equivalent to a list with a single dictionary."""

        if self.embeddings is None:
            return [], [], []

        embedding = self._convert_ndarray_float32(embedding)
        embedding = np.array([embedding])
        faiss.normalize_L2(embedding)

        if self._embeddings_changed:
            with self.lock:
                self._build_index()
        
        with self.lock:
            filtered_indices = self._get_filtered_indices(metadata_filter, exclude_filter, or_filters)

        # If no filtered indices, return empty results
        if not filtered_indices:
            return [], [], []

        # Determine the maximum number of possible matches
        max_possible_matches = min(k, len(filtered_indices))

        found_results = []
        search_k = max_possible_matches

        # Check if filtered_indices corresponds to all possible matches
        if len(filtered_indices) == self.embeddings.shape[0]:
            # Simply perform the search
            distances, indices = self.index.search(embedding, search_k)

            for idx, dist in zip(indices[0], distances[0]):
                if idx == -1:
                    continue  # Skip processing for non-existent indices

                if idx in self.id_map:
                    try:
                        found_results.append((self.id_map[idx], dist, self.metadata[idx]))
                    except KeyError:
                        pass
        else:
            # Otherwise, we create a new index with only the filtered indices
            filtered_embeddings = self.embeddings[list(filtered_indices)]
            filtered_index = faiss.IndexFlatIP(self.embedding_size)
            filtered_index.add(filtered_embeddings)

            distances, indices = filtered_index.search(embedding, search_k)

            for idx, dist in zip(indices[0], distances[0]):
                if idx == -1:
                    continue  # Skip processing for non-existent indices

                try:
                    found_results.append((self.id_map[list(filtered_indices)[idx]], dist, self.metadata[list(filtered_indices)[idx]]))
                except KeyError:
                    pass

        # Unzip the results into separate lists
        ids, distances, metadatas = zip(*found_results) if found_results else ([], [], [])

        return ids, distances, metadatas

    def persist_to_disk(self):
        with self.lock:
            with open(self.storage_file, 'wb') as f:
                data = {
                    'embeddings': self.embeddings,
                    'metadata': self.metadata,
                    'id_map': self.id_map,
                    'inverse_id_map': self.inverse_id_map,
                    'inverted_index': self.inverted_index
                }
                pickle.dump(data, f)

class VectorDB:
    def __init__(self, mongo_uri: str, mongo_database: str, mongo_collection: str, 
                 vector_storage: ShardedLmdbStorage, text_storage: ShardedLmdbStorage,
                 vector_dimension: int, quantization_mode: str = None):
        """
        Initializes the VectorDB.

        :param vector_dimension: The dimension of the vectors.
        :param quantization_mode: The quantization mode to use. Can be '8bit', '1bit', or None.
        """
        self.mongo_uri = mongo_uri
        self.mongo_database = mongo_database
        self.mongo_collection = mongo_collection
        self.mongo_connection = pymongo.MongoClient(self.mongo_uri)
        self.mongo_reference = self.mongo_connection[self.mongo_database][self.mongo_collection]
        self.vector_storage = vector_storage
        self.text_storage = text_storage
        self.quantization_mode = quantization_mode
        self.vector_dimension = vector_dimension
        self.quantizer = None
        
        if self.quantization_mode == '8bit':
            self.quantizer = RotationalQuantization(self.vector_dimension, seed=42)
        elif self.quantization_mode == '1bit':
            self.quantizer = BinaryRotationalQuantization(self.vector_dimension, seed=42)
        elif self.quantization_mode is not None:
            raise ValueError("`quantization_mode` must be '8bit', '1bit', or None.")

    def sync_lmdb_objects(self):
        self.vector_storage.sync()
        self.text_storage.sync()

    def check_counts(self):
        print(f"Vector/Data storage count: {self.vector_storage.get_data_count()}")
        print(f"Text storage count: {self.text_storage.get_data_count()}")
        print(f"MongoDB count: {self.mongo_reference.count_documents({})}")
    
    def get_total_count(self):
        return self.text_storage.get_data_count()

    def ensure_embeddings_typing(self, embeddings):
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings, dtype=np.float32)
        elif embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)
        return embeddings

    def store_embeddings_batch(self, unique_ids: list, embeddings, metadata_dicts=[], text_field=None):
        payload = []
        metadata_dicts_copy = copy.deepcopy(metadata_dicts)
        embeddings = self.ensure_embeddings_typing(embeddings)

        if len(metadata_dicts_copy) < len(unique_ids):
            metadata_dicts_copy.extend([{} for _ in range(len(unique_ids) - len(metadata_dicts_copy))])
        
        texts = [ m.pop(text_field, '') for m in metadata_dicts_copy ] if text_field else [ '' for _ in range(len(unique_ids)) ]

        for uid, metadata_dict in zip(unique_ids, metadata_dicts_copy):
            payload.append({**{ '_id': uid }, **metadata_dict})

        if self.quantization_mode == '8bit':
            quantized_data = [self.quantizer.encode(vec) for vec in embeddings]
            self.vector_storage.store_quantized_vectors(quantized_data, unique_ids)
        elif self.quantization_mode == '1bit':
            quantized_data = [self.quantizer.encode(vec) for vec in embeddings]
            self.vector_storage.store_binary_quantized_vectors(quantized_data, unique_ids)
        elif self.quantization_mode is None:
            self.vector_storage.store_vectors(embeddings, unique_ids)

        self.text_storage.store_data(texts, unique_ids)
        self.mongo_reference.insert_many(payload)
        
        self.sync_lmdb_objects()
        del metadata_dicts_copy
    
    def delete_embeddings_batch(self, unique_ids):
        self.mongo_reference.delete_many({'_id': {'$in': unique_ids}})
        self.vector_storage.delete_data(unique_ids)
        self.text_storage.delete_data(unique_ids)
        self.sync_lmdb_objects()
    
    def delete_embeddings_by_metadata(self, metadata_filters):
        identifiers = list(self.mongo_reference.find(metadata_filters, {'_id': 1}))
        ids_to_delete = [i['_id'] for i in identifiers]
        self.mongo_reference.delete_many({'_id': {'$in': ids_to_delete}})
        self.vector_storage.delete_data(ids_to_delete)
        self.text_storage.delete_data(ids_to_delete)
        self.sync_lmdb_objects()
    
    def get_vector_by_metadata(self, metadata_filters):
        try:
            first_result = self.mongo_reference.find_one({**metadata_filters})
            if first_result is None: return None
            
            if self.quantization_mode == '8bit':
                return self.vector_storage.get_quantized_vectors([first_result['_id']])[0]
            if self.quantization_mode == '1bit':
                return self.vector_storage.get_binary_quantized_vectors([first_result['_id']])[0]
            
            return self.vector_storage.get_vectors([first_result['_id']])[0]
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
        return None

    def _search_quantized(self, query_embedding, corpus_data, corpus_ids, top_k):
        """Helper to search using 8-bit quantized vectors."""
        q_code, q_l, q_delta, q_norm_sq = self.quantizer.encode(query_embedding)
        top_k_heap = []

        for i, (x_code, x_l, x_delta, x_norm_sq) in enumerate(corpus_data):
            corpus_id = corpus_ids[i]
            similarity = self.quantizer.cosine_similarity(
                q_code, q_l, q_delta, q_norm_sq,
                x_code, x_l, x_delta, x_norm_sq
            )

            if len(top_k_heap) < top_k:
                heapq.heappush(top_k_heap, (similarity, corpus_id))
            elif similarity > top_k_heap[0][0]:
                heapq.heapreplace(top_k_heap, (similarity, corpus_id))
        
        sorted_results = sorted(top_k_heap, key=lambda x: x[0], reverse=True)
        ids = [item[1] for item in sorted_results]
        scores = [item[0] for item in sorted_results]
        return ids, scores

    def _search_binary_quantized(self, query_embedding, corpus_data, corpus_ids, top_k):
        """Helper to search using 1-bit quantized vectors."""
        q_codes, q_step, q_norm_sq = self.quantizer.encode_query(query_embedding)
        top_k_heap = []

        for i, (db_packed_bits, db_step, db_norm_sq) in enumerate(corpus_data):
            corpus_id = corpus_ids[i]
            similarity = self.quantizer.cosine_similarity(
                q_codes, q_step, q_norm_sq,
                db_packed_bits, db_step, db_norm_sq
            )

            if len(top_k_heap) < top_k:
                heapq.heappush(top_k_heap, (similarity, corpus_id))
            elif similarity > top_k_heap[0][0]:
                heapq.heapreplace(top_k_heap, (similarity, corpus_id))
        
        sorted_results = sorted(top_k_heap, key=lambda x: x[0], reverse=True)
        ids = [item[1] for item in sorted_results]
        scores = [item[0] for item in sorted_results]
        return ids, scores
    
    def search_faiss(self, query_embeddings, corpus_embeddings, top_k):
        faiss.normalize_L2(corpus_embeddings)
        faiss.normalize_L2(query_embeddings)
        index = faiss.IndexFlatIP(corpus_embeddings.shape[1])
        index.add(corpus_embeddings)
        similarities, indices = index.search(query_embeddings, top_k)
        results = [{"corpus_id": idx, "score": sim} for idx, sim in zip(indices[0], similarities[0]) if idx != -1]
        return results

    def find_most_similar(self, embedding, filters={}, output_fields=[], k=5, use_find_one=False):
        try:
            results = self._fetch_mongo_documents(filters, output_fields, use_find_one)
            if not results: return [], [], []
            
            mongo_ids = [r['_id'] for r in results if '_id' in r]
            
            # Handle quantized vs. float32 search path
            if self.quantization_mode == '8bit':
                quantized_data_raw = self.vector_storage.get_quantized_vectors(mongo_ids)
                corpus_data, corpus_ids = [], []
                for i, data in enumerate(quantized_data_raw):
                    if data:
                        corpus_data.append(data)
                        corpus_ids.append(mongo_ids[i])
                if not corpus_ids: return [], [], []
                
                db_ids, scores = self._search_quantized(embedding, corpus_data, corpus_ids, k)
                return self._prepare_final_results(db_ids, scores, results)

            elif self.quantization_mode == '1bit':
                quantized_data_raw = self.vector_storage.get_binary_quantized_vectors(mongo_ids)
                corpus_data, corpus_ids = [], []
                for i, data in enumerate(quantized_data_raw):
                    if data:
                        corpus_data.append(data)
                        corpus_ids.append(mongo_ids[i])
                if not corpus_ids: return [], [], []

                db_ids, scores = self._search_binary_quantized(embedding, corpus_data, corpus_ids, k)
                return self._prepare_final_results(db_ids, scores, results)

            else: # Original Faiss Path
                vector_ids, vectors, query_embedding, = self._prepare_embeddings(results, embedding)
                if not vector_ids: return [], [], []
                
                index_to_vector_id = { idx: id for idx, id in enumerate(vector_ids) }
                semantic_results = self.search_faiss(
                    query_embeddings=query_embedding, 
                    corpus_embeddings=vectors,
                    top_k=k
                )
                ids = [r['corpus_id'] for r in semantic_results]
                scores = [r['score'] for r in semantic_results]
                db_ids = [index_to_vector_id[id] for id in ids]
                
                seen_ids, unique_db_ids, unique_scores = set(), [], []
                for i, db_id in enumerate(db_ids):
                    if db_id not in seen_ids:
                        seen_ids.add(db_id)
                        unique_db_ids.append(db_id)
                        unique_scores.append(scores[i])
                
                return self._prepare_final_results(unique_db_ids, unique_scores, results)

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            return [], [], []

    def find_most_similar_in_batches(self, embedding, filters={}, output_fields=[], k=5, use_find_one=False, max_ram_usage_gb=2):
        try:
            if use_find_one:
                return self.find_most_similar(embedding, filters, output_fields, k, use_find_one=True)

            total_count = self.mongo_reference.count_documents(filters) if filters else self.mongo_reference.estimated_document_count()
            if total_count == 0: return [], [], []

            query_embedding_np = self.ensure_embeddings_typing(embedding)
            vector_dim = self.vector_dimension

            if self.quantization_mode == '8bit':
                avg_vector_size_bytes = vector_dim + 12
            elif self.quantization_mode == '1bit':
                avg_vector_size_bytes = math.ceil(self.quantizer.padded_dimension / 8) + 8
            else:
                avg_vector_size_bytes = vector_dim * 4

            avg_doc_and_vector_size_bytes = (5 * 1024) + avg_vector_size_bytes
            max_ram_usage_bytes = max_ram_usage_gb * (1024 ** 3)
            batch_size = max(1, min(500000, math.floor(max_ram_usage_bytes / avg_doc_and_vector_size_bytes)))
            total_memory_usage_gb = (total_count * avg_doc_and_vector_size_bytes) / (1024 ** 3)

            if total_memory_usage_gb <= max_ram_usage_gb:
                return self.find_most_similar(embedding, filters, output_fields, k, use_find_one=False)

            top_k_results_heap = []

            for i in range(0, total_count, batch_size):
                batch_mongo_ids_only = self._fetch_mongo_documents(filters, ['_id'], False, limit=batch_size, skip=i)
                if not batch_mongo_ids_only: continue
                
                batch_mongo_ids = [doc['_id'] for doc in batch_mongo_ids_only]

                if self.quantization_mode == '8bit':
                    quantized_data_raw = self.vector_storage.get_quantized_vectors(batch_mongo_ids)
                    q_code, q_l, q_delta, q_norm_sq = self.quantizer.encode(query_embedding_np)
                    for j, data in enumerate(quantized_data_raw):
                        if data:
                            x_code, x_l, x_delta, x_norm_sq = data
                            mongo_id = batch_mongo_ids[j]
                            score = self.quantizer.cosine_similarity(
                                q_code, q_l, q_delta, q_norm_sq,
                                x_code, x_l, x_delta, x_norm_sq
                            )
                            if len(top_k_results_heap) < k or score > top_k_results_heap[0][0]:
                                if len(top_k_results_heap) == k: heapq.heapreplace(top_k_results_heap, (score, mongo_id))
                                else: heapq.heappush(top_k_results_heap, (score, mongo_id))
                elif self.quantization_mode == '1bit':
                    quantized_data_raw = self.vector_storage.get_binary_quantized_vectors(batch_mongo_ids)
                    q_codes, q_step, q_norm_sq = self.quantizer.encode_query(query_embedding_np)
                    for j, data in enumerate(quantized_data_raw):
                        if data:
                            db_packed_bits, db_step, db_norm_sq = data
                            mongo_id = batch_mongo_ids[j]
                            score = self.quantizer.cosine_similarity(
                                q_codes, q_step, q_norm_sq,
                                db_packed_bits, db_step, db_norm_sq
                            )
                            if len(top_k_results_heap) < k or score > top_k_results_heap[0][0]:
                                if len(top_k_results_heap) == k: heapq.heapreplace(top_k_results_heap, (score, mongo_id))
                                else: heapq.heappush(top_k_results_heap, (score, mongo_id))
                else: # Faiss Path
                    vector_ids, vectors, query_embedding = self._prepare_embeddings(batch_mongo_ids_only, embedding)
                    if not vector_ids: continue
                    faiss_index_to_mongo_id = {idx: mongo_id for idx, mongo_id in enumerate(vector_ids)}
                    semantic_results = self.search_faiss(
                        query_embeddings=query_embedding, 
                        corpus_embeddings=vectors,
                        top_k=k
                    )
                    for r in semantic_results:
                        mongo_id, score = faiss_index_to_mongo_id[r['corpus_id']], r['score']
                        if len(top_k_results_heap) < k or score > top_k_results_heap[0][0]:
                            if len(top_k_results_heap) == k: heapq.heapreplace(top_k_results_heap, (score, mongo_id))
                            else: heapq.heappush(top_k_results_heap, (score, mongo_id))

            final_sorted_results = sorted(top_k_results_heap, key=lambda x: x[0], reverse=True)
            final_db_ids = [db_id for _, db_id in final_sorted_results]
            final_scores = [score for score, _ in final_sorted_results]
            
            final_mongo_results = self._fetch_mongo_documents({'_id': {'$in': final_db_ids}}, output_fields, False, enforce_order_ids=final_db_ids)
            return self._prepare_final_results(final_db_ids, final_scores, final_mongo_results)

        except Exception as e:
            print(f"An error occurred in find_most_similar_in_batches: {e}")
            traceback.print_exc()
            return [], [], []

    def _fetch_mongo_documents(self, filters, output_fields, use_find_one, limit=None, skip=None, enforce_order_ids=None):
        projection = {'_id': 1}
        if output_fields != 'all':
            for field in output_fields:
                if field != '_id': projection[field] = 1
        
        if use_find_one:
            doc = self.mongo_reference.find_one(filters, projection)
            return [doc] if doc else []

        cursor = self.mongo_reference.find(filters, projection)
        if limit is not None: cursor = cursor.limit(limit)
        if skip is not None: cursor = cursor.skip(skip)
        result = list(cursor)

        if enforce_order_ids:
            id_map = {doc['_id']: doc for doc in result if '_id' in doc}
            return [id_map.get(_id) for _id in enforce_order_ids]
        return result

    def _prepare_embeddings(self, results, query_embedding):
        mongo_ids = [r['_id'] for r in results if '_id' in r]
        retrieved_vectors_raw = self.vector_storage.get_vectors(mongo_ids)
        
        vector_ids, retrieved_vectors = [], []
        for i, vector in enumerate(retrieved_vectors_raw):
            if vector is not None:
                vector_ids.append(mongo_ids[i])
                retrieved_vectors.append(vector)

        if not vector_ids: return [], [], []

        lmdb_vectors = np.array(retrieved_vectors, dtype=np.float32)
        query_embedding = np.array([query_embedding], dtype=np.float32)
        return vector_ids, lmdb_vectors, query_embedding

    def _prepare_final_results(self, db_ids, scores, mongo_results):
        texts_raw = self.text_storage.get_data(db_ids)
        id_mapped_results = {r['_id']: r for r in mongo_results if '_id' in r}
        
        metadatas = []
        for i, db_id in enumerate(db_ids):
            metadata = id_mapped_results.get(db_id, {})
            if '_id' not in metadata: metadata['_id'] = db_id
            
            text = texts_raw[i] if texts_raw and i < len(texts_raw) and texts_raw[i] is not None else ''
            metadata['text'] = text
            metadatas.append(metadata)

        return db_ids, scores, metadatas

class MongoVectorDB:
    def __init__(self, *args, **kwargs):
        self._instance = VectorDB(*args, **kwargs)

    def __getattr__(self, name):
        # Delegate attribute access to the internal VectorDB instance
        return getattr(self._instance, name)

class HybridVectorDB:
    def __init__(self, mongo_uri: str, mongo_database: str, mongo_collection: str, dense_vector_storage: ShardedLmdbStorage, sparse_vector_storage: ShardedLmdbStorage, text_storage: ShardedLmdbStorage):
        self.mongo_uri = mongo_uri
        self.mongo_database = mongo_database
        self.mongo_collection = mongo_collection
        self.mongo_reference = pymongo.MongoClient(self.mongo_uri)[self.mongo_database][self.mongo_collection]
        self.dense_vector_storage = dense_vector_storage
        self.sparse_vector_storage = sparse_vector_storage
        self.text_storage = text_storage

    def check_counts(self):
        print(f"Dense Vector storage count: {self.dense_vector_storage.get_data_count()}")
        print(f"Sparse Vector storage count: {self.sparse_vector_storage.get_data_count()}")
        print(f"Text storage count: {self.text_storage.get_data_count()}")
        print(f"MongoDB count: {self.mongo_reference.count_documents({})}")
    
    def sync_lmdb_objects(self):
        self.dense_vector_storage.sync()
        self.sparse_vector_storage.sync()
        self.text_storage.sync()
    
    def get_total_count(self):
        return self.text_storage.get_data_count()

    def ensure_embeddings_typing(self, embeddings):
        # Ensure embeddings is a numpy array
        if type(embeddings) is not np.ndarray:
            # Convert embeddings to numpy array 32-bit float
            embeddings = np.array(embeddings, dtype=np.float32)
        return embeddings
    
    def convert_sparse_tensor_to_sparse_matrix(self, sparse_tensor):
        coalesced = sparse_tensor.coalesce()
        indices = coalesced.indices().cpu().numpy()
        values = coalesced.values().cpu().numpy()
        size = coalesced.size()
        scipy_sparse = sp.coo_matrix((values, (indices[0], indices[1])), shape=size)
        return scipy_sparse

    def store_embeddings_batch(self, unique_ids: list, sparse_embeddings, dense_embeddings, metadata_dicts=[], text_field=None):
        payload = []

        metadata_dicts_copy = copy.deepcopy(metadata_dicts)

        dense_embeddings = self.ensure_embeddings_typing(dense_embeddings)
        sparse_embeddings = self.convert_sparse_tensor_to_sparse_matrix(sparse_embeddings)
        
        if len(metadata_dicts_copy) < len(unique_ids):
            metadata_dicts_copy.extend([{} for _ in range(len(unique_ids) - len(metadata_dicts_copy))])
        
        if text_field is not None:
            texts = [ m.pop(text_field, '') for m in metadata_dicts_copy ]
        else:
            texts = [ '' for _ in range(len(unique_ids)) ]

        for uid, metadata_dict in zip(unique_ids, metadata_dicts_copy):
            payload.append({**{ '_id': uid }, **metadata_dict})

        self.dense_vector_storage.store_vectors(dense_embeddings, unique_ids)
        self.sparse_vector_storage.store_sparse_vectors(sparse_embeddings, unique_ids)
        self.text_storage.store_data(texts, unique_ids)
        self.mongo_reference.insert_many(payload)
        self.sync_lmdb_objects()
        del metadata_dicts_copy
    
    def delete_embeddings_batch(self, unique_ids):
        self.mongo_reference.delete_many({'_id': {'$in': unique_ids}})
        self.dense_vector_storage.delete_data(unique_ids)
        self.sparse_vector_storage.delete_data(unique_ids)
        self.text_storage.delete_data(unique_ids)
        self.sync_lmdb_objects()
    
    def delete_embeddings_by_metadata(self, metadata_filters):
        identifiers = list(self.mongo_reference.find(metadata_filters, {'_id': 1}))
        self.mongo_reference.delete_many(metadata_filters)
        self.dense_vector_storage.delete_data([i['_id'] for i in identifiers])
        self.sparse_vector_storage.delete_data([i['_id'] for i in identifiers])
        self.text_storage.delete_data([i['_id'] for i in identifiers])
        self.sync_lmdb_objects()
    
    def get_vector_by_metadata(self, metadata_filters, get_dense: bool = True):
        try:
            first_result = self.mongo_reference.find_one({**metadata_filters})
            if first_result is None:
                return None
            if get_dense:
                return self.dense_vector_storage.get_vectors([first_result['_id']])[0]
            else:
                return self.sparse_vector_storage.get_sparse_vectors([first_result['_id']])[0]
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
        return None

    def search_faiss(self, query_embeddings, corpus_embeddings, top_k):
        # Cosine similarity requires L2 normalization
        faiss.normalize_L2(corpus_embeddings)
        faiss.normalize_L2(query_embeddings)
        
        # Use IndexFlatIP for Inner Product, which equals cosine similarity after L2 normalization
        index = faiss.IndexFlatIP(corpus_embeddings.shape[1])
    
        index.add(corpus_embeddings)
    
        # distances here are actually similarities (dot products)
        similarities, indices = index.search(query_embeddings, top_k)
    
        results = []
        
        # Zip the indices and similarities together
        for idx, dist in zip(indices[0], similarities[0]):
            if idx == -1:
                continue
    
            results.append({
                "corpus_id": idx,
                "score": dist # Score is the similarity (higher is better)
            })
            
        return results

    def find_most_similar(self, sparse_embedding, dense_embedding, filters={}, output_fields=[], k=5, use_find_one=False, k_rrf=500):
        """
        Finds the most similar documents using Reciprocal Rank Fusion (RRF) between dense and sparse embeddings.

        Args:
            sparse_embedding: The sparse query embedding (torch sparse tensor).
            dense_embedding: The dense query embedding (numpy array or compatible).
            filters: MongoDB filters to restrict the document search.
            output_fields: Fields to return from MongoDB.
            k: Number of top results to return.
            use_find_one: If True, fetch only one MongoDB document matching the filters.
            k_rrf: The RRF constant added to each rank to dampen the impact of lower-ranked items. 
                A higher k_rrf reduces the influence of rank differences, making fusion scores less sensitive
                to exact ranks. Good results have been observed between 50 and 500.

        Returns:
            Tuple containing:
                - List of document IDs (ordered by fused score).
                - List of fused scores.
                - List of metadata dictionaries with retrieved texts and fields.
        """
        try:
            results = self._fetch_mongo_documents(filters, output_fields, use_find_one)
            if not results:
                return [], [], []

            vector_ids, sparse_vectors, dense_vectors, sparse_query_embedding, dense_query_embedding = self._prepare_embeddings(
                results, sparse_embedding, dense_embedding)
            
            if not vector_ids:
                return [], [], []

            # Dense similarity
            dense_semantic_results = self.search_faiss(
                query_embeddings=dense_query_embedding,
                corpus_embeddings=dense_vectors,
                top_k=k * 5
            )
            dense_scores = {vector_ids[r['corpus_id']]: r['score'] for r in dense_semantic_results}

            # Sparse similarity (dot product)
            sparse_scores = {}
            for i, sv in enumerate(sparse_vectors):
                if sv is not None:
                    score = sparse_query_embedding.dot(sv.T).data
                    if len(score) > 0:
                        sparse_scores[vector_ids[i]] = score[0]

            # Reciprocal Rank Fusion (RRF)
            fusion_scores = {}
            dense_ranks = {uid: rank+1 for rank, uid in enumerate(sorted(dense_scores, key=dense_scores.get, reverse=True))}
            sparse_ranks = {uid: rank+1 for rank, uid in enumerate(sorted(sparse_scores, key=sparse_scores.get, reverse=True))}
            
            for uid in set(dense_scores.keys()).union(sparse_scores.keys()):
                score = 0
                if uid in dense_ranks:
                    score += 1 / (k_rrf + dense_ranks[uid])
                if uid in sparse_ranks:
                    score += 1 / (k_rrf + sparse_ranks[uid])
                fusion_scores[uid] = score

            # Top k
            sorted_uids = sorted(fusion_scores.items(), key=lambda x: x[1], reverse=True)[:k]
            db_ids = [uid for uid, _ in sorted_uids]
            scores = [score for _, score in sorted_uids]

            return self._prepare_final_results(db_ids, scores, results)

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            return [], [], []

    def find_most_similar_in_batches(self, sparse_embedding, dense_embedding, filters={}, output_fields=[], k=5, use_find_one=False, k_rrf=20, max_ram_usage_gb=2):
        """
        Finds the most similar documents using RRF in batches to manage memory.
        This function is updated to support both sparse and dense embeddings.
        """
        try:
            if use_find_one:
                return self.find_most_similar(sparse_embedding, dense_embedding, filters, output_fields, k, use_find_one=True, k_rrf=k_rrf)

            total_count = self.mongo_reference.count_documents(filters) if filters else self.mongo_reference.estimated_document_count()

            if total_count == 0:
                return [], [], []

            # Ensure dense embedding is a numpy array for shape and dtype inference
            dense_query_embedding_fixed_typing = self.ensure_embeddings_typing(dense_embedding)
            dense_vector_dim = dense_query_embedding_fixed_typing.shape[0]
           
            # Estimate memory usage, now including sparse vectors
            # A csc_matrix has 'data', 'indices' (int32), and 'indptr' (int32) arrays.
            # Assuming an average of 128 non-zero elements for a sparse vector.
            # data: 128 * float32 (4 bytes)
            # indices: 128 * int32 (4 bytes)
            # indptr: (30552 + 1) * int32 (4 bytes)
            avg_sparse_vector_size_bytes = (128 * 4) + (128 * 4) + ((30552 + 1) * 4)
            avg_dense_vector_size_bytes = dense_vector_dim * 4  # float32
            avg_doc_size_bytes = 50 * 1024 # Assuming 50KB for MongoDB doc
           
            max_ram_usage_bytes = max_ram_usage_gb * (1024 ** 3)
            avg_doc_and_vectors_size_bytes = avg_doc_size_bytes + avg_dense_vector_size_bytes + avg_sparse_vector_size_bytes
           
            batch_size = math.floor(max_ram_usage_bytes / avg_doc_and_vectors_size_bytes)
            batch_size = max(1, min(batch_size, 500000)) # Ensure batch_size is at least 1 and capped

            total_memory_usage_gb = (total_count * avg_doc_and_vectors_size_bytes) / (1024 ** 3)

            if total_memory_usage_gb > max_ram_usage_gb:
                # --- BATCH PROCESSING WITH RRF ---
                all_dense_scores = {}
                all_sparse_scores = {}

                for i in range(0, total_count, batch_size):
                    skip = i
                    limit = batch_size
                   
                    # Fetch batch of documents (only IDs needed for now)
                    batch_mongo_ids_only = self._fetch_mongo_documents(filters, ['_id'], use_find_one=False, limit=limit, skip=skip)
                    if not batch_mongo_ids_only:
                        continue

                    # Prepare embeddings for the current batch
                    vector_ids, sparse_vectors, dense_vectors, sparse_query_embedding, dense_query_embedding = self._prepare_embeddings(
                        batch_mongo_ids_only, sparse_embedding, dense_embedding
                    )
                    if not vector_ids:
                        continue
                   
                    # 1. Calculate dense scores for the batch
                    dense_semantic_results = self.search_faiss(
                        query_embeddings=dense_query_embedding,
                        corpus_embeddings=dense_vectors,
                        top_k=len(vector_ids) # Get scores for all in batch
                    )
                    for r in dense_semantic_results:
                        all_dense_scores[vector_ids[r['corpus_id']]] = r['score']

                    # 2. Calculate sparse scores for the batch
                    for j, sv in enumerate(sparse_vectors):
                        if sv is not None:
                            score = sparse_query_embedding.dot(sv.T).data
                            if len(score) > 0:
                                all_sparse_scores[vector_ids[j]] = score[0]

                # --- FUSE RESULTS AFTER ALL BATCHES ---
                fusion_scores = {}
                dense_ranks = {uid: rank + 1 for rank, uid in enumerate(sorted(all_dense_scores, key=all_dense_scores.get, reverse=True))}
                sparse_ranks = {uid: rank + 1 for rank, uid in enumerate(sorted(all_sparse_scores, key=all_sparse_scores.get, reverse=True))}

                for uid in set(all_dense_scores.keys()).union(all_sparse_scores.keys()):
                    score = 0
                    if uid in dense_ranks:
                        score += 1 / (k_rrf + dense_ranks[uid])
                    if uid in sparse_ranks:
                        score += 1 / (k_rrf + sparse_ranks[uid])
                    fusion_scores[uid] = score
               
                # Get top K results from fused scores
                sorted_uids = sorted(fusion_scores.items(), key=lambda x: x[1], reverse=True)[:k]
                final_db_ids = [uid for uid, _ in sorted_uids]
                final_scores = [score for _, score in sorted_uids]

                # Fetch full metadata only for the final top K results
                final_mongo_results = self._fetch_mongo_documents(
                    {'_id': {'$in': final_db_ids}}, 
                    output_fields, 
                    use_find_one=False, 
                    enforce_order_ids=final_db_ids
                )
               
                return self._prepare_final_results(final_db_ids, final_scores, final_mongo_results)

            else:
                # If total memory is within limits, perform search without batching
                return self.find_most_similar(sparse_embedding, dense_embedding, filters, output_fields, k, use_find_one=False, k_rrf=k_rrf)

        except Exception as e:
            print(f"An error occurred in find_most_similar_in_batches: {e}")
            traceback.print_exc()
            return [], [], []

    def _fetch_mongo_documents(self, filters, output_fields, use_find_one, limit=None, skip=None, enforce_order_ids=None):
        """
        Handle MongoDB document retrieval.
        If enforce_order_ids is provided, results are returned ordered as per enforce_order_ids.
        """
        projection = {'_id': 1}
        if output_fields != 'all':
            for field in output_fields:
                if field != '_id':
                    projection[field] = 1

        if use_find_one:
            doc = self.mongo_reference.find_one(filters, projection)
            return [doc] if doc else []

        cursor = self.mongo_reference.find(filters, projection)
        if limit is not None:
            cursor = cursor.limit(limit)
        if skip is not None:
            cursor = cursor.skip(skip)
        result = list(cursor)

        if enforce_order_ids:
            # Map results by _id
            id_map = {doc['_id']: doc for doc in result if '_id' in doc}
            # Reconstruct ordered list
            ordered_result = [id_map.get(_id) for _id in enforce_order_ids]
            return ordered_result

        return result

    def _prepare_embeddings(self, results, sparse_query_embedding, dense_query_embedding):
        """
        Prepare embeddings for similarity search.
        Refined filtering for None vectors to ensure vector_ids and retrieved_vectors remain perfectly aligned.
        """
        # Extract _ids from the MongoDB results (which might only contain _id at this stage)
        mongo_ids = [r['_id'] for r in results if '_id' in r]
        
        retrieved_dense_vectors_raw = self.dense_vector_storage.get_vectors(mongo_ids)
        retrieved_sparse_vectors_raw = self.sparse_vector_storage.get_sparse_vectors(mongo_ids)
        
        vector_ids = []
        retrieved_vectors = []

        # Filter out None values and keep corresponding IDs aligned
        for i, vector in enumerate(retrieved_dense_vectors_raw):
            if vector is not None:
                vector_ids.append(mongo_ids[i])
                retrieved_vectors.append(vector)
        
        if not vector_ids:
            return [], [], [] # Return empty if no valid vectors

        lmdb_dense_vectors = np.array(retrieved_vectors, dtype=np.float32)
        
        # Wrap the dense query embedding in a list before casting to np.array only if it's dimension is 1
        dense_query_embedding = np.array([dense_query_embedding], dtype=np.float32) if len(dense_query_embedding.shape) == 1 else dense_query_embedding
        sparse_query_embedding = self.convert_sparse_tensor_to_sparse_matrix(sparse_query_embedding)
        
        return vector_ids, retrieved_sparse_vectors_raw, lmdb_dense_vectors, sparse_query_embedding, dense_query_embedding

    def _prepare_final_results(self, db_ids, scores, mongo_results):
        """
        Prepare the final results with texts and metadata.
        Refined _prepare_final_results: Explicitly handles cases where text_storage.get_data might return None
        for a given ID, ensuring 'text' field is always a string.
        """
        texts_raw = self.text_storage.get_data(db_ids)
        
        # Create a mapping from _id to the full MongoDB document for efficient lookup
        id_mapped_results = {r['_id']: r for r in mongo_results if '_id' in r}
        
        metadatas = []
        for i, db_id in enumerate(db_ids):
            metadata = id_mapped_results.get(db_id, {})
            
            # Ensure _id is always present in metadata
            if '_id' not in metadata:
                metadata['_id'] = db_id
            
            # Ensure 'text' field is always a string, handling None from text_storage
            text = texts_raw[i] if texts_raw and i < len(texts_raw) and texts_raw[i] is not None else ''
            metadata['text'] = text
            metadatas.append(metadata)

        return db_ids, scores, metadatas

class DuckVectorDB:
    def __init__(self, db_file: str, vector_storage: ShardedLmdbStorage, text_storage: ShardedLmdbStorage):
        self.db_file = db_file
        self.vector_storage = vector_storage
        self.text_storage = text_storage
        self._local = threading.local()
        self._init_schema()

    def close(self):
        """Close the DuckDB connection owned by the calling thread."""
        if hasattr(self._local, 'db') and self._local.db is not None:
            try:
                self._local.db.close()
            finally:
                self._local.db = None

    def _init_schema(self):
        """Initialize database schema once"""
        with duckdb.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    _id VARCHAR PRIMARY KEY,
                    metadata_json JSON
                );
            """)
    
    def _get_connection(self):
        """Get a thread-local connection"""
        if not hasattr(self._local, 'db') or self._local.db is None:
            self._local.db = duckdb.connect(self.db_file, config={
                "access_mode": "READ_WRITE",
                "checkpoint_threshold": "1GB",
                "wal_autocheckpoint": "1GB",
                "threads": max(1, (os.cpu_count() or 1) // 2)
            })
        return self._local.db
    
    def sync_lmdb_objects(self):
        self.vector_storage.sync()
        self.text_storage.sync()

    def check_counts(self):
        conn = self._get_connection()
        metadata_count = conn.execute("SELECT COUNT(*) FROM metadata").fetchone()[0]
        print(f"Semantic storage count: {self.vector_storage.get_data_count()}")
        print(f"Text storage count: {self.text_storage.get_data_count()}")
        print(f"DuckDB metadata count: {metadata_count}")

    def get_total_count(self):
        return self.text_storage.get_data_count()

    def ensure_embeddings_typing(self, embeddings):
        if type(embeddings) is not np.ndarray:
            embeddings = np.array(embeddings, dtype=np.float32)
        return embeddings

    def store_embeddings_batch(self, unique_ids: list, embeddings, metadata_dicts=[], text_field=None):
        metadata_dicts_copy = copy.deepcopy(metadata_dicts)
        embeddings = self.ensure_embeddings_typing(embeddings)

        if len(metadata_dicts_copy) < len(unique_ids):
            metadata_dicts_copy.extend([{} for _ in range(len(unique_ids) - len(metadata_dicts_copy))])

        # Add a marker field to empty dictionaries
        for metadata_dict in metadata_dicts_copy:
            if not metadata_dict:
                metadata_dict['_empty'] = True

        if text_field is not None:
            texts = [m.pop(text_field, '') for m in metadata_dicts_copy]
        else:
            texts = ['' for _ in range(len(unique_ids))]

        conn = self._get_connection()
        try:
            values_clause = []
            params = []
            for uid, metadata_dict in zip(unique_ids, metadata_dicts_copy):
                values_clause.append("(?, ?)")
                params.extend([uid, json.dumps(metadata_dict)])

            sql = f"""INSERT INTO metadata (_id, metadata_json) VALUES {', '.join(values_clause)} 
                     ON CONFLICT (_id) DO UPDATE SET metadata_json = EXCLUDED.metadata_json"""
            conn.execute(sql, params)
        except Exception as e:
            print(f"Database error: {e}")
            raise

        self.vector_storage.store_vectors(embeddings, unique_ids)
        self.text_storage.store_data(texts, unique_ids)

        self.sync_lmdb_objects()
        del metadata_dicts_copy

    def delete_embeddings_batch(self, unique_ids):
        conn = self._get_connection()
        conn.execute(f"DELETE FROM metadata WHERE _id IN ({','.join(['?']*len(unique_ids))})", unique_ids)
        self.vector_storage.delete_data(unique_ids)
        self.text_storage.delete_data(unique_ids)
        self.sync_lmdb_objects()

    def delete_embeddings_by_metadata(self, metadata_filters):
        where_clause, params = self._build_where_clause(metadata_filters)

        conn = self._get_connection()
        # First, select the _ids to be deleted
        query = f"SELECT _id FROM metadata WHERE {where_clause}"
        identifiers = [row[0] for row in conn.execute(query, params).fetchall()]

        # Then, delete the metadata
        if identifiers:
            conn.execute(f"DELETE FROM metadata WHERE _id IN ({','.join(['?']*len(identifiers))})", identifiers)

        # Delete from vector and text storage
        self.vector_storage.delete_data(identifiers)
        self.text_storage.delete_data(identifiers)
        self.sync_lmdb_objects()

    def get_vector_by_metadata(self, metadata_filters):
        try:
            where_clause, params = self._build_where_clause(metadata_filters)
            query = f"SELECT _id FROM metadata WHERE {where_clause} LIMIT 1"

            conn = self._get_connection()
            result = conn.execute(query, params).fetchone()

            if result is None:
                return None

            return self.vector_storage.get_vectors([result[0]])[0]
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
        return None

    def search_faiss(self, query_embeddings, corpus_embeddings, top_k):
        faiss.normalize_L2(corpus_embeddings)
        faiss.normalize_L2(query_embeddings)
        index = faiss.IndexFlatIP(corpus_embeddings.shape[1])
        index.add(corpus_embeddings)
        similarities, indices = index.search(query_embeddings, top_k)
        results = []
        for idx, dist in zip(indices[0], similarities[0]):
            if idx == -1:
                continue
            results.append({"corpus_id": idx, "score": dist})
        return results

    def find_most_similar(self, embedding, filters={}, output_fields=[], k=5, use_find_one=False):
        """
        Main entry point to find the most similar documents based on the given embedding.
        """
        try:
            # Step 1: Get documents from DuckDB
            results = self._fetch_duckdb_documents(filters, output_fields, use_find_one)
            if not results:
                return [], [], []

            # Step 2: Prepare embeddings
            vector_ids, vectors, query_embedding, = self._prepare_embeddings(results, embedding)

            if not vector_ids:
                return [], [], []

            # Create a vector_id to index mapping
            index_to_vector_id = { idx: id for idx, id in enumerate(vector_ids) }
            # Step 3: Perform similarity search
            semantic_results = self.search_faiss(
                query_embeddings = query_embedding,
                corpus_embeddings = vectors,
                top_k = k
            )
            ids = [ r['corpus_id'] for r in semantic_results if r['corpus_id'] != -1 ]
            scores =  [ r['score'] for r in semantic_results if r['corpus_id'] != -1 ]
            translated_ids = [ index_to_vector_id[id] for id in ids ]

            db_ids = translated_ids
            scores = scores

            # Iterate db_ids and scores together. If a duplicate db_id is found, remove it and its score
            seen_ids = set()

            # Iterate from inverse order to prevent errors on removal during iteration
            for i in range(len(db_ids) - 1, -1, -1):
                if db_ids[i] in seen_ids:
                    db_ids.pop(i)
                    scores.pop(i)
                else:
                    seen_ids.add(db_ids[i])

            # Step 4: Prepare final results
            return self._prepare_final_results(db_ids, scores, results)

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            return [], [], []

    def find_most_similar_in_batches(self, embedding, filters={}, output_fields=[], k=5, use_find_one=False, max_ram_usage_gb=2):
        """
        Main entry point to find the most similar documents based on the given embedding.
        This function performs the search in batches if the estimated memory usage exceeds the specified limit.
        """
        try:
            if use_find_one:
                return self.find_most_similar(embedding, filters, output_fields, k, use_find_one=True)

            conn = self._get_connection()
            total_count_query = f"SELECT COUNT(*) FROM metadata WHERE {self._build_where_clause(filters)[0]}"
            total_count = conn.execute(total_count_query, self._build_where_clause(filters)[1]).fetchone()[0]

            if total_count == 0:
                return [], [], []

            query_embedding_fixed_typing = self.ensure_embeddings_typing(embedding)
            vector_dim = query_embedding_fixed_typing.shape[0]

            max_ram_usage_bytes = max_ram_usage_gb * (1024 ** 3)
            avg_doc_and_vector_size_bytes = (5 * 1024) + (vector_dim * 4)

            batch_size = math.floor(max_ram_usage_bytes / avg_doc_and_vector_size_bytes)
            if batch_size < 1:
                batch_size = 1
            if batch_size > 500000:
                batch_size = 500000

            total_memory_usage_gb = (total_count * avg_doc_and_vector_size_bytes) / (1024 ** 3)
            top_k_results_heap = []

            if total_memory_usage_gb > max_ram_usage_gb:
                for i in range(0, total_count, batch_size):
                    skip = i
                    limit = batch_size

                    batch_duckdb_ids_only = self._fetch_duckdb_documents(filters, ['_id'], use_find_one=False, limit=limit, skip=skip)

                    if not batch_duckdb_ids_only:
                        continue

                    vector_ids, vectors, query_embedding = self._prepare_embeddings(batch_duckdb_ids_only, embedding)

                    if not vector_ids:
                        continue

                    faiss_index_to_duckdb_id = {idx: mongo_id for idx, mongo_id in enumerate(vector_ids)}

                    semantic_results = self.search_faiss(
                        query_embeddings=query_embedding,
                        corpus_embeddings=vectors,
                        top_k=k
                    )

                    for r in semantic_results:
                        if r['corpus_id'] != -1:
                            duckdb_id = faiss_index_to_duckdb_id[r['corpus_id']]
                            score = r['score']

                            if len(top_k_results_heap) < k:
                                heapq.heappush(top_k_results_heap, (score, duckdb_id))
                            else:
                                if score > top_k_results_heap[0][0]:
                                    heapq.heapreplace(top_k_results_heap, (score, duckdb_id))

                final_sorted_results = sorted(top_k_results_heap, key=lambda x: x[0], reverse=True)
                final_db_ids = [db_id for _, db_id in final_sorted_results]
                final_scores = [score for score, _ in final_sorted_results]

                final_duckdb_results = self._fetch_duckdb_documents({'_id': {'$in': final_db_ids}}, output_fields, use_find_one=False, enforce_order_ids=final_db_ids)

                return self._prepare_final_results(final_db_ids, final_scores, final_duckdb_results)

            else:
                return self.find_most_similar(embedding, filters, output_fields, k, use_find_one=False)

        except Exception as e:
            print(f"An error occurred in find_most_similar_in_batches: {e}")
            traceback.print_exc()
            return [], [], []

    def _fetch_duckdb_documents(self, filters, output_fields, use_find_one, limit=None, skip=None, enforce_order_ids=None):
        """
        Handle DuckDB document retrieval.
        If enforce_order_ids is provided, results are returned ordered as per enforce_order_ids.
        """
        where_clause, params = self._build_where_clause(filters)

        # Base query
        query = f"SELECT _id, metadata_json FROM metadata WHERE {where_clause}"

        if use_find_one:
            query += " LIMIT 1"
        else:
            if limit is not None:
                query += f" LIMIT {limit}"
            if skip is not None:
                query += f" OFFSET {skip}"

        conn = self._get_connection()
        results = conn.execute(query, params).fetchall()

        # Process results
        processed_results = []
        for row in results:
            doc = {"_id": row[0]}
            metadata = json.loads(row[1])
            if output_fields == 'all':
                doc.update(metadata)
            else:
                for field in output_fields:
                    if field in metadata:
                        doc[field] = metadata[field]
            processed_results.append(doc)

        if enforce_order_ids:
            id_map = {doc['_id']: doc for doc in processed_results}
            ordered_result = [id_map.get(_id) for _id in enforce_order_ids]
            return ordered_result

        return processed_results

    def _prepare_embeddings(self, results, query_embedding):
        """
        Prepare embeddings for similarity search.
        Refined filtering for None vectors to ensure vector_ids and retrieved_vectors remain perfectly aligned.
        """
        # Extract _ids from the DuckDB results
        duckdb_ids = [r['_id'] for r in results if '_id' in r]

        retrieved_vectors_raw = self.vector_storage.get_vectors(duckdb_ids)

        vector_ids = []
        retrieved_vectors = []

        # Filter out None values and keep corresponding IDs aligned
        for i, vector in enumerate(retrieved_vectors_raw):
            if vector is not None:
                vector_ids.append(duckdb_ids[i])
                retrieved_vectors.append(vector)

        if not vector_ids:
            return [], [], [] # Return empty if no valid vectors

        lmdb_vectors = np.array(retrieved_vectors, dtype=np.float32)
        query_embedding = np.array([query_embedding], dtype=np.float32)

        return vector_ids, lmdb_vectors, query_embedding

    def _escape_json_key(self, key):
        return key.replace("'", "''")

    def _build_where_clause(self, filters):
        if not filters:
            return "1=1", []

        conditions = []
        params = []

        for key, value in filters.items():
            # Fixed JSON extraction syntax for DuckDB
            if isinstance(value, dict) and "$in" in value:
                placeholders = ','.join(['?'] * len(value['$in']))
                conditions.append(f"metadata_json->>'{key}' IN ({placeholders})")
                params.extend(value['$in'])
            else:
                conditions.append(f"metadata_json->>'{key}' = ?")
                params.append(str(value))  # Ensure string conversion

        return " AND ".join(conditions), params

    def _prepare_final_results(self, db_ids, scores, duckdb_results):
        """
        Prepare the final results with texts and metadata.
        """
        texts_raw = self.text_storage.get_data(db_ids)

        # Create a mapping from _id to the full DuckDB document for efficient lookup
        id_mapped_results = {r['_id']: r for r in duckdb_results if '_id' in r}

        metadatas = []
        for i, db_id in enumerate(db_ids):
            metadata = id_mapped_results.get(db_id, {})

            # Ensure _id is always present in metadata
            if '_id' not in metadata:
                metadata['_id'] = db_id

            # Ensure 'text' field is always a string, handling None from text_storage
            text = texts_raw[i] if texts_raw and i < len(texts_raw) and texts_raw[i] is not None else ''
            metadata['text'] = text
            metadatas.append(metadata)

        return db_ids, scores, metadatas
