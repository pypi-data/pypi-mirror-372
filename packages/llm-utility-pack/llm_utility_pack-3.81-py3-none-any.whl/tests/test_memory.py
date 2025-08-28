import unittest
from unittest.mock import MagicMock, patch

from utility_pack.memory import Memory


class TestMemory(unittest.TestCase):
    @patch("utility_pack.memory.pymongo")
    @patch("utility_pack.memory.VectorDB")
    @patch("utility_pack.memory.LmdbStorage")
    def setUp(self, mock_lmdb, mock_vectordb, mock_pymongo):
        self.mock_vectordb = mock_vectordb.return_value
        self.mock_conversation_collection = MagicMock()
        mock_pymongo.MongoClient.return_value.__getitem__.return_value.__getitem__.return_value = (
            self.mock_conversation_collection
        )

        self.memory = Memory(
            mongo_uri="mongodb://localhost:27017/",
            mongo_database="test_db",
            mongo_collection_vectordb="test_vectordb",
            mongo_collection_conversation_data="test_conversation",
        )

    @patch("utility_pack.memory.extract_embeddings")
    def test_store_embeddings(self, mock_extract_embeddings):
        mock_extract_embeddings.return_value = [0.1, 0.2]
        self.memory.store_embeddings(["sentence"], "session_id", "message_id", "type")
        self.mock_vectordb.store_embeddings_batch.assert_called_once()

    @patch("utility_pack.memory.compress_text", return_value="summary")
    @patch("utility_pack.memory.Memory.store_embeddings")
    def test_memorize(self, mock_store_embeddings, mock_compress_text):
        session_id, question_id, answer_id = self.memory.memorize("question", "answer")
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(question_id)
        self.assertIsNotNone(answer_id)
        self.assertEqual(self.mock_conversation_collection.insert_one.call_count, 2)
        self.assertEqual(mock_store_embeddings.call_count, 2)

    def test_get_last_interactions(self):
        self.mock_conversation_collection.find.return_value = [
            {"message_id": "1"},
            {"message_id": "2"},
        ]
        chats = self.memory.get_last_interactions("session_id")
        self.assertEqual(len(chats), 2)

    @patch("utility_pack.memory.extract_embeddings")
    @patch("utility_pack.memory.rerank")
    def test_remember(self, mock_rerank, mock_extract_embeddings):
        self.mock_conversation_collection.find.return_value = []
        self.mock_vectordb.find_most_similar.return_value = (
            None,
            None,
            [{"text": "retrieved", "message_id": "3", "type": "question"}],
        )
        mock_rerank.return_value = [("retrieved", 0.9)]

        result = self.memory.remember("session_id", "new_prompt")
        self.assertIn("suggested_context", result)

    def test_delete_session_from_vector_db(self):
        self.memory.delete_session_from_vector_db("session_id")
        self.mock_vectordb.delete_embeddings_by_metadata.assert_called_with(
            {"session_id": "session_id"}
        )

    def test_delete_message_from_vector_db(self):
        self.memory.delete_message_from_vector_db("session_id", "message_id")
        self.mock_vectordb.delete_embeddings_by_metadata.assert_called_with(
            {"session_id": "session_id", "message_id": "message_id"}
        )

    @patch("utility_pack.memory.Memory.delete_session_from_vector_db")
    def test_forget_session(self, mock_delete):
        self.memory.forget_session("session_id")
        self.mock_conversation_collection.delete_many.assert_called_with(
            {"session_id": "session_id"}
        )
        mock_delete.assert_called_with("session_id")

    @patch("utility_pack.memory.Memory.delete_message_from_vector_db")
    def test_forget_message(self, mock_delete):
        self.memory.forget_message("session_id", "message_id")
        self.mock_conversation_collection.delete_one.assert_called_with(
            {"session_id": "session_id", "message_id": "message_id"}
        )
        mock_delete.assert_called_with("session_id", "message_id")

    def test_list_messages(self):
        self.mock_conversation_collection.count_documents.return_value = 1
        self.mock_conversation_collection.find.return_value = [{"message_id": "1"}]

        count = self.memory.list_messages("session_id", count=True)
        self.assertEqual(count, 1)

        messages = self.memory.list_messages("session_id")
        self.assertEqual(len(messages), 1)


if __name__ == "__main__":
    unittest.main()
