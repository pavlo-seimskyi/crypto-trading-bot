from src.data_scraper.scraper_binance import BinanceScraper
from src.data_scraper import time_helpers


if __name__ == '__main__':
    # Initializing the timestamps to use in all data scrapers
    end_timestamp = time_helpers.get_current_timestamp()
    training_start_timestamp = time_helpers.get_training_start_timestamp(end_timestamp=end_timestamp)
    production_start_timestamp = time_helpers.get_production_start_timestamp(end_timestamp=end_timestamp)

    # Exchange data
    # Dev mode
    # scraper = BinanceScraper()
    # scraper.load_from_disk(training_start_timestamp, end_timestamp)
    # training_data = scraper.load_from_disk(training_start_timestamp, end_timestamp)
    # print(training_data.tail())
    #
    # Prod mode
    scraper = BinanceScraper()
    prod_data = scraper.scrape_data(production_start_timestamp, end_timestamp)
    print(prod_data.tail())












