import credentials
import cbpro
import config


class TradingSystems :
    def __init__(self, cbpro_client) :
        self.client = cbpro_client

    def trade(self, action, limitPrice, quantity) :
        if action == BUY :
            response = self.client.buy(
                            price=limitPrice,
                            size=self.round(quantity),
                            order_type='limit',
                            product_id=f'{config.CURRENCY_TO_BUY}-{config.CURRENCY_TO_SELL}',
                            overdraft_enabled=False
                            )
            return response['id']

        elif action == SELL :
            response = self.client.sell(
                            price=limitPrice,
                            size=self.round(quantity),
                            order_type='limit',
                            product_id=f'{config.CURRENCY_TO_BUY}-{config.CURRENCY_TO_SELL}',
                            overdraft_enabled=False
                            )
            return response['id']

    def round(self, val):
        return Decimal(int(val * Decimal(10000000)))/Decimal(10000000)

    def viewAccounts(self, accountCurrency) :
        accounts = self.client.get_accounts()
        account = list(filter(lambda x : x['currency'] == accountCurrency, accounts))[0]
        return accounts

    def viewOrder(self, order_id) :
        response = self.client.get_order(order_id)
        return response # {'status': response['status'], 'fee' : response['fee'], 'done_reason' : response['done_reason']}

    def getCurrentPriceOfCurrency(self) :
        tick = self.client.get_product_ticker(product_id=f'{config.CURRENCY_TO_BUY}-{config.CURRENCY_TO_SELL}')
        return tick['bid']



if __name__ == '__main__' :
    auth_client = cbpro.AuthenticatedClient(
        key=credentials.KEY,
        b64secret=credentials.SECRET,
        passphrase=credentials.PASSPHRASE,
        api_url=config.API_URL
        )

    tradingSystems = TradingSystems(auth_client)

    # print(tradingSystems.viewAccounts('BTC')['balance'])
    currentPrice = float(tradingSystems.getCurrentPriceOfCurrency())
    balance = float(tradingSystems.viewAccounts(config.CURRENCY_TO_SELL)['balance'])

    # this will buy the currency fully spending the EUR
    order_id = tradingSystems.trade(action=BUY, limitPrice=currentPrice, quantity=balance/currentPrice)

    lastOrderInfo = tradingSystems.viewOrder(order_id)
    print(f"Order status: {lastOrderInfo['status']}\nFee: {lastOrderInfo['fill_fees']}\nFilled: {lastOrderInfo['done_reason']}")
