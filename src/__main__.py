import credentials
import src.config as config
from src.data_scraper.data_scraper import DataScraper
import time

if __name__ == '__main__':

    # Testing
    scraper = DataScraper(path=config.FOLDER_TO_SAVE)

    # Binance data
    binance = scraper.get_latest_binance_data(currency_to_buy=config.CURRENCY_TO_BUY,
                                              currency_to_sell=config.CURRENCY_TO_SELL,
                                              interval=config.INTERVAL)

    print(binance)

    # Twitter broad data from verified profiles
    # 1. Get real-time data
    df = scraper.get_twitter_data(keywords=config.KEYWORDS, production=True, save=True, verified_only=True)
    print('REAL-TIME DATA:\n', df.tail())

    # 2. Get historical data
    df = scraper.get_twitter_data(keywords=config.KEYWORDS, production=False, save=False, verified_only=True)
    print('HISTORIC DATA:\n', df.tail())

    # 3. Real-time twitter data for only selected profiles
    df = scraper.get_twitter_data(keywords=config.KEYWORDS, production=True, save=True, verified_only=True,
                                  selected_profiles=config.SELECTED_TWITTER_PROFILES)
    print('REAL-TIME DATA:\n', df.tail())

    # 4. Historical data for only selected profiles
    df = scraper.get_twitter_data(keywords=config.KEYWORDS, production=False, save=False, verified_only=True,
                                  selected_profiles=config.SELECTED_TWITTER_PROFILES)
    print('HISTORIC DATA:\n', df.tail())