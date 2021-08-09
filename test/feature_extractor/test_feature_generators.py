from unittest import TestCase

import pandas as pd
from talipp.indicators import MACD, EMA

from src.feature_extractor.feature_generators import TalippGenerator


class TestTalippGenerator(TestCase):
    def test_initialize(self):
        data = pd.DataFrame({
            "close": [2, 3, 5, 7, 4, 5]
        })

        EMA_feature = TalippGenerator(EMA, input_column_names="close", period=2)

        EMA_feature.initialize(data)
        assert EMA_feature.output_values == [2.5, 4.166666666666666, 6.055555555555555, 4.685185185185185, 4.895061728395062]
        assert EMA_feature.name == "EMA"
        assert EMA_feature.last_value == 4.895061728395062

    def test_add_value(self):
        data = pd.DataFrame({
            "close": [2, 3, 5, 7, 4, 5]
        })

        EMA_feature = TalippGenerator(EMA, input_column_names="close", period=2)

        EMA_feature.initialize(data)

        assert EMA_feature.last_value == 4.895061728395062

        data_row = pd.DataFrame({"close": [8]})
        EMA_feature.add_value(data_row, False)

        assert EMA_feature.last_value == 6.965020576131687

