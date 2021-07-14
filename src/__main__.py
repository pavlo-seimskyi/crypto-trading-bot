import credentials
import config
import src.functions as functions
import cbpro


if __name__ == '__main__' :
    auth_client = cbpro.AuthenticatedClient(
        key=credentials.KEY,
        b64secret=credentials.SECRET,
        passphrase=credentials.PASSPHRASE,
        api_url=config.API_URL
        )

    tradingSystems = functions.TradingSystems(auth_client)

    tradingSystems.viewAccounts('BTC')['balance']
    # currentPrice = float(tradingSystems.getCurrentPriceOfCurrency())
    balance = float(tradingSystems.viewAccounts(config.CURRENCY_TO_SELL)['balance'])

    currentPrice = float(tradingSystems.getCurrentPriceOfCurrency())


    # this will buy the currency fully spending the EUR
    order_id = tradingSystems.trade(action='buy', funds=float(config.SPEND_PER_TRADE))

    lastOrderInfo = tradingSystems.viewOrder(order_id)
    print(f"Order status: {lastOrderInfo['status']}\nFee: {lastOrderInfo['fill_fees']}\nFilled: {lastOrderInfo['done_reason']}")
