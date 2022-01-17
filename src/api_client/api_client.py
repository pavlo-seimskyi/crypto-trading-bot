from binance.client import Client
from binance import enums
import pandas as pd
import numpy as np
from src import config


class BinanceClient:
    def __init__(self, api_key, api_secret, **kwargs):
        self.client = Client(api_key=api_key, api_secret=api_secret)

    def get_historical_exchange_rates(self, currency_pair, interval, start_time, end_time):
        """
        Get historical exchange rates for a currency pair from Binance
        :param currency_pair: Currency to buy & currency to sell (ex.: BTCEUR)
        :param interval: 1m, 5m, 15m, 1h, 2h, 4h, 6h, 8h, 1d, 3d, etc.
        :param start_time: Date string in UTC format or timestamp in milliseconds.
        :param end_time: Date string in UTC format or timestamp in milliseconds.
        :return:
        """
        response = self.client.get_historical_klines(symbol=currency_pair,
                                                     interval=interval,
                                                     start_str=start_time,
                                                     end_str=end_time)
        return response

    def get_current_exchange_rate(self, currency_to_buy, currency_to_sell, data=None):
        currency_pair_exists = self.client.get_symbol_info(f'{currency_to_buy}{currency_to_sell}') is not None
        if currency_pair_exists:
            exchange_rate = self.client.get_symbol_ticker(symbol=f'{currency_to_buy}{currency_to_sell}')['price']
            return float(exchange_rate)
        else:
            exchange_rate = self.client.get_symbol_ticker(symbol=f'{currency_to_sell}{currency_to_buy}')['price']
            return 1 / float(exchange_rate)

    def trade(self, currency_to_buy, currency_to_sell, action, amount, data=None):
        precision = self.get_amount_precision(currency_pair=f'{currency_to_buy}{currency_to_sell}')
        response = self.client.create_test_order(symbol=f'{currency_to_buy}{currency_to_sell}',
                                                 quantity=f"%.{precision}f" % amount,
                                                 side=action,
                                                 type=enums.ORDER_TYPE_MARKET)
        return response

    def get_balances(self):
        """
        Get all the balances with values of more than 0 of the account.
        :return: pd.DataFrame
        """
        info = self.client.get_account()
        portfolio = pd.DataFrame(info['balances'])
        portfolio = portfolio.set_index('asset')
        portfolio = portfolio.astype(float)
        return portfolio[portfolio['free'] > 0]

    def get_commission(self, currency_pair=f'{config.CURRENCY_TO_BUY}{config.CURRENCY_TO_SELL}'):
        fees = self.client.get_trade_fee(symbol=currency_pair)
        return float(fees[0]['takerCommission'])

    def get_amount_precision(self, currency_pair=f'{config.CURRENCY_TO_BUY}{config.CURRENCY_TO_SELL}'):
        asset_info = self.client.get_symbol_info(currency_pair)
        step_size = float(asset_info['filters'][2]['stepSize'])
        return int(np.log10(round(1 / step_size)))

    def get_minimum_amount(self, currency_to_buy, currency_to_sell):
        asset_info = self.client.get_symbol_info(f'{currency_to_buy}{currency_to_sell}')
        if asset_info['filters'][3]['applyToMarket']:
            amount_usdt = float(asset_info['filters'][3]['minNotional'])
        else:
            amount_usdt = float(asset_info['filters'][5]['minNotional'])
        price = self.get_current_exchange_rate(currency_to_buy=currency_to_buy, currency_to_sell=currency_to_sell)
        return amount_usdt / price


class BinanceBackTestClient(BinanceClient):
    def __init__(self, api_key, api_secret, **kwargs):
        super().__init__(api_key, api_secret, **kwargs)
        self.balances = pd.DataFrame(
            data=[[0.02, 0],   # BTC
                  [1000, 0]],  # EUR
            index=[config.CURRENCY_TO_BUY, config.CURRENCY_TO_SELL],
            columns=['free', 'locked']
        )
        self.commission = super().get_commission(f'{config.CURRENCY_TO_BUY}{config.CURRENCY_TO_SELL}')
        self.precision = super().get_amount_precision(f'{config.CURRENCY_TO_BUY}{config.CURRENCY_TO_SELL}')
        self.min_amount = super().get_minimum_amount(config.CURRENCY_TO_BUY, config.CURRENCY_TO_SELL)

    def get_current_exchange_rate(self, currency_to_buy, currency_to_sell, data=None):
        if data is None:
            return super().get_current_exchange_rate(currency_to_buy, currency_to_sell)
        if f"{currency_to_buy}{currency_to_sell}_Open" in data.columns:
            return data.iloc[-1][f"{currency_to_buy}{currency_to_sell}_Open"]
        else:
            return 1 / data.iloc[-1][f"{currency_to_sell}{currency_to_buy}_Open"]

    def get_balances(self):
        return self.balances

    def get_commission(self, *args, **kwargs):
        return self.commission

    def get_amount_precision(self, *args, **kwargs):
        return self.precision

    def get_minimum_amount(self, *args, **kwargs):
        return self.min_amount

    def trade(self, currency_to_buy, currency_to_sell, action, amount, data=None):
        exchange_rate = self.get_current_exchange_rate(currency_to_buy, currency_to_sell, data)
        commission = self.get_commission()
        if action == enums.SIDE_BUY:
            self.balances.at[currency_to_sell, 'free'] -= amount * exchange_rate * (1 + commission)
            self.balances.at[currency_to_buy,  'free'] += amount
        if action == enums.SIDE_SELL:
            self.balances.at[currency_to_buy,  'free'] -= amount * (1 + commission)
            self.balances.at[currency_to_sell, 'free'] += amount * exchange_rate

