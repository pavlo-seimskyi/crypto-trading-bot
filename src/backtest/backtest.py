import src.config as config
import credentials
from src.data_scraper import time_helpers
from src.api_client.api_client import BinanceBackTestClient
from src.order_executer.service.portfolio import Portfolio, WALLET_WORTH
from src.order_executer.service.order_executer import OrderExecuter
from src.order_executer.service.logger import Logger

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

OWNER = "BackTest"

class BackTester:
    def __init__(self,
                 data_service,
                 model,
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
        self.portfolio = Portfolio(owner_name=OWNER,
                                   client=BinanceBackTestClient(api_key=credentials.BINANCE_API_KEY,
                                                                api_secret=credentials.BINANCE_API_SECRET))
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

        if self.plot:
            self.plot_returns(wallet_history, valid_start_timestamp, valid_end_timestamp)

        return self.calculate_metrics(wallet_history, valid_start_timestamp, valid_end_timestamp)

    def calculate_metrics(self, history, valid_start_timestamp, valid_end_timestamp):
        metrics = {}
        returns = self.pct_change(history)

        price_data = self.get_validation_data(valid_start_timestamp, valid_end_timestamp)
        btc_prices = price_data[f'BTC{config.CURRENCY_TO_SELL}_Close']
        btc_returns = btc_prices.pct_change().dropna().to_numpy()
        metrics['return'] = self.cumulative_returns(returns)[-1]
        metrics['sharpe'] = self.sharpe_ratio(returns)
        metrics['sortino'] = self.sortino_ratio(returns)
        metrics['max_drawdown'] = self.max_drawdown(returns)
        metrics['btc_return'] = self.cumulative_returns(btc_returns)[-1]
        metrics['btc_sharpe'] = self.sharpe_ratio(btc_returns)

        return metrics

    def plot_returns(self, history, valid_start_timestamp, valid_end_timestamp):
        returns = self.pct_change(history)
        cum_returns = self.cumulative_returns(returns)

        price_data = self.get_validation_data(valid_start_timestamp, valid_end_timestamp)
        dates = price_data['exact_time']
        price_data = price_data[[f'{crypto}{config.CURRENCY_TO_SELL}_Close' for crypto in ['BTC', 'ETH']]]
        tics = [x.split(f'{config.CURRENCY_TO_SELL}')[0]
                for x in price_data.columns[price_data.columns.str.endswith('_Close')]]

        fig = make_subplots(rows=1)
        # Current strategy that is being tested
        fig.add_trace(
            go.Scatter(x=dates.iloc[1:], y=cum_returns, name="Strategy"), row=1, col=1
        )

        # Holding different cryptos
        for tic in tics:
            tic_returns = price_data[f'{tic}{config.CURRENCY_TO_SELL}_Close'].pct_change().dropna().to_numpy()
            tic_cum_returns = self.cumulative_returns(tic_returns)
            fig.add_trace(
                go.Scatter(x=dates.iloc[1:], y=tic_cum_returns, name=tic), row=1, col=1
            )

        # Horizontal line along ROI=1
        fig.add_shape(
            type="line", x0=dates.iloc[1], x1=dates.iloc[-1], y0=1, y1=1,
            line_width=2, line_dash="dot", line_color="grey"
        )

        fig.show()

    def get_training_data(self, train_start_timestamp, train_end_timestamp):
        self.data_service.start_timestamp = train_start_timestamp
        self.data_service.end_timestamp = train_end_timestamp
        _ = self.data_service.initialize()
        training_data = self.data_service.get_channel_data(train_start_timestamp, train_end_timestamp)
        return training_data

    def get_validation_data(self, valid_start_timestamp, valid_end_timestamp):
        window_after_start_time = time_helpers.add_lookback_window(valid_start_timestamp)
        data = self.data_service.channels['Binance'].cache_data.copy()

        return data[
            (data['Timestamp (ms)'] >= window_after_start_time) &
            (data['Timestamp (ms)'] < valid_end_timestamp)
        ]

    # CALCULATING METRICS
    def pct_change(self, x):
        return np.diff(x, axis=0) / x[1:]

    def sharpe_ratio(self, returns):
        cumulative_returns = self.cumulative_returns(returns)
        return (cumulative_returns[-1] - 1) / np.std(returns)

    def sortino_ratio(self, returns):
        cumulative_returns = self.cumulative_returns(returns)
        return (cumulative_returns[-1] - 1) / np.std([ret for ret in returns if ret < 0])

    def max_drawdown(self, returns):
        returns = pd.Series(returns)
        rolling_max = (returns + 1).cumprod().rolling(window=1440, min_periods=1).max()
        daily_value = (returns + 1).cumprod()
        return -(rolling_max - daily_value).max()

    def cumulative_returns(self, returns):
        cumulative_returns = (returns + 1).cumprod(axis=0)
        return cumulative_returns

    # TODO research if this approach is better than the current one
    #     def sharpe_ratio(self, returns, N=60*24*365, risk_free_rate=0):
    #         mean = returns.mean() * N - risk_free_rate
    #         sigma = returns.std() * np.sqrt(N)
    #         return mean / sigma

    # TODO research if this approach is better than the current one
    #     def sortino_ratio(self, returns, N=60*24*365, risk_free_rate=0):
    #         mean = returns.mean() * N - risk_free_rate
    #         negative_std = returns[returns < 0].std() * np.sqrt(N)
    #         return mean / negative_std
