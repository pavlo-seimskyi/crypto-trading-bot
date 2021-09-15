import credentials
import pandas as pd
from src.api_client.api_client import BinanceClient
from src import utils
import os
import datetime as dt
import snscrape.modules.twitter as sntwitter
import src.config as config
from functools import partial


class Binance:
    def __init__(self, currency_to_buy=config.CURRENCY_TO_BUY, currency_to_sell=config.CURRENCY_TO_SELL,
                 all_currencies=config.ALL_CURRENCIES, interval=config.INTERVAL, **kwargs):
        os.makedirs(f'{config.FOLDER_TO_SAVE}/binance', exist_ok=True)
        self.client = BinanceClient(key=credentials.BINANCE_API_KEY, secret=credentials.BINANCE_API_SECRET)
        self.interval = interval
        self.currency_to_buy = currency_to_buy
        self.currency_to_sell = currency_to_sell
        all_currencies.remove(self.currency_to_buy)
        self.currency_pairs = [f'{self.currency_to_buy}{self.currency_to_sell}',
                               *[f'{currency}{self.currency_to_sell}' for currency in all_currencies]]

    def get_checkpoint_timestamps(self, currency_pair, start_time, end_time):
        filename = f'{currency_pair}_{self.interval}.csv'
        exact_start_time = utils.timestamp_to_str(start_time, format='exact_time')
        exact_end_time = utils.timestamp_to_str(end_time, format='exact_time')
        start_time, end_time = utils.load_from_checkpoint(subfolder='binance', filename=filename,
                                                          start_time=exact_start_time,
                                                          end_time=exact_end_time)
        start_time = utils.str_to_timestamp(start_time, format='exact_time')
        end_time = utils.str_to_timestamp(end_time, format='exact_time')
        return end_time, start_time

    def get_data(self, start_time, end_time, load_from_checkpoint=False, overwrite=False):
        """Get Binance API exchange rates for all selected currencies.
        By default, it will try to continue from the latest available data point if the last saved timestamp is ahead
        of the timestamp specified in the config, to save time instead of loading already available data."""
        colnames = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                    'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
        df = pd.DataFrame(columns=colnames)

        for currency_pair in self.currency_pairs:
            # Check if the data already exists and continue from there
            if load_from_checkpoint:
                print('==== BEFORE ====\n', start_time, end_time, '\n\n', type(start_time), type(end_time))
                end_time, start_time = self.get_checkpoint_timestamps(currency_pair, start_time, end_time)
                print('==== AFTER ====\n', start_time, end_time, '\n\n', type(start_time), type(end_time))

            klines = self.client.get_exchange_rates(
                currency_to_buy=self.currency_to_buy, currency_to_sell=self.currency_to_sell,
                interval=self.interval, start_time=start_time, end_time=end_time)

            temp_df = pd.DataFrame(klines, columns=colnames)
            temp_df[config.MERGE_DATA_ON] = temp_df['Open time'].apply(partial(utils.timestamp_to_str, format='exact_time'))

            # Rename the columns, except for merger column
            temp_df = temp_df.rename(columns={f'{col}': f'{currency_pair}_{col}' for col in temp_df.columns
                                              if col != config.MERGE_DATA_ON})

            if len(temp_df) == 0:
                print(f'{currency_pair}_{self.interval} skipped.')

            if len(df) == 0:
                df = temp_df.copy()
            else:
                # print('=== DF===========\n', df, '\n', df.info(), '\n===========\n')
                # print('=== TEMP DF =====\n', temp_df, '\n', temp_df.info(), '\n===========\n')
                df = df.merge(temp_df, how='outer', on=config.MERGE_DATA_ON)

        utils.save(data=df, subfolder='binance', filename=f'binance_{self.interval}.csv', overwrite=overwrite)

        return df


class Twitter:
    def load_tweets(self, search, subfolder='', filename=None, save_checkpoint=False):
        tweets_list = []
        cols = [config.MERGE_DATA_ON, 'id', 'username', 'user_verified', 'text', 'renderedText',
                'likes', 'retweets', 'replies', 'media', 'hashtags']
        df = pd.DataFrame(columns=cols)
        scraped_tweets_generator = sntwitter.TwitterSearchScraper(search).get_items()
        for i, tweet in enumerate(scraped_tweets_generator):
            tweets_list.append([tweet.date, tweet.id, tweet.user.username, tweet.user.verified,
                                tweet.content, tweet.renderedContent, tweet.likeCount, tweet.retweetCount,
                                tweet.replyCount, tweet.media, tweet.hashtags])
            # for every 1000-th tweet or if it's the last tweet, append new data and save to prevent loss
            if save_checkpoint:
                if i / 1000 == i // 1000:
                    df = df.append(pd.DataFrame(tweets_list, columns=cols))
                    utils.save(data=df, subfolder=f'twitter/{subfolder}', filename=filename, overwrite=False)
                    tweets_list = []
        return df

    def adjust_start_date(self, start_date, end_date):
        """If the start date is same as end date, it will adjust it by subtracting 1 day from the start date."""
        if start_date == end_date:
            start_date = dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.timedelta(days=1)
            return start_date.strftime('%Y-%m-%d')
        else:
            return start_date


class TwitterProfiles(Twitter):
    def __init__(self, selected_profiles: list = config.SELECTED_TWITTER_PROFILES, **kwargs):
        super().__init__(**kwargs)
        self.selected_profiles = selected_profiles

    def get_data(self, start_date, end_date, save_checkpoint, overwrite):
        """Load the data for selected profiles between the start and the end date.
        start_date | end_date : "yyyy-mm-dd" format."""
        start_date = super().adjust_start_date(start_date=start_date, end_date=end_date)

        data = pd.DataFrame()
        for user in self.selected_profiles:
            search = f"from:{user} since:{start_date} until:{end_date}"
            print(search)
            new_data = super().load_tweets(search, save_checkpoint=save_checkpoint, subfolder='selected_profiles',
                                           filename=f'{user}.csv')
            data = data.append(new_data)
        data = data.sort_values(by='id')
        utils.save(data=data, subfolder='twitter', filename='twitter_profiles', overwrite=overwrite)

        return data


class TwitterGeneric(Twitter):
    def __init__(self, keywords=config.KEYWORDS, language=None, verified_only=True, **kwargs):
        """
        Loads generic tweets (either all the profiles or verified only) containing provided keywords.
        :param keywords: Keywords that the tweets should contain.
        :param language: Longuage of tweets. By default, searches in all languages.
        :param verified_only: Only load tweets from verified profiles. Reduces the amount of loaded data substantially.
        """
        super().__init__(**kwargs)
        search_terms = [f'{kw} OR' for kw in keywords[:-1]]
        search_terms.append(keywords[-1])
        search_terms = ' '.join(search_terms)
        self.search_terms = search_terms

        if language is not None: lang = f' lang:{language}'
        else: lang = ''
        self.language = lang

        if verified_only: verified = ' filter:verified'
        else: verified = ''
        self.verified_only = verified

    def get_data(self, start_date, end_date, save_checkpoint, overwrite):
        """
        Load generic tweets for specified dates containing provided keywords.
        :param start_date: 'yyyy-mm-dd'
        :param end_date: 'yyyy-mm-dd'
        :param save_checkpoint: for every 1000-th tweet, save the so far loaded data to prevent loss.
        :return: DataFrame
        """
        start_date = super().adjust_start_date(start_date=start_date, end_date=end_date)
        search = f"{self.search_terms} since:{start_date} until:{end_date}{self.language}{self.verified_only}"
        print(search)
        data = super().load_tweets(search, save_checkpoint=save_checkpoint, subfolder='generic_tweets', filename='generic_tweets.csv')
        utils.save(data=data, subfolder='twitter', filename='twitter_generic', overwrite=overwrite)
        return data


class Trends:
    def setup_proxies(self):
        pass

    def get_historical_data(self):
        pass

    def get_latest_data(self):
        pass
