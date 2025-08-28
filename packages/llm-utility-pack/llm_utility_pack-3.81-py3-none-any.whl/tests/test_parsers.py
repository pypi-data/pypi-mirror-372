import unittest

from utility_pack.parsers import (
    extract_markdown_content,
    find_and_parse_json_from_string,
)


class TestParsers(unittest.TestCase):
    def test_find_and_parse_json_from_string(self):
        text = 'Here is some json: {"key": "value"}'
        parsed = find_and_parse_json_from_string(text)
        self.assertEqual(parsed, {"key": "value"})

        text_encapsulated = '```json\n{"key": "value"}\n```'
        parsed_encapsulated = find_and_parse_json_from_string(text_encapsulated)
        self.assertEqual(parsed_encapsulated, {"key": "value"})

    def test_extract_markdown_content(self):
        text = "```sql\nSELECT * FROM table\n```"
        content = extract_markdown_content(text, "sql")
        self.assertEqual(content, "SELECT * FROM table")

        text_plain = "```\nHello, world!\n```"
        content_plain = extract_markdown_content(text_plain)
        self.assertEqual(content_plain, "Hello, world!")


if __name__ == "__main__":
    unittest.main()
