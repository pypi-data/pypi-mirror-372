import unittest
import numpy as np
import os
import shutil
from utility_pack.vector_storage import DuckVectorDB
from utility_pack.vector_storage_helper import ShardedLmdbStorage

class TestVectorDB(unittest.TestCase):
    def setUp(self):
        self.db_file = "test.duckdb"
        self.vector_storage_path = "test_vector_storage"
        self.text_storage_path = "test_text_storage"

        # Clean up previous test runs
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        if os.path.exists(self.vector_storage_path):
            shutil.rmtree(self.vector_storage_path)
        if os.path.exists(self.text_storage_path):
            shutil.rmtree(self.text_storage_path)

        self.vector_storage = ShardedLmdbStorage(self.vector_storage_path)
        self.text_storage = ShardedLmdbStorage(self.text_storage_path)
        self.db = DuckVectorDB(self.db_file, self.vector_storage, self.text_storage)

    def tearDown(self):
        self.db.close()
        # Clean up after tests
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        if os.path.exists(self.vector_storage_path):
            shutil.rmtree(self.vector_storage_path)
        if os.path.exists(self.text_storage_path):
            shutil.rmtree(self.text_storage_path)

    def test_a_store_and_get_vector(self):
        unique_ids = ["vec1", "vec2", "vec3"]
        embeddings = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]], dtype=np.float32)
        metadata_dicts = [{"author": "author1"}, {"author": "author2"}, {"author": "author1"}]

        self.db.store_embeddings_batch(unique_ids, embeddings, metadata_dicts)

        retrieved_vector = self.db.get_vector_by_metadata({"author": "author2"})
        self.assertIsNotNone(retrieved_vector)
        np.testing.assert_array_almost_equal(retrieved_vector, embeddings[1])

    def test_b_find_most_similar(self):
        unique_ids = ["vec1", "vec2", "vec3"]
        embeddings = np.array([[0.1, 0.2], [0.8, 0.9], [0.12, 0.22]], dtype=np.float32)
        metadata_dicts = [{"id": 1}, {"id": 2}, {"id": 3}]
        self.db.store_embeddings_batch(unique_ids, embeddings, metadata_dicts)

        query_embedding = np.array([0.81, 0.91], dtype=np.float32)
        ids, scores, metadatas = self.db.find_most_similar(query_embedding, k=1)

        self.assertEqual(len(ids), 1)
        self.assertEqual(ids[0], "vec2")

    def test_c_delete_by_metadata(self):
        unique_ids = ["vec1", "vec2", "vec3"]
        embeddings = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]], dtype=np.float32)
        metadata_dicts = [{"author": "author1"}, {"author": "author2"}, {"author": "author1"}]
        self.db.store_embeddings_batch(unique_ids, embeddings, metadata_dicts)

        self.db.delete_embeddings_by_metadata({"author": "author2"})
        self.assertEqual(self.db.get_total_count(), 2)
        retrieved_vector = self.db.get_vector_by_metadata({"author": "author2"})
        self.assertIsNone(retrieved_vector)

    def test_d_delete_batch(self):
        unique_ids = ["vec1", "vec2", "vec3"]
        embeddings = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]], dtype=np.float32)
        metadata_dicts = [{"author": "author1"}, {"author": "author2"}, {"author": "author1"}]
        self.db.store_embeddings_batch(unique_ids, embeddings, metadata_dicts)

        self.db.delete_embeddings_batch(["vec1", "vec3"])
        self.assertEqual(self.db.get_total_count(), 1)
        retrieved_vector = self.db.get_vector_by_metadata({"author": "author1"})
        self.assertIsNone(retrieved_vector)

if __name__ == '__main__':
    unittest.main()
