import src.config as config
import credentials
import cbpro
from binance.client import Client
import datetime as dt


class APIClient:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def round(self, val):
        return Decimal(int(val * Decimal(10000000))) / Decimal(10000000)

    def get_current_timestamp(self):
        return int(round(dt.datetime.now(dt.timezone.utc).timestamp() * 1000))

    def convert_to_timestamp(self, time):
        return int(dt.datetime.strptime(time, '%Y-%m-%d').timestamp() * 1000)

    # def trade(self):
    #     pass


class BinanceClient(APIClient):
    def __init__(self, key, secret, **kwargs):
        self.client = Client(api_key=key, api_secret=secret)
        super().__init__(**kwargs)

    def get_historical_prices(self, currency_to_buy, currency_to_sell, interval, start_time, end_time):
        '''start_str | end_str : Date string in UTC format or timestamp in milliseconds.'''
        response = self.client.get_historical_klines(symbol=f'{currency_to_buy}{currency_to_sell}',
                                                     interval=interval,
                                                     start_str=start_time,
                                                     end_str=end_time)
        return response

    def get_latest_prices(self, currency_to_buy, currency_to_sell, interval, start_time, end_time):
        '''
        Can get a max of 1,000 klines.
        startTime | endTime : Timestamp in milliseconds.
        '''
        response = self.client.get_klines(symbol=f'{currency_to_buy}{currency_to_sell}',
                                          interval=interval,
                                          limit=1000,
                                          startTime=start_time,
                                          endTime=end_time)
        return response

    def get_current_price(self, currency_to_buy, currency_to_sell):
        return self.client.get_symbol_ticker(symbol=f'{currency_to_buy}{currency_to_sell}')['price']

    def trade(self, currency_to_buy, currency_to_sell, action, quantity):
        response = self.client.create_order(symbol=f'{currency_to_buy}{currency_to_sell}',
                                            quantity=super().round(quantity),
                                            side=action,
                                            type='MARKET')
        return response['orderId']

    def view_order(self, order_id):
        response = self.client.get_order(orderId=order_id)
        return response

    def view_account(self):
        pass



class CoinbaseClient(APIClient):
    def __init__(self, key, secret, passphrase, api_url, **kwargs):
        super().__init__(**kwargs)
        self.client = cbpro.AuthenticatedClient(key=key,
                                                b64secret=secret,
                                                passphrase=passphrase,
                                                api_url=api_url)

    def trade(self, action, limitPrice, quantity):
        if action == 'buy':
            response = self.client.buy(
                price=limitPrice,
                size=self.round(quantity),
                order_type='limit',
                product_id=f'{config_coinbase.CURRENCY_TO_BUY}-{config_coinbase.CURRENCY_TO_SELL}',
                overdraft_enabled=False
            )
            return response['id']

        elif action == 'sell':
            response = self.client.sell(
                price=limitPrice,
                size=self.round(quantity),
                order_type='limit',
                product_id=f'{config_coinbase.CURRENCY_TO_BUY}-{config_coinbase.CURRENCY_TO_SELL}',
                overdraft_enabled=False
            )
            return response['orderId']

        def view_order(self, order_id):
            response = self.client.get_order(orderId=order_id)
            return response  # {'status': response['status'], 'fee' : response['fee'], 'done_reason' : response['done_reason']}

        def viewAccounts(self, accountCurrency):
            accounts = self.client.get_accounts()
            account = list(filter(lambda x: x['currency'] == accountCurrency, accounts))[0]
            return accounts

        def getCurrentPriceOfCurrency(self):
            tick = self.client.get_product_ticker(
                product_id=f'{config_coinbase.CURRENCY_TO_BUY}-{config_coinbase.CURRENCY_TO_SELL}')
            return tick['bid']
