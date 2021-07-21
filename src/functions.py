import cbpro
import pandas as pd
import os
import credentials
import datetime
import time
from dateutil import parser
import config


def get_trading_data(path=config.FOLDER_TO_SAVE):
    client = cbpro.AuthenticatedClient(key=credentials.KEY,
                                       b64secret=credentials.SECRET,
                                       passphrase=credentials.PASSPHRASE)


    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', path)
    os.makedirs(path, exist_ok=True)
    print(path)

    samples_backwards = (3600 / config.GRANULARITY_IN_SECONDS) * 24 * config.DAYS_BACK # min * hours * days
    cycles = int(samples_backwards / 300)
    step = pd.to_timedelta(300, config.GRANULARITY)
    first_date = datetime.datetime.now() - pd.to_timedelta(samples_backwards, config.GRANULARITY)

    for currency_pair in config.CURRENCY_PAIRS:
      df = pd.DataFrame()

      for cycle in range(cycles) :
        if cycle == 0 :
          start_date = first_date
        else:
          start_date = parser.parse(start_date) + step
        end_date = start_date + step
        start_date = start_date.isoformat()
        end_date = end_date.isoformat()
        response = client.get_product_historic_rates(currency_pair, start=start_date, end=end_date, granularity=config.GRANULARITY_IN_SECONDS)
        temp_df = pd.DataFrame(response).sort_values(by=0)
        df = df.append(temp_df, ignore_index=True)
        time.sleep(0.2)
      try:
          df = df.rename(columns={0:'time', 1:'low', 2:'high', 3:'open', 4:'close', 5:'volume'})
          df.to_csv(f'{path}/{currency_pair}.csv', index=False)
          print(f'{currency_pair}.csv saved in {path}')

      except:
          print(f'{currency_pair} skipped.')
          continue



class TradingSystems :
    def __init__(self, cbpro_client) :
        self.client = cbpro_client

    def trade(self, action : ['buy', 'sell'], funds=float(config.SPEND_PER_TRADE)) :# , limitPrice=None, quantity=None) :
        if action == 'buy' :
            response = self.client.buy(
                            # price=limitPrice,
                            # size=self.round(quantity),
                            funds=funds,
                            order_type='market',
                            product_id=f'{config.CURRENCY_TO_BUY}-{config.CURRENCY_TO_SELL}',
                            overdraft_enabled=False
                            )
            return response['id']

        elif action == 'sell' :
            response = self.client.sell(
                            # price=limitPrice,
                            # size=self.round(quantity),
                            funds=funds,
                            order_type='market',
                            product_id=f'{config.CURRENCY_TO_BUY}-{config.CURRENCY_TO_SELL}',
                            overdraft_enabled=False
                            )
            return response['id']

    def round(self, val):
        return Decimal(int(val * Decimal(10000000)))/Decimal(10000000)

    def viewAccounts(self, accountCurrency) :
        accounts = self.client.get_accounts()
        account = list(filter(lambda x : x['currency'] == accountCurrency, accounts))[0]
        print(f"{accountCurrency} balance: {float(account['balance'])}")
        return account

    def viewOrder(self, order_id) :
        response = self.client.get_order(order_id)
        return response # {'status': response['status'], 'fee' : response['fee'], 'done_reason' : response['done_reason']}

    def getCurrentPriceOfCurrency(self) :
        tick = self.client.get_product_ticker(product_id=f'{config.CURRENCY_TO_BUY}-{config.CURRENCY_TO_SELL}')
        print(f"{config.CURRENCY_TO_BUY}-{config.CURRENCY_TO_SELL} exchange price: {float(tick['price'])}")
        return tick['price']
