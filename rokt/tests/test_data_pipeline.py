import unittest
import pandas as pd
from rokt.data_pipeline import process_df


class TestProcessDf(unittest.TestCase):
    def test_process_df(self):
        data = [['2000-01-01T25:49Z', 'casey.eichmann@hayes.us', '56cc8832-9f9d-4dc5-b340-8dabc5107430'],
                [None, None, None],
                ['2000-01-01T50:25:49Z', None, None]
                ]
        input_df = pd.DataFrame(data)
        output_df = process_df(input_df, 'test_file.txt', 'sqlite')
        print(output_df)
        actual = len(output_df)
        expected = 0
        self.assertEqual(actual, expected)
