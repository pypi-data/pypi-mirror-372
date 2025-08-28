import unittest
from unittest.mock import patch

from utility_pack.embeddings import EmbeddingType, extract_embeddings


class TestEmbeddings(unittest.TestCase):
    def test_extract_embeddings_textual(self):
        texts = ["This is a test sentence.", "This is another test sentence."]
        embeddings = extract_embeddings(texts, embedding_type=EmbeddingType.TEXTUAL)
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(len(embeddings[0]), 512)

    @patch("utility_pack.embeddings._initialize_onnx")
    @patch("utility_pack.embeddings.onnx_model")
    def test_extract_embeddings_semantic(self, mock_onnx_model, mock_initialize_onnx):
        texts = ["This is a test sentence.", "This is another test sentence."]

        # Mock the return value of onnx_model.run(...)[0].tolist()
        mock_onnx_model.run.return_value = [
            unittest.mock.MagicMock(tolist=lambda: [[0.1, 0.2], [0.3, 0.4]])
        ]

        embeddings = extract_embeddings(texts, embedding_type=EmbeddingType.SEMANTIC)

        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(len(embeddings[0]), 2)

    def test_extract_embeddings_invalid_type(self):
        with self.assertRaises(ValueError):
            extract_embeddings(["test"], embedding_type="invalid")


if __name__ == "__main__":
    unittest.main()
