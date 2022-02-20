import logging
import random

from src.feature_extractor.feature_service import FeatureService
from src.config import FEATURE_GENERATORS
from src.order_executer.service.portfolio import PortfolioManager

logger = logging.getLogger()
from flask import Flask

app = Flask(__name__)


class OrderExecuter:
    def __init__(self, data_service, portfolios, model=None, logger=None):
        self.is_active = False
        self.feature_service = FeatureService(*FEATURE_GENERATORS)
        self.data_service = data_service
        self.model = model
        self.portfolio_manager = PortfolioManager(portfolios)  # TODO Needs to be refreshed every X minutes
        self.logger = logger

    def start(self):
        # Start FeatureService
        self.feature_service.reset()
        recent_data = self.data_service.initialize()

        self.feature_service.initialize(recent_data["Binance"]) # Make it channel agnostic
        # Start logger
        if self.logger:
            self.logger.initialize()
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
            data = self.data_service.get_data()
            if len(data) == 0:
                # TODO Update this condition when multiple data inputs
                return
            self.feature_service.add_value(data["Binance"], purging=True)
            # Model will return 1, 0 or -1 if price goes above or below 1%
            predictions = {"BTC": random.randint(-1, 2)}
            price_data = data["Binance"]
            self.portfolio_manager.calculate_movements(predictions, price_data)

            if self.logger:
                self.logger.log(self.feature_service, self.portfolio_manager, price_data)

        else:
            logger.info("Service INACTIVE")
