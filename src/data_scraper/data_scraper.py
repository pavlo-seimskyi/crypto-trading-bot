import credentials
import pandas as pd
from src.api_client.api_client import BinanceClient
import os
import datetime as dt
import snscrape.modules.twitter as sntwitter
import src.config as config
from functools import partial


class DataScraper:
    def __init__(self, path):
        self.path = path
        self.end_timestamp = self.get_current_timestamp()
        self.production_start_timestamp = self.end_timestamp - (1000 * 60 * config.LATEST_DATA_LOOKBACK_MIN)
        self.training_start_timestamp = self.end_timestamp - (1000 * 60 * 60 * 24 * config.DAYS_BACK) # ms * s * m * h * d
        self.end_datetime = self.timestamp_to_datetime(self.end_timestamp)
        self.production_start_datetime = self.timestamp_to_datetime(self.production_start_timestamp)
        self.training_start_datetime = self.timestamp_to_datetime(self.training_start_timestamp)

    @staticmethod
    def get_current_timestamp():
        return int(round(dt.datetime.now(dt.timezone.utc).timestamp() * 1000))

    @staticmethod
    def timestamp_to_datetime(timestamp):
        return dt.datetime.utcfromtimestamp(timestamp / 1000)

    @staticmethod
    def timestamp_to_str(timestamp, with_time):
        if with_time:
            return dt.datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return dt.datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')

    def get_historical_binance_data(self, currency_to_buy, currency_to_sell, all_currencies, interval):
        os.makedirs(f'{self.path}/binance', exist_ok=True)
        client = BinanceClient(key=credentials.BINANCE_API_KEY, secret=credentials.BINANCE_API_SECRET)

        colnames = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                    'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']

        all_currencies.remove(currency_to_buy)
        currency_pairs = [f'{currency_to_buy}{currency_to_sell}',
                          *[f'{currency}{currency_to_sell}' for currency in all_currencies]]

        for currency_pair in currency_pairs:
            klines = client.get_historical_prices(currency_to_buy=currency_to_buy,
                                                  currency_to_sell=currency_to_sell,
                                                  interval=interval,
                                                  start_time=self.training_start_timestamp,
                                                  end_time=self.end_timestamp)

            df = pd.DataFrame(klines, columns=colnames)
            df['real time'] = df['Open time'].apply(partial(self.timestamp_to_str, with_time=True))
            try:
                df.to_csv(f'{self.path}/binance/{currency_pair}_{interval}.csv', index=False)
                print(f'{currency_pair}_{interval}.csv saved in {self.path}/binance')

            except:
                print(f'{currency_pair}_{interval} skipped.')
                continue

    def get_latest_binance_data(self, currency_to_buy, currency_to_sell, interval):
        client = BinanceClient(key=credentials.BINANCE_API_KEY, secret=credentials.BINANCE_API_SECRET)
        colnames = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                    'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
        klines = client.get_latest_prices(currency_to_buy=currency_to_buy,
                                          currency_to_sell=currency_to_sell,
                                          interval=interval,
                                          start_time=self.production_start_timestamp,
                                          end_time=self.end_timestamp)
        df = pd.DataFrame(klines, columns=colnames)
        df['real time'] = df['Open time'].apply(partial(self.timestamp_to_str, with_time=True))
        return df

    def get_twitter_data(self, keywords, verified_only, production, save,
                         limit=None, selected_profiles=None, language='en'):
        '''start_date | end_date : "yyyy-mm-dd" format.'''

        os.makedirs(f'{self.path}/twitter', exist_ok=True)

        # Creating list to append tweet data to
        tweets_list = []

        cols = ['datetime', 'id', 'username', 'user_verified', 'text', 'renderedText',
                'likes', 'retweets', 'replies', 'media', 'hashtags']

        all_tweets = pd.DataFrame(columns=cols)

        search_terms = [f'{kw} OR' for kw in keywords[:-1]]
        search_terms.append(keywords[-1])
        search_terms = ' '.join(search_terms)

        end_date = self.timestamp_to_str(timestamp=self.end_timestamp, with_time=False)

        if production:
            start_date = self.timestamp_to_str(timestamp=self.production_start_timestamp, with_time=False)
            if start_date == end_date:
                start_date = dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.timedelta(days=1)
                start_date = start_date.strftime('%Y-%m-%d')
        else:
            start_date = self.timestamp_to_str(timestamp=self.training_start_timestamp, with_time=False)

        if language is not None:
            lang = f' lang:{language}'
        else:
            lang = ''
        if verified_only:
            verified = ' filter:verified'
            name = 'verified_tweets'
        else:
            verified = ''
            name = 'all_tweets'
        search = f"{search_terms} since:{start_date} until:{end_date}{lang}{verified}"
        print(search)

        if selected_profiles is None:
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search).get_items()):
                if limit is not None:
                    # stop at this point
                    if i > limit:
                        break

                tweets_list.append([tweet.date, tweet.id, tweet.user.username, tweet.user.verified,
                                    tweet.content, tweet.renderedContent,
                                    tweet.likeCount, tweet.retweetCount, tweet.replyCount,
                                    tweet.media, tweet.hashtags])

                if save:
                    # for every n-th tweet, append to the dataframe and save to prevent loss
                    if i / 1000 == i // 1000:
                        if len(df) == 0:
                            df = pd.DataFrame(tweets_list, columns=cols)
                        else:
                            df = df.append(pd.DataFrame(tweets_list, columns=cols))
                        df.to_csv(f'{self.path}/twitter/{name}.csv', index=False)
                        tweets_list = []
                else:
                    df = pd.DataFrame(tweets_list, columns=cols)

            return df

        else:
            for user in selected_profiles:
                search = f"from:{user} since:{start_date} until:{end_date}"
                for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search).get_items()):
                    tweets_list.append([tweet.date, tweet.id, tweet.user.username, tweet.user.verified,
                                        tweet.content, tweet.renderedContent,
                                        tweet.likeCount, tweet.retweetCount, tweet.replyCount,
                                        tweet.media, tweet.hashtags])

                df = df.append(pd.DataFrame(tweets_list, columns=cols))
                tweets_list = []

            df.to_csv('../data/all_tweets/sel_prof_twitter.csv', index=False)

    def setup_proxies(self):
        pass

    def get_historical_google_trends_data(self):
        pass

    def get_latest_google_trends_data(self):
        pass
