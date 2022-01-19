from binance import enums
from src import config
from src.data_scraper.time_helpers import EXACT_TIME_FMT

WALLET_WORTH = "wallet_worth"

class PortfolioManager:
    def __init__(self, portfolios):
        self.portfolios = portfolios

    def calculate_movements(self, predictions, price_data):
        for portfolio in self.portfolios:
            self.update_portfolio(portfolio, predictions, price_data)

    def update_portfolio(self, portfolio, predictions, price_data):
        for currency, prediction in predictions.items():
            min_amount = portfolio.client.get_minimum_amount(currency, config.CURRENCY_TO_SELL)
            if prediction == 1:
                amount = portfolio.get_available_amount(
                    currency_to_buy=currency, currency_to_sell=config.CURRENCY_TO_SELL,
                    buying=True, aggressiveness=0.10, price_data=price_data
                )
                if amount >= min_amount:
                    portfolio.buy(currency, amount, price_data)
            elif prediction == -1:
                amount = portfolio.get_available_amount(
                    currency_to_buy=currency, currency_to_sell=config.CURRENCY_TO_SELL,
                    buying=False, aggressiveness=0.10, price_data=price_data
                )
                if amount >= min_amount:
                    portfolio.sell(currency, amount, price_data)
            else:
                # print("HODL!")
                pass

    def log_wallets(self, price_data):
        timestamp = price_data["exact_time"].iloc[0].strftime(EXACT_TIME_FMT)
        wallets = {"timestamp": timestamp, WALLET_WORTH: {}}

        for portfolio in self.portfolios:
            wallets[WALLET_WORTH][portfolio.owner_name] = portfolio.get_wallet_worth(price_data)

        return wallets


class Portfolio:
    def __init__(self, owner_name, client):
        self.owner_name = owner_name
        self.client = client

    def buy(self, currency, amount, price_data):
        """
        Currently in test mode, sends and validates a request to Binance API but does not really trade.
        """
        # print(f"Buying {amount} {currency}")
        self.client.trade(
            currency_to_buy=currency,
            currency_to_sell=config.CURRENCY_TO_SELL,
            action=enums.SIDE_BUY,
            amount=amount,
            price_data=price_data
        )

    def sell(self, currency, amount, price_data):
        """
        Currently in test mode, sends and validates a request to Binance API but does not really trade.
        """
        # print(f"Selling {amount} {currency}")
        self.client.trade(
            currency_to_buy=currency,
            currency_to_sell=config.CURRENCY_TO_SELL,
            action=enums.SIDE_SELL,
            amount=amount,
            price_data=price_data
        )

    def get_wallet_worth(self, price_data):
        total_balance = 0
        balances = self.client.get_balances()
        for currency, balance in balances.items():
            if not currency == config.CURRENCY_TO_SELL:
                balance = self.convert(balance, currency, config.CURRENCY_TO_SELL, price_data)
            total_balance += balance
        return total_balance

    def get_available_amount(self, currency_to_buy, currency_to_sell, buying, aggressiveness, price_data):
        """
        Get available crypto amount to trade. It depends on available funds,
        the level of aggressiveness, and the maximum exchange precision.

        :param currency_to_buy: Crypto to buy
        :param currency_to_sell: Crypto or fiat to sell
        :param buying: If true, checks the amount of the currency to sell, otherwise, currency to buy
        :param aggressiveness: Percent of available funds to trade
        :return: Available amount to trade (in crypto)
        """
        if buying:
            funds = self.get_available_funds(currency_to_sell)  # In EUR
            funds = self.convert(funds, currency_to_sell, currency_to_buy, price_data)  # In BTC
        else:
            funds = self.get_available_funds(currency_to_buy)  # In BTC

        precision = self.client.get_amount_precision(f'{currency_to_buy}{currency_to_sell}')
        amount = round(funds * aggressiveness, precision)  # In BTC
        commission = self.client.get_commission(f'{currency_to_buy}{currency_to_sell}')

        if funds > amount * (1 + commission):
            return amount
        else:
            return 0.0

    def get_available_funds(self, currency):
        balances = self.client.get_balances()
        return balances[currency]

    def convert(self, funds, from_currency, to_currency, price_data):
        exchange_rate = self.client.get_current_exchange_rate(to_currency, from_currency, price_data=price_data)
        return funds / exchange_rate
