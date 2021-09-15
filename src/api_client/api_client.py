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



# class CoinbaseClient:
#     def __init__(self, key, secret, passphrase, api_url, **kwargs):
#         self.client = cbpro.AuthenticatedClient(key=key,
#                                                 b64secret=secret,
#                                                 passphrase=passphrase,
#                                                 api_url=api_url)
#
#     def trade(self, action, limit_price, quantity):
#         if action == 'buy':
#             response = self.client.buy(
#                 price=limit_price,
#                 size=quantity,
#                 order_type='limit',
#                 product_id=f'{config.CURRENCY_TO_BUY}-{config.CURRENCY_TO_SELL}',
#                 overdraft_enabled=False
#             )
#             return response['id']
#
#         elif action == 'sell':
#             response = self.client.sell(
#                 price=limitPrice,
#                 size=quantity,
#                 order_type='limit',
#                 product_id=f'{config_coinbase.CURRENCY_TO_BUY}-{config_coinbase.CURRENCY_TO_SELL}',
#                 overdraft_enabled=False
#             )
#             return response['orderId']
#
#     def view_order(self, order_id):
#         response = self.client.get_order(orderId=order_id)
#         return response  # {'status': response['status'], 'fee' : response['fee'], 'done_reason' : response['done_reason']}
#
#     def viewAccounts(self, accountCurrency):
#         accounts = self.client.get_accounts()
#         account = list(filter(lambda x: x['currency'] == accountCurrency, accounts))[0]
#         return accounts
#
#     def getCurrentPriceOfCurrency(self):
#         tick = self.client.get_product_ticker(
#             product_id=f'{config_coinbase.CURRENCY_TO_BUY}-{config_coinbase.CURRENCY_TO_SELL}')
#         return tick['bid']
