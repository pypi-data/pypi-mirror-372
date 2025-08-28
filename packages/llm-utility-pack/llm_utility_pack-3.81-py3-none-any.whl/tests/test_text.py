import unittest
from unittest.mock import patch

from utility_pack.text import (
    StringSimilarity,
    chunk_text,
    cleanup_markdown,
    compress_text,
    detect_language,
    find_needle_in_haystack,
    get_uuid,
    remove_accents_completely,
    remove_accents_replace,
    remove_asian_characters,
    remove_emails,
    remove_extra_whitespace,
    remove_html_tags,
    remove_numbers,
    remove_special_characters,
    remove_stopwords,
    remove_urls,
    string_similarity,
    string_similarity_from_list,
)


class TestText(unittest.TestCase):
    def test_chunk_text(self):
        text = "This is a long text to be chunked."
        chunks = chunk_text(text, chunk_token_count=5)
        self.assertIsInstance(chunks, list)
        self.assertTrue(len(chunks) > 1)

    @patch("utility_pack.text.compress_text_semantic", return_value="compressed text")
    def test_compress_text(self, mock_compress):
        text = "This is a long text to be compressed."
        compressed = compress_text(text)
        self.assertEqual(compressed, "compressed text")

    def test_detect_language(self):
        self.assertEqual(detect_language("Hello, world!"), "en")
        self.assertEqual(detect_language("Olá, mundo!"), "pt")

    @patch("utility_pack.text.initialize_reranker")
    @patch("utility_pack.text.textual_reranker")
    @patch("utility_pack.text.semantic_reranker")
    def test_find_needle_in_haystack(
        self, mock_semantic_reranker, mock_textual_reranker, mock_init
    ):
        mock_textual_reranker.rerank_documents.return_value = [("This is a test.", 0.9)]
        mock_semantic_reranker.rerank_documents.return_value = [
            ("Another sentence.", 0.8)
        ]
        haystack = ["This is a test.", "Another sentence."]
        needle = "test"
        result = find_needle_in_haystack(needle, haystack)
        self.assertEqual(result, ["This is a test."])

    def test_get_uuid(self):
        self.assertIsInstance(get_uuid(), str)

    def test_remove_stopwords(self):
        self.assertEqual(remove_stopwords("this is a test", "en"), "test")

    def test_remove_accents_replace(self):
        self.assertEqual(remove_accents_replace("áéíóú"), "aeiou")

    def test_remove_accents_completely(self):
        self.assertEqual(remove_accents_completely("áéíóú"), "")

    def test_remove_special_characters(self):
        self.assertEqual(remove_special_characters("!@#$%^&*()"), "")

    def test_remove_asian_characters(self):
        self.assertEqual(remove_asian_characters("你好"), "")

    def test_remove_html_tags(self):
        self.assertEqual(remove_html_tags("<p>test</p>"), "test")

    def test_cleanup_markdown(self):
        self.assertEqual(cleanup_markdown("**test**"), "test")

    def test_remove_extra_whitespace(self):
        self.assertEqual(remove_extra_whitespace("  test  "), "test")

    def test_remove_numbers(self):
        self.assertEqual(remove_numbers("123test"), "test")

    def test_remove_urls(self):
        self.assertEqual(remove_urls("http://example.com"), "")

    def test_remove_emails(self):
        self.assertEqual(remove_emails("test@example.com"), "")

    def test_string_similarity(self):
        self.assertGreater(string_similarity("test", "test"), 99)

    def test_string_similarity_from_list(self):
        result = string_similarity_from_list("test", ["test", "other"])
        self.assertEqual(result[0], "test")


if __name__ == "__main__":
    unittest.main()
