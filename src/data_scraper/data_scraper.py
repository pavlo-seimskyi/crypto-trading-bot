import credentials
import pandas as pd
from src.api_client.api_client import BinanceClient
from src.utils import *
import os
import datetime as dt
import snscrape.modules.twitter as sntwitter
import src.config as config
from functools import partial


class DataScraper:
    def __init__(self, end_timestamp, path=config.FOLDER_TO_SAVE):
        self.path = path
        self.end_timestamp = end_timestamp
        self.end_date = timestamp_to_str(self.end_timestamp, format='date')
        self.end_exact_time = timestamp_to_str(self.end_timestamp, format='exact_time')

        self.production_start_timestamp = self.end_timestamp - (1000 * 60 * config.LATEST_DATA_LOOKBACK_MIN)
        # training start timestamp -> ms * s * m * h * d
        self.training_start_timestamp = self.end_timestamp - (1000 * 60 * 60 * 24 * config.DAYS_BACK)

        self.production_start_date = timestamp_to_str(self.production_start_timestamp, format='date')
        self.production_start_exact_time = timestamp_to_str(self.production_start_timestamp, format='exact_time')

        self.training_start_date = timestamp_to_str(self.training_start_timestamp, format='date')
        self.training_start_exact_time = timestamp_to_str(self.training_start_timestamp, format='exact_time')

    def save(self, df, subfolder, filename, merge_by: ['indexes', 'columns', None], merge_on=None):
        """Save the loaded data. If a file already exists, it will try to append to it,
        removing duplicates, and save again."""
        os.makedirs(os.path.join(self.path, subfolder), exist_ok=True)
        # print('==========\n', os.listdir(os.path.join(self.path, subfolder)))
        if filename in os.listdir(os.path.join(self.path, subfolder)):
            saved_df = pd.read_csv(os.path.join(self.path, subfolder, filename))
            print(saved_df.info())
            if merge_by == "indexes":
                # print('\n==== INDEXES ====\n')
                if not df.columns.tolist() == saved_df.columns.tolist():
                    raise Exception("Cannot merge on indexes because columns differ.")
                else:
                    print(df.info())
                    final_df = pd.merge(df, saved_df, how='outer')
                    # Make the saved
            if merge_by == "columns":
                # print('\n==== COLUMNS ====\n')
                final_df = df.merge(saved_df, how='outer', on=[merge_on])
                # print(final_df)
        else:
            final_df = df

        final_df.to_csv(os.path.join(self.path, subfolder, filename), index=False)


class Binance(DataScraper):
    def __init__(self, currency_to_buy=config.CURRENCY_TO_BUY, currency_to_sell=config.CURRENCY_TO_SELL,
                 all_currencies=config.ALL_CURRENCIES, interval=config.INTERVAL, **kwargs):
        super().__init__(**kwargs)
        self.client = BinanceClient(key=credentials.BINANCE_API_KEY, secret=credentials.BINANCE_API_SECRET)
        self.interval = interval
        self.currency_to_buy = currency_to_buy
        self.currency_to_sell = currency_to_sell
        all_currencies.remove(self.currency_to_buy)
        self.currency_pairs = [f'{self.currency_to_buy}{self.currency_to_sell}',
                               *[f'{currency}{self.currency_to_sell}' for currency in all_currencies]]

    def get_data(self, start_time, end_time, load_from_checkpoint):
        os.makedirs(f'{self.path}/binance', exist_ok=True)
        colnames = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                    'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
        df = pd.DataFrame(columns=colnames)

        for currency_pair in self.currency_pairs:
            # Check if the data already exists and continue from there
            print('==== BEFORE ====\n', start_time, end_time, '\n\n', type(start_time), type(end_time))
            if load_from_checkpoint:
                if f'{currency_pair}_{self.interval}.csv' in os.listdir(os.path.join(self.path, 'binance')):
                    test = pd.read_csv(f'{self.path}/binance/{currency_pair}_{self.interval}.csv')
                    # If the last timestamp in the saved file > specified end timestamp
                    if test.iloc[-1][f'{currency_pair}_Open time'] > end_time:
                        if test.iloc[0][f'{currency_pair}_Open time'] < start_time:
                            print('File already saved.')
                            continue
                        else:
                            end_time = int(test.iloc[0][f'{currency_pair}_Open time'])

                    # If the last timestamp in the saved file > specified start timestamp, use the df's latest one
                    if test.iloc[-1][f'{currency_pair}_Close time'] > start_time:
                        if test.iloc[0][f'{currency_pair}_Close time'] < start_time:
                            start_time = int(test.iloc[-2][f'{currency_pair}_Open time'])

                    del test
            print('==== AFTER ====\n', start_time, end_time, '\n\n', type(start_time), type(end_time))

            klines = self.client.get_historical_prices(currency_to_buy=self.currency_to_buy,
                                                       currency_to_sell=self.currency_to_sell,
                                                       interval=self.interval,
                                                       start_time=start_time,
                                                       end_time=end_time)

            temp_df = pd.DataFrame(klines, columns=colnames)
            temp_df['real time'] = temp_df['Open time'].apply(partial(timestamp_to_str, format='exact_time'))
            # Rename the columns
            temp_df = temp_df.rename(columns={f'{col}': f'{currency_pair}_{col}' for col in temp_df.columns
                                              if col != 'real time'})

            if len(temp_df) == 0:
                print(f'{currency_pair}_{self.interval} skipped.')
                continue
            else:
                super().save(df=temp_df, subfolder='binance', filename=f'{currency_pair}_{self.interval}.csv',
                             merge_by='indexes', merge_on='real time')
                # temp_df.to_csv(f'{self.path}/binance/{currency_pair}_{self.interval}.csv', index=False)
                print(f'{currency_pair}_{self.interval}.csv saved in {self.path}/binance')

            # Rename the columns
            temp_df = temp_df.rename(columns={f'{metric}': f'{currency_pair}_{metric}' for metric in temp_df.columns})
            if len(df) == 0:
                df = temp_df.copy()
            else:
                df = df.join(temp_df, how='outer')

        return df

    def get_historical_data(self, load_from_checkpoint=True):
        """Get Binance API historical exchange rates for all selected currencies.
        By default, it will try to continue from the latest available data point if the last saved timestamp is ahead
        of the timestamp specified in the config, to save time instead of loading already available data."""
        return self.get_data(start_time=self.training_start_timestamp, end_time=self.end_timestamp,
                             load_from_checkpoint=load_from_checkpoint)

    def get_latest_data(self, load_from_checkpoint=False):
        """Get Binance API real-time exchange rates for all selected currencies.
        By default, it will overwrite the saved data that overlaps with the real-time one. This way, the data is
        loaded faster in production."""
        return self.get_data(start_time=self.production_start_timestamp, end_time=self.end_timestamp,
                             load_from_checkpoint=load_from_checkpoint)


class Twitter(DataScraper):
    def load_tweets(self, search, save_checkpoint=False, subfolder='', filename=None):
        tweets_list = []
        cols = ['datetime', 'id', 'username', 'user_verified', 'text', 'renderedText',
                'likes', 'retweets', 'replies', 'media', 'hashtags']
        df = pd.DataFrame(columns=cols)
        scraped_tweets = sntwitter.TwitterSearchScraper(search).get_items()
        for i, tweet in enumerate(scraped_tweets):
            tweets_list.append([tweet.date, tweet.id, tweet.user.username, tweet.user.verified,
                                tweet.content, tweet.renderedContent, tweet.likeCount, tweet.retweetCount,
                                tweet.replyCount, tweet.media, tweet.hashtags])

            # for every 1000-th tweet, append to the dataframe and save to prevent loss
            # save anyway if it's the last tweet
            if save_checkpoint:
                if i / 1000 == i // 1000 or i + 1 == len(scraped_tweets):
                    df = df.append(pd.DataFrame(tweets_list, columns=cols))
                    super().save(df=df, subfolder=os.path.join('twitter', subfolder), filename=filename,
                                 merge_by='indexes', merge_on=None)
                    tweets_list = []

            # if it's the last tweet, combine into one DataFrame
            if not save_checkpoint and i + 1 == len(scraped_tweets):
                df = df.append(pd.DataFrame(tweets_list, columns=cols))

        return df


class TwitterProfiles(Twitter):
    def __init__(self, selected_profiles: list, **kwargs):
        super().__init__(**kwargs)
        self.selected_profiles = selected_profiles

    def get_data(self, start_date, end_date, save_checkpoint):
        """Load the data for selected profiles between the start and the end date.
        start_date | end_date : "yyyy-mm-dd" format."""
        df = pd.DataFrame()
        if start_date == end_date:
            start_date = dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.timedelta(days=1)
            start_date = start_date.strftime('%Y-%m-%d')

        for user in self.selected_profiles:
            search = f"from:{user} since:{start_date} until:{end_date}"
            new_df = super().load_tweets(search, save_checkpoint=save_checkpoint, subfolder='selected_profiles',
                                         filename=f'{user}.csv')
            df = df.append(new_df)

        return df.sort_values(by='id')

    def get_latest_data(self, save_checkpoint=True):
        """Get the real-time data. Use in production."""
        start_date = timestamp_to_str(timestamp=self.production_start_timestamp, format='date')
        end_date = timestamp_to_str(timestamp=self.end_timestamp, format='date')
        return self.get_data(start_date=start_date, end_date=end_date,
                             save_checkpoint=save_checkpoint)

    def get_historical_data(self, save_checkpoint=True):
        """Get the historical data. Use for training."""
        start_date = timestamp_to_str(timestamp=self.training_start_timestamp, format='date')
        end_date = timestamp_to_str(timestamp=self.end_timestamp, format='date')
        return self.get_data(start_date=start_date, end_date=end_date,
                             save_checkpoint=save_checkpoint)


class TwitterGeneric(Twitter):
    def __init__(self, keywords, language, verified_only, **kwargs):
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

        if language is not None:
            lang = f' lang:{language}'
        else:
            lang = ''
        if verified_only:
            verified = 'filter:verified'
        else:
            verified = ''
        self.language = lang
        self.verified_only = verified

    def get_data(self, start_date, end_date, save_checkpoint):
        """
        Load generic tweets for specified dates containing provided keywords.
        :param start_date: 'yyyy-mm-dd'
        :param end_date: 'yyyy-mm-dd'
        :param save: for every 1000-th tweet, save the so far loaded data to prevent loss.
        :return: DataFrame
        """
        if start_date == end_date:
            start_date = dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.timedelta(days=1)
            start_date = start_date.strftime('%Y-%m-%d')

        search = f"{self.search_terms} since:{start_date} until:{end_date}{self.language}{self.verified_only}"
        df = super().load_tweets(search, save_checkpoint=save_checkpoint,
                                 subfolder='generic_tweets', filename=f'generic_tweets.csv')
        return df

    def get_latest_data(self, save_checkpoint=True):
        """
        Load latest generic tweets containing provided keywords.
        :param save: for every 1000-th tweet, save the so far loaded data to prevent loss.
        :return: DataFrame
        """
        start_date = timestamp_to_str(timestamp=self.production_start_timestamp, format='date')
        end_date = timestamp_to_str(timestamp=self.end_timestamp, format='date')
        return self.get_data(start_date=start_date, end_date=end_date, save_checkpoint=save_checkpoint)

    def get_historical_data(self, save_checkpoint=True):
        """
        Load historical generic tweets containing provided keywords.
        :param save: for every 1000-th tweet, save the so far loaded data to prevent loss.
        :return: DataFrame
        """
        start_date = timestamp_to_str(timestamp=self.training_start_timestamp, format='date')
        end_date = timestamp_to_str(timestamp=self.end_timestamp, format='date')
        return self.get_data(start_date=start_date, end_date=end_date, save_checkpoint=save_checkpoint)


class Trends(DataScraper):
    def setup_proxies(self):
        pass

    def get_historical_data(self):
        pass

    def get_latest_data(self):
        pass
