import unittest
from unittest.mock import patch

import pandas as pd

from utility_pack.parallel import parallelize_apply


def sample_df_func(df):
    df["b"] = df["a"] * 2
    return df


class TestParallel(unittest.TestCase):
    @patch("utility_pack.parallel.ProcessPoolExecutor")
    def test_parallelize_apply(self, mock_executor):
        df = pd.DataFrame({"a": [1, 2, 3]})
        mock_executor.return_value.__enter__.return_value.map.return_value = [
            (0, pd.DataFrame({"a": [1], "b": [2]})),
            (1, pd.DataFrame({"a": [2], "b": [4]})),
            (2, pd.DataFrame({"a": [3], "b": [6]})),
        ]

        result_df = parallelize_apply(df, sample_df_func, n_jobs=3)
        self.assertEqual(list(result_df["b"]), [2, 4, 6])


if __name__ == "__main__":
    unittest.main()
