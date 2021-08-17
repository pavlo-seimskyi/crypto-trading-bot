from unittest import TestCase

import pandas as pd
from talipp.indicators import EMA, RSI

from src.feature_extractor.feature_generators import TalippGenerator
from src.feature_extractor.feature_service import FeatureService


class TestFeatureService(TestCase):
    def test_reset(self):
        data = pd.DataFrame({
            "close": [1, 2, 3, 4, 5, 6]
        })

        service = FeatureService(TalippGenerator(EMA, input_column_names="close", period=2),
                                 TalippGenerator(RSI, input_column_names="close", period=3))

        service.initialize(data)
        assert service.status == {'EMA': 5.5, 'RSI': 100.0}

        service.reset()

        assert service.status == {'EMA': None, 'RSI': None}

    def test_initialize(self):
        data = pd.DataFrame({
            "close": [1, 2, 3, 4, 5, 6]
        })

        service = FeatureService(TalippGenerator(EMA, input_column_names="close", period=2),
                                 TalippGenerator(RSI, input_column_names="close", period=3))

        service.initialize(data)
        assert service.data == [{'EMA': None, 'RSI': None},
                                {'EMA': 1.5, 'RSI': None},
                                {'EMA': 2.5, 'RSI': None},
                                {'EMA': 3.5, 'RSI': 100.0},
                                {'EMA': 4.5, 'RSI': 100.0},
                                {'EMA': 5.5, 'RSI': 100.0}]

    def test_add_value_and_purge(self):
        data = pd.DataFrame({"close": [1, 2, 3, 4, 5, 6]})

        service = FeatureService(TalippGenerator(EMA, input_column_names="close", period=2),
                                 TalippGenerator(RSI, input_column_names="close", period=3))

        service.initialize(data)
        assert service.data == [{'EMA': None, 'RSI': None},
                                {'EMA': 1.5, 'RSI': None},
                                {'EMA': 2.5, 'RSI': None},
                                {'EMA': 3.5, 'RSI': 100.0},
                                {'EMA': 4.5, 'RSI': 100.0},
                                {'EMA': 5.5, 'RSI': 100.0}]

        new_row = pd.DataFrame({"timestamp": 12345, "close": 3}, index=[0]).iloc[0]
        service.add_value(new_row, purging=True)

        assert service.data == [{'EMA': 1.5, 'RSI': None},
                                {'EMA': 2.5, 'RSI': None},
                                {'EMA': 3.5, 'RSI': 100.0},
                                {'EMA': 4.5, 'RSI': 100.0},
                                {'EMA': 5.5, 'RSI': 100.0},
                                {'EMA': 3.8333333333333335, 'RSI': 39.99999999999999}]

