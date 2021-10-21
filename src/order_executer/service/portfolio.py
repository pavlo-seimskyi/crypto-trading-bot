class PortfolioManager:
    def __init__(self, portfolios):
        self.portfolios = portfolios

    def calculate_movements(self, predictions):
        for portfolio in self.portfolios:
            self.update_portfolio(portfolio, predictions)

    def update_portfolio(self, portfolio, predictions):
        for asset, prediction in predictions.items():
            if prediction == 1:
                portfolio.buy(asset)
            elif prediction == -1:
                portfolio.sell(asset)


class Portfolio:
    def __init__(self, owner_name, binance_key, binance_pass):
        self.owner_name = owner_name
        self.binance_key = binance_key
        self.binance_pass = binance_pass
        self.assets = {}

    def buy(self, asset):
        print(f"Buying {asset}")

    def sell(self, asset):
        print(f"Selling {asset}")
