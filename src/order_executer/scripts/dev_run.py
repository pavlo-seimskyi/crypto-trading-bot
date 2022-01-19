import credentials
from src.data_scraper.scraper_binance import BinanceScraper
from src.api_client.api_client import BinanceBackTestClient
from src.order_executer.service.data_service import TrainingDataService
from src.order_executer.service.logger import Logger
from src.order_executer.service.order_executer import OrderExecuter
from src.order_executer.service.portfolio import Portfolio

data_service = TrainingDataService(interval_period_in_minutes=1, channels=[BinanceScraper()],
                                   start_date="2021-12-10", end_date="2021-12-13")

client = BinanceBackTestClient(api_key=credentials.BINANCE_API_KEY, api_secret=credentials.BINANCE_API_SECRET)
portfolios = [Portfolio("test", client)]
logger = Logger("logs.csv")

executer_service = OrderExecuter(data_service, portfolios, logger)
executer_service.start()
while True:
    executer_service.step()
