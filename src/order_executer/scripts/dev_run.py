from src.data_scraper.scraper_binance import BinanceScraper
from src.order_executer.service.data_service import TrainingDataService
from src.order_executer.service.logger import Logger
from src.order_executer.service.order_executer import OrderExecuter
from src.order_executer.service.portfolio import Portfolio

data_service = TrainingDataService(interval_period_in_minutes=1, channels=[BinanceScraper()],
                                   start_date="2020-01-01", end_date="2021-12-13")

portfolios = [Portfolio("test", "key", "pass")]
logger = Logger("logs.csv")

executer_service = OrderExecuter(data_service, portfolios, logger)
executer_service.start()
while True:
    executer_service.step()
