import unittest
from unittest.mock import MagicMock, patch

from utility_pack.logger import get_datetime_brasilia, log_exception


class TestLogger(unittest.TestCase):
    @patch("utility_pack.logger.datetime")
    def test_get_datetime_brasilia(self, mock_datetime):
        mock_now = MagicMock()
        mock_now.strftime.return_value = "01/01/2025 - 12:00:00"
        mock_datetime.datetime.now.return_value = mock_now

        self.assertEqual(get_datetime_brasilia(), "01/01/2025 - 12:00:00")
        self.assertIsNotNone(get_datetime_brasilia(return_string=False))

    @patch("utility_pack.logger.logging")
    @patch("utility_pack.logger.traceback.format_exc")
    @patch("utility_pack.logger.get_datetime_brasilia")
    def test_log_exception(
        self, mock_get_datetime_brasilia, mock_format_exc, mock_logging
    ):
        mock_get_datetime_brasilia.return_value = "01/01/2025 - 12:00:00"
        mock_format_exc.return_value = "Traceback"

        try:
            raise ValueError("test exception")
        except ValueError:
            log_exception()

        mock_logging.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
