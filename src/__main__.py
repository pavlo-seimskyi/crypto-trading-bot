import credentials
import config
import src.functions as functions
import cbpro
import time


if __name__ == '__main__' :
    auth_client = cbpro.AuthenticatedClient(
        key=credentials.KEY,
        b64secret=credentials.SECRET,
        passphrase=credentials.PASSPHRASE,
        api_url=config.API_URL
        )

    tradingSystems = functions.TradingSystems(auth_client)
    functions.get_trading_data(path=config.FOLDER_TO_SAVE)

    # tradingSystems.viewAccounts('BTC')['balance']
    # # currentPrice = float(tradingSystems.getCurrentPriceOfCurrency())
    # balance = float(tradingSystems.viewAccounts(config.CURRENCY_TO_SELL)['balance'])
    #
    # currentPrice = float(tradingSystems.getCurrentPriceOfCurrency())
    #
    #
    # # this will buy the currency fully spending the EUR
    # order_id = tradingSystems.trade(action='buy', funds=float(config.SPEND_PER_TRADE))
    #
    # lastOrderInfo = tradingSystems.viewOrder(order_id)
    # print(f"Order status: {lastOrderInfo['status']}\nFee: {lastOrderInfo['fill_fees']}\nFilled: {lastOrderInfo['done_reason']}")

    # while True :
    #     tradingSystems.viewAccounts('BTC')['balance']
    #     tradingSystems.viewAccounts(config.CURRENCY_TO_SELL)['balance']
    #     tradingSystems.getCurrentPriceOfCurrency()
    #
    #     tradingSystems.trade(action='buy')
    #     time.sleep(60)
    #
    #     tradingSystems.trade(action='sell')
    #     time.sleep(60)
