import credentials
from src import config
from src.data_scraper import data_scraper
from src import utils
import time


if __name__ == '__main__':

    # Testing NEW STRUCTURE

    # Initializing the timestamps to use in all data scrapers
    end_timestamp = utils.get_current_timestamp()
    training_start_timestamp = utils.get_start_time(end_timestamp=end_timestamp, format='timestamp', mode='training')
    production_start_timestamp = utils.get_start_time(end_timestamp=end_timestamp, format='timestamp', mode='production')

    end_date = utils.timestamp_to_str(end_timestamp, format='date')
    training_start_date = utils.timestamp_to_str(training_start_timestamp, format='date')
    production_start_date = utils.timestamp_to_str(production_start_timestamp, format='date')

    # # BINANCE

    # BinanceScraper = data_scraper.Binance()
    # binance_latest_df = BinanceScraper.get_data(start_time=production_start_timestamp, end_time=end_timestamp, overwrite=True)
    # print(binance_latest_df.head())
    #
    # # binance_historical_df = BinanceScraper.get_data(start_time=training_start_timestamp, end_time=end_timestamp, overwrite=False)
    # # print(binance_historical_df.head())
    #
    #
    # # Twitter Profiles
    #
    # TwitterProfilesScraper = data_scraper.TwitterProfiles()
    #
    # latest_profile_tweets = TwitterProfilesScraper.get_data(start_date=production_start_date, end_date=end_date,
    #                                                         save_checkpoint=False, overwrite=True)
    # print(latest_profile_tweets.head())
    # #
    # # historical_profile_tweets = TwitterProfilesScraper.get_data(start_date=training_start_date, end_date=end_date,
    # #                                                             save_checkpoint=False, overwrite=True)
    # # print(historical_profile_tweets.head())
    #
    #
    # # Twitter Generic Tweets
    # TwitterGenericScraper = data_scraper.TwitterGeneric()
    #
    # latest_generic_tweets = TwitterGenericScraper.get_data(start_date=production_start_date, end_date=end_date,
    #                                                         save_checkpoint=False, overwrite=True)
    # print(latest_generic_tweets.head())
    #
    # # historical_generic_tweets = TwitterGenericScraper.get_data(start_date=training_start_date, end_date=end_date,
    # #                                                             save_checkpoint=False, overwrite=True)
    # # print(historical_generic_tweets.head())


    # Testing loading Twitter data with id -> timestamp

    TwitterGenericScraper = data_scraper.TwitterGeneric()

    historical_generic_tweets = TwitterGenericScraper.get_data(start_timestamp=training_start_timestamp,
                                                           end_timestamp=end_timestamp,
                                                           save_checkpoint=False, overwrite=True)
    print(historical_generic_tweets.tail())

    latest_generic_tweets = TwitterGenericScraper.get_data(start_timestamp=production_start_timestamp,
                                                           end_timestamp=end_timestamp,
                                                           save_checkpoint=False, overwrite=True)
    print(latest_generic_tweets.tail())


    # Twitter Profiles with timestamp
    TwitterProfilesScraper = data_scraper.TwitterProfiles()

    latest_profile_tweets = TwitterProfilesScraper.get_data(start_timestamp=production_start_timestamp, end_timestamp=end_timestamp,
                                                            save_checkpoint=False, overwrite=True)
    print(latest_profile_tweets.tail())

    historical_profile_tweets = TwitterProfilesScraper.get_data(start_timestamp=training_start_timestamp,
                                                            end_timestamp=end_timestamp,
                                                            save_checkpoint=False, overwrite=True)
    print(historical_profile_tweets.tail())








