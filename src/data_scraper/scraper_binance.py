from src import utils

import pandas as pd
import pyarrow.parquet as pq

import credentials
from src import config
from src.api_client.api_client import BinanceClient
from src.data_scraper import time_helpers


class BinanceScraper:
    def __init__(self, currency_to_buy=config.CURRENCY_TO_BUY, currency_to_sell=config.CURRENCY_TO_SELL,
                 all_currencies=config.ALL_CURRENCIES, interval=config.INTERVAL, dev_run=True, **kwargs):
        self.name = "Binance"
        self.dev_run = dev_run
        self.client = BinanceClient(key=credentials.BINANCE_API_KEY, secret=credentials.BINANCE_API_SECRET)
        self.interval = interval
        self.currency_to_buy = currency_to_buy
        self.currency_to_sell = currency_to_sell
        self.currency_pairs = [
            f'{self.currency_to_buy}{self.currency_to_sell}',
            *[f'{currency}{self.currency_to_sell}' for currency in all_currencies if currency != self.currency_to_buy]
        ]
        self.col_names = ['Timestamp (ms)', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                          'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
        self.datatypes = [int, float, float, float, float, float, int, float, int, float, float, int]
        self.dataset_path = f"{config.FOLDER_TO_SAVE}/{self.name}/{self.interval}"
        self.cache_data = None

    def get_data(self, start_time, end_time):
        """
        Load the exchange data from Binance. Always scrapes data in production.
        Tries to load data from disk in development. If it is not possible, scrapes the data and saves in parquet.
        """
        if not self.dev_run:  # Always scrape if in production
            return self.scrape_data(start_time, end_time)
        else:  # Try loading from disk if in development
            return self.get_stored_data(start_time, end_time)

    def scrape_data(self, start_time, end_time):
        """
        Get Binance API exchange rates for all selected currencies. Operates in UTC timezone.
        """
        df = pd.DataFrame(columns=self.col_names)

        for currency_pair in self.currency_pairs:
            klines = self.client.get_exchange_rates(
                currency_to_buy=self.currency_to_buy, currency_to_sell=self.currency_to_sell,
                interval=self.interval, start_time=start_time, end_time=end_time)

            temp_df = pd.DataFrame(klines, columns=self.col_names)

            # Setting the right data types to save later as metadata in parquet
            temp_df = temp_df.astype({col_name: dtype for col_name, dtype in zip(self.col_names, self.datatypes)})

            # Rename the columns, except for merger column
            temp_df = temp_df.rename(columns={f'{col}': f'{currency_pair}_{col}' for col in temp_df.columns
                                              if col != 'Timestamp (ms)'})

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
