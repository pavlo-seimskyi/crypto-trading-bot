import os
from functools import partial

import pandas as pd

import credentials
from src import config
from src.api_client.api_client import BinanceClient
from src.data_scraper import time_helpers


class BinanceScraper:
    def __init__(self, currency_to_buy=config.CURRENCY_TO_BUY, currency_to_sell=config.CURRENCY_TO_SELL,
                 all_currencies=config.ALL_CURRENCIES, interval=config.INTERVAL, dev_run=True, **kwargs):
        os.makedirs(f'{config.FOLDER_TO_SAVE}/binance', exist_ok=True)
        self.name = "Binance"
        self.dev_run = dev_run
        self.client = BinanceClient(key=credentials.BINANCE_API_KEY, secret=credentials.BINANCE_API_SECRET)
        self.interval = interval
        self.currency_to_buy = currency_to_buy
        self.currency_to_sell = currency_to_sell
        all_currencies.remove(self.currency_to_buy)
        self.currency_pairs = [f'{self.currency_to_buy}{self.currency_to_sell}',
                               *[f'{currency}{self.currency_to_sell}' for currency in all_currencies]]
        self.col_names = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                          'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']

        self.dataset_path = f"{config.FOLDER_TO_SAVE}/binance"
        self.dataset_name = f"{self.currency_to_buy}{self.currency_to_sell}"

    def get_data(self, start_time, end_time):
        """Get Binance API exchange rates for all selected currencies. Operates in UTC timezone.
        By default, it will try to continue from the latest available data point if the last saved timestamp is ahead
        of the timestamp specified in the config, to save time instead of loading already available data."""

        df = pd.DataFrame(columns=self.col_names)

        for currency_pair in self.currency_pairs:
            start_time_datetime = time_helpers.timestamp_to_str(start_time, format="exact_time")
            end_time_datetime = time_helpers.timestamp_to_str(end_time, format="exact_time")
            klines = self.client.get_exchange_rates(
                currency_to_buy=self.currency_to_buy, currency_to_sell=self.currency_to_sell,
                interval=self.interval, start_time=start_time_datetime, end_time=end_time_datetime)

            temp_df = pd.DataFrame(klines, columns=self.col_names)
            temp_df[config.MERGE_DATA_ON] = temp_df['Open time'].apply(partial(
                time_helpers.timestamp_to_str, format='exact_time'))

            # Rename the columns, except for merger column
            temp_df = temp_df.rename(columns={f'{col}': f'{currency_pair}_{col}' for col in temp_df.columns
                                              if col != config.MERGE_DATA_ON})

            if len(temp_df) == 0:
                print(f'{currency_pair}_{self.interval} skipped.')

            if len(df) == 0:
                df = temp_df.copy()
            else:
                df = df.merge(temp_df, how='outer', on=config.MERGE_DATA_ON)

        # Creating general datetime column in seconds
        df["datetime"] = df[f"{currency_pair}_Open time"]

        return df

    def load_dataset(self, start_time, end_time):
        full_dataset_name = f"{self.dataset_name}_{start_time}_{end_time}"
        if self.dataset_not_stored(full_dataset_name):
            to_store_dataset = self.get_data(start_time, end_time)
            to_store_dataset.to_csv(f"{self.dataset_path}/{full_dataset_name}")
            self.cache_dataset = to_store_dataset
        else:
            self.cache_dataset = pd.read_csv(f"{self.dataset_path}/{full_dataset_name}")

        self.cache_dataset[config.MERGE_DATA_ON] = pd.to_datetime(self.cache_dataset[config.MERGE_DATA_ON],
                                                                  infer_datetime_format=True)

    def dataset_not_stored(self, full_dataset_name):
        return not os.path.exists(f"{self.dataset_path}/{full_dataset_name}")

    def get_stored_data(self, start_time, end_time):
        data =  self.cache_dataset.loc[
               (self.cache_dataset["datetime"] > start_time) & (
                           self.cache_dataset["datetime"] <= end_time), :]

        if len(data) == 0:
            raise RuntimeError("No more data")
        return data
