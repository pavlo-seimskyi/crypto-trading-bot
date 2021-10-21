import logging
import random

from src.data_scraper.data_scraper import Binance
from src.feature_extractor.feature_service import FeatureService
from src.config import FEATURE_GENERATORS
from src.order_executer.service.data_service import DataServiceBuilder
from src.order_executer.service.portfolio import Portfolio, PortfolioManager

logger = logging.getLogger()
from flask import Flask

app = Flask(__name__)


class OrderExecuter:
    def __init__(self, dev_run, portfolios):
        self.is_active = False
        self.feature_service = FeatureService(*FEATURE_GENERATORS)
        self.data_service = DataServiceBuilder.build(
            parameters={"interval_period_in_minutes": 1, "channels": [Binance(dev_run=dev_run),
                                                                      ]}, dev_run=False)
        self.model = None
        self.portfolio_manager = PortfolioManager(portfolios)  # TODO Needs to be refreshed every X minutes

    def start(self):
        # Start FeatureService
        self.feature_service.reset()
        recent_data = self.data_service.initialize()

        self.feature_service.initialize(recent_data["Binance"]) # Make it channel agnostic
        # Load Model
        # self.model = Model.load(model_object)
        self.set_active()

    def close(self):
        self.feature_service.reset()
        self.set_inactive()

    def set_active(self):
        logger.info("Setting service [ACTIVE]")
        self.is_active = True

    def set_inactive(self):
        logger.info("Setting service [INACTIVE]")
        self.is_active = False

    def step(self):
        if self.is_active:
            price_data = self.data_service.get_data()["Binance"]
            if len(price_data) == 0:
                # TODO Update this condition when multiple data inputs
                return
            self.feature_service.add_value(price_data, purging=True)
            print(self.feature_service.status)
            # Model will return 1, 0 or -1 if price goes above or below 1%
            predictions = {"BTCEUR": random.randint(0, 1)}
            self.portfolio_manager.calculate_movements(predictions)

        else:
            logger.info("Service INACTIVE")
