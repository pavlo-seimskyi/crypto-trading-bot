from unittest import TestCase
import numpy as np
import sys

from src.data_scraper.time_helpers import get_current_timestamp

sys.path[0] = sys.path[0].split('trading_bot')[0] + 'trading_bot'
from src.data_scraper.scraper_twitter import DataScraper
from src.utils import *



class TestDataScraper(TestCase):
    @staticmethod
    def test_save():
        print(f'{sys.path[0]}/{config.FOLDER_TO_SAVE}/binance/test.csv')
        # Test merging on indexes
        pd.DataFrame({
            'BNB_Open time': [1, 2, 3, 4, 5, 6],
            'BNB_Close': [11, 12, 13, 14, 15, 16],
            'BNB_Volume': [101, 102, 103, 104, 105, 106],
            'BNB_Ignore': ['0.0', '0.0', '0.0', '0.0', '0.0', '0.0'],
            'real time': ['2020-10-23 10:00:00', '2020-10-23 10:01:00', '2020-10-23 10:02:00',
                          '2020-10-23 10:03:00', '2020-10-23 10:04:00', '2020-10-23 10:05:00']
        }).to_csv(f'{sys.path[0]}/{config.FOLDER_TO_SAVE}/binance/test.csv', index=False)

        new_df = pd.DataFrame({
            'BTC_Open time': [4, 5, 6, 7, 8, 9],
            'BTC_Close': [14, 15, 16, 17, 18, 19],
            'BTC_Volume': [104, 105, 106, 107, 108, 109],
            'BTC_Ignore': ['0.0', '0.0', '0.0', '0.0', '0.0', '0.0'],
            'real time': ['2020-10-23 10:03:00', '2020-10-23 10:04:00', '2020-10-23 10:05:00',
                          '2020-10-23 10:06:00', '2020-10-23 10:07:00', '2020-10-23 10:08:00']
        })

        end_timestamp = get_current_timestamp()
        scraper = DataScraper(end_timestamp=end_timestamp)
        scraper.save(new_df, subfolder='binance', filename='test.csv', by='columns', merge_on='real time')
        test_df = pd.read_csv(f'{sys.path[0]}/{config.FOLDER_TO_SAVE}/binance/test.csv')

        assert test_df.iloc[0]['BNB_Volume'] == 101
        assert test_df.iloc[-1]['BNB_Volume'] == np.nan
        assert test_df.iloc[0]['BTC_Volume'] == np.nan
        assert test_df.iloc[-1]['BTC_Volume'] == 109
        assert len(test_df) == 9
        assert len(test_df.columns) == 9
        os.remove(f'{sys.path[0]}/{config.FOLDER_TO_SAVE}/binance/test.csv')

        # Test merging on columns

    def test_add_value(self):
        data = pd.DataFrame({
            "close": [2, 3, 5, 7, 4, 5]
        })

        pass


if __name__ == '__main__':
    test = TestDataScraper
    test.test_save()