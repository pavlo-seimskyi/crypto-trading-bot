import src.config as config
from src.data_scraper import time_helpers
from src.order_executer.service.portfolio import WALLET_WORTH
from src.order_executer.service.order_executer import OrderExecuter
from src.order_executer.service.logger import Logger

from src.backtest import plotting, metrics

OWNER = "BackTest"


class BackTester:
    def __init__(self,
                 data_service,
                 model,
                 portfolio,
                 splits=5,
                 gap_proportion=0.05,
                 valid_proportion=0.25,
                 plot=True):
        self.data_service = data_service
        self.model = model
        self.start_timestamp = self.data_service.start_timestamp
        self.end_timestamp = self.data_service.end_timestamp
        self.splits = splits
        self.train_proportion = 1 - gap_proportion - valid_proportion
        self.gap_proportion = gap_proportion
        self.valid_proportion = valid_proportion
        self.portfolio = portfolio
        self.plot = plot

    def get_split_timestamps(self, split_num):
        split_length = (self.end_timestamp - self.start_timestamp) // split_num
        gap_length = int(split_length * self.gap_proportion)
        valid_length = int(split_length * self.valid_proportion)
        train_length = split_length - valid_length - gap_length

        train_start = self.start_timestamp
        train_end = train_start + train_length
        valid_start = train_start + train_length + gap_length
        valid_end = valid_start + valid_length

        return train_start, train_end, valid_start, valid_end

    def run(self):
        total_results = []

        for split in range(1, self.splits + 1):
            train_start, train_end, valid_start, valid_end = self.get_split_timestamps(split)
            self.train(train_start, train_end)
            results = self.test(valid_start, valid_end)
            total_results.append(results)

        summary = {}
        for metric in results.keys():
            summary[metric] = sum(d[metric] for d in total_results) / len(total_results)

        return summary

    def train(self, train_start_timestamp, train_end_timestamp):
        # data = self.get_training_data(train_start_timestamp, train_end_timestamp)
        # self.model.reset()
        # self.model.train(data)
        pass

    def test(self, valid_start_timestamp, valid_end_timestamp):
        self.data_service.start_timestamp = valid_start_timestamp
        self.data_service.end_timestamp = valid_end_timestamp
        logger = Logger("backtest_logs")

        executer_service = OrderExecuter(self.data_service, [self.portfolio], self.model, logger)
        executer_service.start()

        while executer_service.data_service.last_end_timestamp <= valid_end_timestamp:
            executer_service.step()

        portfolio_history = logger.load_owner_wallet(OWNER)
        wallet_history = list(portfolio_history[WALLET_WORTH])
        price_data = self.get_validation_data(valid_start_timestamp, valid_end_timestamp)

        if self.plot:
            plotting.plot_returns(wallet_history, price_data)

        btc_price_data = price_data[f'BTC{config.CURRENCY_TO_SELL}_Close']
        return metrics.calculate_metrics(wallet_history, btc_price_data)

    def get_training_data(self, train_start_timestamp, train_end_timestamp):
        self.data_service.start_timestamp = train_start_timestamp
        self.data_service.end_timestamp = train_end_timestamp
        _ = self.data_service.initialize()
        training_data = self.data_service.get_channel_data(train_start_timestamp, train_end_timestamp)
        return training_data

    def get_validation_data(self, valid_start_timestamp, valid_end_timestamp):
        window_after_start_time = valid_start_timestamp + time_helpers.get_lookback_window()
        data = self.data_service.channels['Binance'].cache_data.copy()

        return data[
            (data['Timestamp (ms)'] >= window_after_start_time) &
            (data['Timestamp (ms)'] < valid_end_timestamp)
            ]
