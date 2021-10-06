from binance.client import Client


class BinanceClient:
    def __init__(self, key, secret, **kwargs):
        self.client = Client(api_key=key, api_secret=secret)

    def get_exchange_rates(self, currency_to_buy, currency_to_sell, interval, start_time, end_time):
        """
        start_str | end_str : Date string in UTC format or timestamp in milliseconds.
        """
        response = self.client.get_historical_klines(symbol=f'{currency_to_buy}{currency_to_sell}',
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
