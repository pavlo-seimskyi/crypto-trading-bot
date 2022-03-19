from src.order_executer.service.data_service import TrainingDataService
from src.data_scraper.scraper_binance import BinanceScraper
from src import config
from src.api_client.api_client import BinanceClient
from src.feature_extractor.feature_service import FeatureService
from src.config import FEATURE_GENERATORS
import numpy as np
import pandas as pd

INTERVAL_PERIOD_IN_MINUTES = 1
COLNAME_TO_PREDICT = f'{config.CURRENCY_TO_BUY}{config.CURRENCY_TO_SELL}_Close'


class DataBuilder:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def build(self):
        raw_data = self.get_raw_data()
        features = self.build_features(raw_data=raw_data)
        features = self.fill_features_to_longest(features)
        prices = raw_data[COLNAME_TO_PREDICT].values
        # 1% change in 1 hour
        features['label'] = self.three_bar_method(variable_to_predict=prices, interval_rows=60, threshold_pct=0.01)
        return features

    def get_raw_data(self):
        data_service = TrainingDataService(
            interval_period_in_minutes=INTERVAL_PERIOD_IN_MINUTES,
            channels=[BinanceScraper()],
            start_date=self.start_date,
            end_date=self.end_date
        )
        _ = data_service.initialize()
        return data_service.channels['Binance'].cache_data

    def build_features(self, raw_data: pd.DataFrame) -> dict:
        feature_service = FeatureService(*FEATURE_GENERATORS)
        features = feature_service.initialize(raw_data)
        return feature_service.all_data

    def fill_features_to_longest(self, features: dict):
        max_length = max([len(feature) for feature in features.values()])
        for feature in features:
            missing_items = max_length - len(features[feature])
            features[feature] = missing_items * [np.nan] + features[feature]
        return features

    # Labeler
    def three_bar_method(self, variable_to_predict: list, interval_rows: int, threshold_pct: float) -> np.array:
        """
        Label depending on change in future values of a variable.
        Positive and negative changes above threshold get labeled as 1 and -1, respectively.
        Below threshold as 0.
        """
        future_variable = np.roll(a=variable_to_predict, shift=-interval_rows)

        labels = future_variable / variable_to_predict - 1

        labels[labels > threshold_pct] = 1
        labels[(labels <= threshold_pct) & (labels >= -threshold_pct)] = 0
        labels[labels < -threshold_pct] = -1

        return labels
