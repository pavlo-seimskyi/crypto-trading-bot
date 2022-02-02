from unittest import TestCase

from src.order_executer.service.logger import Logger


class TestLogger(TestCase):

    def test_loading_wallets_fromn_owner(self):
        logger = Logger("test")
        logger.portfolio_file = open("resources/portfolio.log")
        wallet_history = logger.load_owner_wallet("test")
        assert wallet_history.wallet_worth.iloc[0] == 2040.0248