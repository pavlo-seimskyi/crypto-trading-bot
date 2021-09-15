import credentials
from src import config
from src.data_scraper import data_scraper
from src import utils
import time


if __name__ == '__main__':

    # Testing NEW STRUCTURE

    # BINANCE
    end_timestamp = utils.get_current_timestamp()
    training_start_timestamp = utils.get_start_time(end_timestamp=end_timestamp, format='timestamp', mode='training')
    production_start_timestamp = utils.get_start_time(end_timestamp=end_timestamp, format='timestamp', mode='production')

    BinanceScraper = data_scraper.Binance()
    binance_latest_df = BinanceScraper.get_data(start_time=production_start_timestamp, end_time=end_timestamp, overwrite=True)
    print(binance_latest_df.head())

    # binance_historical_df = BinanceScraper.get_data(start_time=training_start_timestamp, end_time=end_timestamp, overwrite=False)
    # print(binance_historical_df.head())



    # Twitter Profiles
    end_date = utils.timestamp_to_str(end_timestamp, format='date')
    training_start_date = utils.timestamp_to_str(training_start_timestamp, format='date')
    production_start_date = utils.timestamp_to_str(production_start_timestamp, format='date')

    TwitterProfilesScraper = data_scraper.TwitterProfiles()

    latest_profile_tweets = TwitterProfilesScraper.get_data(start_date=production_start_date, end_date=end_date,
                                                            save_checkpoint=False, overwrite=True)
    print(latest_profile_tweets.head())
    #
    # historical_profile_tweets = TwitterProfilesScraper.get_data(start_date=training_start_date, end_date=end_date,
    #                                                             save_checkpoint=False, overwrite=True)
    # print(historical_profile_tweets.head())



    # Twitter Generic Tweets
    TwitterGenericScraper = data_scraper.TwitterGeneric()

    latest_generic_tweets = TwitterGenericScraper.get_data(start_date=production_start_date, end_date=end_date,
                                                            save_checkpoint=False, overwrite=True)
    print(latest_generic_tweets.head())

    # historical_generic_tweets = TwitterGenericScraper.get_data(start_date=training_start_date, end_date=end_date,
    #                                                             save_checkpoint=False, overwrite=True)
    # print(historical_generic_tweets.head())





