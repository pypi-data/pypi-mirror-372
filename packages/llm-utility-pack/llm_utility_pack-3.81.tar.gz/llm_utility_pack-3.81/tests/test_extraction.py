import unittest
from unittest.mock import MagicMock, patch

from utility_pack.extraction import LlmProvider, get_data_from_text, prompt_for_data


class TestExtraction(unittest.TestCase):
    @patch("utility_pack.extraction.openrouter_prompt")
    @patch("utility_pack.extraction.detect_language", return_value="en")
    def test_prompt_for_data_openrouter(self, mock_detect_language, mock_openrouter_prompt):
        mock_openrouter_prompt.return_value = '{"data": "extracted"}'
        result = prompt_for_data("context", "data_name", "data_description", LlmProvider.OPENROUTER, "model")
        self.assertEqual(result, "extracted")

    @patch("utility_pack.extraction.ollama_prompt")
    @patch("utility_pack.extraction.detect_language", return_value="en")
    def test_prompt_for_data_ollama(self, mock_detect_language, mock_ollama_prompt):
        mock_ollama_prompt.return_value = '{"data": "extracted"}'
        result = prompt_for_data("context", "data_name", "data_description", LlmProvider.OLLAMA, "model")
        self.assertEqual(result, "extracted")

    @patch("utility_pack.extraction.vllm_prompt")
    @patch("utility_pack.extraction.detect_language", return_value="en")
    def test_prompt_for_data_vllm(self, mock_detect_language, mock_vllm_prompt):
        mock_vllm_prompt.return_value = '{"data": "extracted"}'
        result = prompt_for_data("context", "data_name", "data_description", LlmProvider.VLLM, "model")
        self.assertEqual(result, "extracted")

    @patch("utility_pack.extraction.openai_prompt")
    @patch("utility_pack.extraction.detect_language", return_value="en")
    def test_prompt_for_data_openai(self, mock_detect_language, mock_openai_prompt):
        mock_openai_prompt.return_value = '{"data": "extracted"}'
        result = prompt_for_data("context", "data_name", "data_description", LlmProvider.OPENAI, "model")
        self.assertEqual(result, "extracted")

    @patch("utility_pack.extraction.count_tokens", return_value=100)
    @patch("utility_pack.extraction.prompt_for_data", return_value="extracted")
    def test_get_data_from_text_short(self, mock_prompt_for_data, mock_count_tokens):
        result = get_data_from_text(
            "full_text", "data_name", "data_description", LlmProvider.OPENAI, "model"
        )
        self.assertEqual(result, "extracted")

    @patch("utility_pack.extraction.count_tokens", return_value=10000)
    @patch("utility_pack.extraction.chunk_text", return_value=["chunk1", "chunk2"])
    @patch("utility_pack.extraction.MiniVectorDB")
    @patch("utility_pack.extraction.extract_embeddings")
    @patch("utility_pack.extraction.find_needle_in_haystack", return_value="found_text")
    @patch("utility_pack.extraction.prompt_for_data", return_value="extracted_rag")
    def test_get_data_from_text_long_rag(
        self,
        mock_prompt_for_data,
        mock_find_needle_in_haystack,
        mock_extract_embeddings,
        mock_minivectordb,
        mock_chunk_text,
        mock_count_tokens,
    ):
        # Mock the behavior of MiniVectorDB's find_most_similar method
        mock_db_instance = mock_minivectordb.return_value
        mock_db_instance.find_most_similar.return_value = (
            None,
            None,
            [{"text": "retrieved_chunk", "index": 0}],
        )

        result = get_data_from_text(
            "full_text", "data_name", "data_description", LlmProvider.OPENAI, "model"
        )

        self.assertEqual(result, "extracted_rag")


if __name__ == "__main__":
    unittest.main()
