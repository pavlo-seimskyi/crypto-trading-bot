import os.path

from src import utils

import pandas as pd
import pyarrow.parquet as pq

import credentials
from src import config
from src.api_client.api_client import BinanceClient
from src.data_scraper import time_helpers


class BinanceScraper:
    """
    Get Binance API exchange rates for all selected currencies. Operates in UTC timezone.
    It always scrapes data in production and loads data from disk in development.
    """
    def __init__(self, currency_to_buy=config.CURRENCY_TO_BUY, currency_to_sell=config.CURRENCY_TO_SELL,
                 all_currencies=config.ALL_CURRENCIES, interval=config.INTERVAL, **kwargs):
        self.name = "Binance"
        self.client = BinanceClient(key=credentials.BINANCE_API_KEY, secret=credentials.BINANCE_API_SECRET)
        self.interval = interval
        self.currency_to_buy = currency_to_buy
        self.currency_to_sell = currency_to_sell
        self.currency_pairs = [
            f'{self.currency_to_buy}{self.currency_to_sell}',
            *[f'{currency}{self.currency_to_sell}' for currency in all_currencies if currency != self.currency_to_buy]
        ]
        self.col_names_and_dtypes = {
            'Timestamp (ms)': int,
            'Open': float,
            'High': float,
            'Low': float,
            'Close': float,
            'Volume': float,
            'Close time': int,
            'Quote asset volume': float,
            'Number of trades': int,
            'Taker buy base asset volume': float,
            'Taker buy quote asset volume': float,
            'Ignore': int
        }
        base_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.dataset_path = f"{base_path}/{config.FOLDER_TO_SAVE}/{self.name}/{self.interval}"
        self.cache_data = None

    def scrape_data(self, start_time, end_time):
        """
        Scrape the data from the Binance API. Operates in UTC timezone.
        """
        df = pd.DataFrame(columns=self.col_names_and_dtypes)

        for currency_pair in self.currency_pairs:
            klines = self.client.get_exchange_rates(
                currency_pair=currency_pair, interval=self.interval, start_time=start_time, end_time=end_time)

            temp_df = pd.DataFrame(klines, columns=self.col_names_and_dtypes.keys())

            # Setting the right data types to save later as metadata in parquet
            temp_df = temp_df.astype(self.col_names_and_dtypes)

            # Rename the columns, except for merger column
            temp_df = temp_df.rename(columns={f'{col}': f'{currency_pair}_{col}' for col in temp_df.columns
                                              if col != 'Timestamp (ms)'})

            temp_df = temp_df.drop('Ignore', axis=1)  # Drop the "Ignore" column that Binance sends

            if len(df) == 0:
                df = temp_df.copy()
            else:
                df = df.merge(temp_df, how='outer', on='Timestamp (ms)')

        # Getting the merger column
        df[config.MERGE_DATA_ON] = pd.to_datetime(df['Timestamp (ms)'], unit='ms')

        # Date column to partition by with parquet later
        df['date'] = df[config.MERGE_DATA_ON].dt.date

        return df

    def get_stored_data(self, start_time, end_time):
        """
        Returns the exact slice of cached data that is between start and end timestamp.
        """
        data = self.cache_data.loc[(self.cache_data["Timestamp (ms)"] > start_time) &
                                   (self.cache_data["Timestamp (ms)"] <= end_time), :]
        if len(data) == 0:
            raise RuntimeError("No more data")

        return data

    def load_from_disk(self, start_time, end_time) -> None:
        """
        Load stored data into cache. To actually get the dataframe returned, call get_stored_data().
        :param start_time: start timestamp
        :param end_time: end timestamp
        :return: None
        """
        if not utils.dataset_stored(self.dataset_path, start_time, end_time):
            for chunk_start, chunk_end in time_helpers.slice_timestamps_in_chunks(start_time, end_time):
                data = self.scrape_data(chunk_start, chunk_end)
                utils.save_data(data, self.dataset_path)
        data = pq.read_table(source=self.dataset_path).to_pandas()
        data = data.groupby(config.MERGE_DATA_ON, as_index=False).last()  # Only takes the last saved data
        self.cache_data = data
