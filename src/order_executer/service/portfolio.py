from src.api_client.api_client import BinanceClient, BinanceBackTestClient
from binance import enums
from src import config


class PortfolioManager:
    def __init__(self, portfolios):
        self.portfolios = portfolios

    def calculate_movements(self, predictions, data):
        for portfolio in self.portfolios:
            self.update_portfolio(portfolio, predictions, data)

    def update_portfolio(self, portfolio, predictions, data):
        for currency, prediction in predictions.items():
            min_amount = portfolio.client.get_minimum_amount(currency, config.CURRENCY_TO_SELL)
            if prediction == 1:
                amount = portfolio.get_available_amount(currency=currency, buying=True,  aggressiveness=0.10, data=data)
                if amount >= min_amount:
                    portfolio.buy(currency, amount, data)
            elif prediction == -1:
                amount = portfolio.get_available_amount(currency=currency, buying=False, aggressiveness=0.10, data=data)
                if amount >= min_amount:
                    portfolio.sell(currency, amount, data)
            else:
                print("HODL!")

    def update_wallet_worth(self, data):
        for portfolio in self.portfolios:
            portfolio.update_wallet_worth(data)


class Portfolio:
    def __init__(self, owner_name, client=BinanceClient, api_key=None, api_secret=None):
        self.owner_name = owner_name
        self.client = client(api_key=api_key, api_secret=api_secret)
        self.wallet_worth_history = []

    def buy(self, currency, amount, data):
        """
        Currently in test mode, sends and validates a request to Binance API but does not really trade.
        """
        print(f"Buying {amount} {currency}")
        self.client.trade(
            currency_to_buy=currency,
            currency_to_sell=config.CURRENCY_TO_SELL,
            action=enums.SIDE_BUY,
            amount=amount,
            data=data
        )

    def sell(self, currency, amount, data):
        """
        Currently in test mode, sends and validates a request to Binance API but does not really trade.
        """
        print(f"Selling {amount} {currency}")
        self.client.trade(
            currency_to_buy=currency,
            currency_to_sell=config.CURRENCY_TO_SELL,
            action=enums.SIDE_SELL,
            amount=amount,
            data=data
        )

    def update_wallet_worth(self, data):
        total_balance = 0
        balances = self.client.get_balances()
        for currency, balance in balances.iterrows():
            balance = balance['free']
            if not currency == config.CURRENCY_TO_SELL:
                balance = self.convert(balance, currency, config.CURRENCY_TO_SELL, data)
            total_balance += balance
        self.wallet_worth_history.append(total_balance)

    def get_available_amount(self, currency, buying, aggressiveness, data):
        """
        Get available crypto amount to trade. It depends on available funds,
        the level of aggressiveness, and the maximum exchange precision.

        :param currency: Crypto to buy/sell
        :param buying: If true, checks the amount of the currency to sell, otherwise, currency to buy
        :param aggressiveness: Percent of available funds to trade
        :return: Available amount to trade (in crypto)
        """
        if buying:
            funds = self.get_available_funds(config.CURRENCY_TO_SELL)  # In EUR
            funds = self.convert(funds, config.CURRENCY_TO_SELL, currency, data)  # In BTC
        else:
            funds = self.get_available_funds(currency)  # In BTC

        precision = self.client.get_amount_precision(f'{currency}{config.CURRENCY_TO_SELL}')
        amount = round(funds * aggressiveness, precision)  # In BTC
        commission = self.client.get_commission(f'{currency}{config.CURRENCY_TO_SELL}')

        if funds > amount * (1 + commission):
            return amount
        else:
            return 0.0

    def get_available_funds(self, currency):
        balances = self.client.get_balances()
        return balances['free'][currency]

    def convert(self, funds, from_currency, to_currency, data):
        exchange_rate = self.client.get_current_exchange_rate(to_currency, from_currency, data=data)
        return funds / exchange_rate

    def calculate_returns(self):
        return (self.wallet_worth_history[-1] - self.wallet_worth_history[0]) / self.wallet_worth_history[0]

    def calculate_max_drawdown(self):
        return (min(self.wallet_worth_history) - max(self.wallet_worth_history)) / max(self.wallet_worth_history)


