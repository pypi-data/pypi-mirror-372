import unittest
import numpy as np
import os
import shutil
import pymongo
import inspect
from utility_pack.vector_storage import VectorDB
from utility_pack.vector_storage_helper import ShardedLmdbStorage

# --- Test Configuration ---
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DATABASE = "test_vector_db"
VECTOR_DIMENSION = 1536

class TestVectorDBModes(unittest.TestCase):
    """
    Test suite for VectorDB, covering all quantization modes:
    - None (no quantization)
    - '8bit'
    - '1bit'
    """
    storage_paths_to_clean = set()
    client = None # Class-level MongoClient

    @classmethod
    def setUpClass(cls):
        """
        Create a single MongoClient instance to be shared across all tests.
        This is more efficient and helps manage resources properly.
        """
        cls.client = pymongo.MongoClient(MONGO_URI)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up all created resources once after all tests are done.
        This is the only place where rmtree and DB dropping is called.
        """
        # 1. Drop the entire test database to ensure a clean state.
        if cls.client:
            cls.client.drop_database(MONGO_DATABASE)
            cls.client.close()

        # 2. Clean up all storage directories.
        for path in cls.storage_paths_to_clean:
            if os.path.exists(path):
                shutil.rmtree(path)

    def setUp(self):
        """Clean up MongoDB collection before each test variation using the shared client."""
        # Use the class-level client to clear the collection.
        self.client[MONGO_DATABASE].get_collection("test_collection").delete_many({})

    def _run_test_for_modes(self, test_func):
        """
        Helper to run a test function for all quantization modes, ensuring
        complete isolation by using unique storage paths for each run.
        """
        test_name = inspect.stack()[1][3]
        modes = [None, '8bit', '1bit']

        for mode in modes:
            with self.subTest(mode=str(mode)):
                self.setUp()
                
                mode_str = str(mode) if mode is not None else 'none'
                vector_storage_path = f"test_storage_{test_name}_{mode_str}_vectors"
                text_storage_path = f"test_storage_{test_name}_{mode_str}_text"

                self.__class__.storage_paths_to_clean.add(vector_storage_path)
                self.__class__.storage_paths_to_clean.add(text_storage_path)

                if os.path.exists(vector_storage_path):
                    shutil.rmtree(vector_storage_path)
                if os.path.exists(text_storage_path):
                    shutil.rmtree(text_storage_path)
                
                vector_storage = ShardedLmdbStorage(vector_storage_path)
                text_storage = ShardedLmdbStorage(text_storage_path)
                
                # NOTE: The ResourceWarning originates from the VectorDB class itself,
                # which likely creates its own MongoClient instance without providing a
                # method to close it. The proper fix would be to modify VectorDB to
                # either accept an external client or have a .close() method.
                # The changes in this test file fix the resource management for the
                # test suite itself.
                db = VectorDB(
                    mongo_uri=MONGO_URI,
                    mongo_database=MONGO_DATABASE,
                    mongo_collection="test_collection",
                    vector_storage=vector_storage,
                    text_storage=text_storage,
                    vector_dimension=VECTOR_DIMENSION,
                    quantization_mode=mode
                )
                
                test_func(db)
                
                db.mongo_connection.close()
                vector_storage.close()
                text_storage.close()

    def test_store_and_search(self):
        """Tests storing embeddings and finding the most similar one."""
        def test_logic(db):
            unique_ids = [f"vec{i}" for i in range(10)]
            embeddings = np.random.rand(10, VECTOR_DIMENSION).astype(np.float32)
            embeddings[5] = np.ones(VECTOR_DIMENSION, dtype=np.float32)
            metadata_dicts = [{"doc_id": i, "author": f"author{i % 2}"} for i in range(10)]
            
            db.store_embeddings_batch(unique_ids, embeddings, metadata_dicts, text_field="text")
            
            self.assertEqual(db.get_total_count(), 10)

            query_embedding = np.ones(VECTOR_DIMENSION, dtype=np.float32) + 0.01
            ids, scores, metadatas = db.find_most_similar(query_embedding, k=1, output_fields=['doc_id'])

            self.assertEqual(len(ids), 1)
            self.assertEqual(ids[0], "vec5")
            self.assertGreater(scores[0], 0.95)
            self.assertEqual(metadatas[0]['doc_id'], 5)

        self._run_test_for_modes(test_logic)

    def test_delete_by_metadata(self):
        """Tests deleting embeddings based on metadata filters."""
        def test_logic(db):
            unique_ids = [f"vec{i}" for i in range(10)]
            embeddings = np.random.rand(10, VECTOR_DIMENSION).astype(np.float32)
            metadata_dicts = [{"author": f"author{i % 2}"} for i in range(10)]
            
            db.store_embeddings_batch(unique_ids, embeddings, metadata_dicts)
            self.assertEqual(db.get_total_count(), 10)

            db.delete_embeddings_by_metadata({"author": "author1"})
            
            self.assertEqual(db.get_total_count(), 5)
            
            retrieved_vector = db.get_vector_by_metadata({"author": "author1"})
            self.assertIsNone(retrieved_vector)

        self._run_test_for_modes(test_logic)

    def test_delete_batch(self):
        """Tests deleting a specific batch of embeddings by their IDs."""
        def test_logic(db):
            unique_ids = [f"vec{i}" for i in range(10)]
            embeddings = np.random.rand(10, VECTOR_DIMENSION).astype(np.float32)
            metadata_dicts = [{"doc_id": i} for i in range(10)]
            
            db.store_embeddings_batch(unique_ids, embeddings, metadata_dicts)
            self.assertEqual(db.get_total_count(), 10)

            ids_to_delete = ["vec1", "vec4", "vec8"]
            db.delete_embeddings_batch(ids_to_delete)
            
            self.assertEqual(db.get_total_count(), 7)
            
            retrieved_vector = db.get_vector_by_metadata({"doc_id": 4})
            self.assertIsNone(retrieved_vector)

        self._run_test_for_modes(test_logic)

    def test_batched_search(self):
        """Tests the find_most_similar_in_batches method."""
        def test_logic(db):
            num_embeddings = 50
            unique_ids = [f"vec{i}" for i in range(num_embeddings)]
            embeddings = np.random.rand(num_embeddings, VECTOR_DIMENSION).astype(np.float32)
            embeddings[30] = np.full(VECTOR_DIMENSION, 0.9, dtype=np.float32)
            metadata_dicts = [{"doc_id": i} for i in range(num_embeddings)]

            db.store_embeddings_batch(unique_ids, embeddings, metadata_dicts)
            self.assertEqual(db.get_total_count(), num_embeddings)

            query_embedding = np.full(VECTOR_DIMENSION, 0.9, dtype=np.float32) + 0.01

            ids, scores, metadatas = db.find_most_similar_in_batches(
                query_embedding, k=1, max_ram_usage_gb=0.0001, output_fields=['doc_id']
            )

            self.assertEqual(len(ids), 1)
            self.assertEqual(ids[0], "vec30")
            self.assertGreater(scores[0], 0.95)
            self.assertEqual(metadatas[0]['doc_id'], 30)

        self._run_test_for_modes(test_logic)

if __name__ == '__main__':
    unittest.main()
