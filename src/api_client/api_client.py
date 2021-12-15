from binance.client import Client


class BinanceClient:
    def __init__(self, key, secret, **kwargs):
        self.client = Client(api_key=key, api_secret=secret)

    def get_exchange_rates(self, currency_pair, interval, start_time, end_time):
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

    def get_current_price(self, currency_to_buy, currency_to_sell):
        return self.client.get_symbol_ticker(symbol=f'{currency_to_buy}{currency_to_sell}')['price']

    def trade(self, currency_to_buy, currency_to_sell, action, quantity):
        response = self.client.create_order(symbol=f'{currency_to_buy}{currency_to_sell}',
                                            quantity=round(quantity),
                                            side=action,
                                            type='MARKET')
        return response['orderId']

    def view_order(self, order_id):
        pass

    def view_account(self):
        pass
