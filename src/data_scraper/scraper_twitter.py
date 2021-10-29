from src.data_scraper import time_helpers
import src.utils as utils
import src.config as config
import pandas as pd
import snscrape.modules.twitter as sntwitter


class Twitter:
    def load_tweets(self, search, subfolder='', filename=None, save_checkpoint=False):
        tweets_list = []
        cols = [config.MERGE_DATA_ON, 'id', 'username', 'user_verified', 'text', 'rendered_text',
                'likes', 'retweets', 'replies', 'followers', 'media', 'hashtags']
        df = pd.DataFrame(columns=cols)
        scraped_tweets_generator = sntwitter.TwitterSearchScraper(search).get_items()
        for i, tweet in enumerate(scraped_tweets_generator):
            tweets_list.append([tweet.date, tweet.id, tweet.user.username, tweet.user.verified,
                                tweet.content, tweet.renderedContent, tweet.likeCount, tweet.retweetCount,
                                tweet.replyCount, tweet.user.followersCount, tweet.media, tweet.hashtags])
            # for every 1000-th tweet or if it's the last tweet, append new data and save to prevent loss
            if save_checkpoint:
                if i / 1000 == i // 1000:
                    df = df.append(pd.DataFrame(tweets_list, columns=cols))
                    utils.save(data=df, subfolder=f'twitter/{subfolder}', filename=filename, overwrite=False)
                    tweets_list = []

        # right now, if there are less than 1000 tweets, it just does not create any dataframe
        # need to have a full dataframe in the end whether "save_checkpoint" or not
        df = df.append(pd.DataFrame(tweets_list, columns=cols))
        return df


class TwitterProfiles(Twitter):
    def __init__(self, selected_profiles: list = config.SELECTED_TWITTER_PROFILES, dev_run=True, **kwargs):
        super().__init__(**kwargs)
        self.name = "TwitterProfiles"
        self.selected_profiles = selected_profiles
        self.dev_run = dev_run

    def get_production_data(self, start_timestamp, end_timestamp, save_checkpoint, overwrite):
        data = pd.DataFrame()
        start_id = time_helpers.timestamp_to_tweet_id(start_timestamp)
        end_id = time_helpers.timestamp_to_tweet_id(end_timestamp)
        for user in self.selected_profiles:
            search = f"from:{user} since_id:{start_id} max_id:{end_id}"
            new_data = super().load_tweets(search, save_checkpoint=save_checkpoint, subfolder='selected_profiles',
                                           filename=f'{user}.csv')
            data = data.append(new_data)
        data = data.sort_values(by='id')
        utils.save(data=data, subfolder='twitter', filename='twitter_profiles.csv', overwrite=overwrite)
        return data

    def get_training_data(self, start_timestamp, end_timestamp, save_checkpoint, overwrite):
        pass

    def get_data(self, start_timestamp, end_timestamp, save_checkpoint=False, overwrite=False):
        """Load the data for selected profiles between the start and the end date. Twitter operates in UTC timezone.
            start_date | end_date : "yyyy-mm-dd" format."""
        if self.dev_run:
            return self.get_training_data(start_timestamp, end_timestamp, save_checkpoint, overwrite)
        else:
            return self.get_production_data(start_timestamp, end_timestamp, save_checkpoint, overwrite)


class TwitterGeneric(Twitter):
    def __init__(self, keywords=config.KEYWORDS, language=None, verified_only=True, dev_run=True, **kwargs):
        """
        Loads generic tweets (either all the profiles or verified only) containing provided keywords.
        :param keywords: Keywords that the tweets should contain.
        :param language: Longuage of tweets. By default, searches in all languages.
        :param verified_only: Only load tweets from verified profiles. Reduces the amount of loaded data substantially.
        """
        super().__init__(**kwargs)
        self.name = "TwitterGeneric"
        self.dev_run = dev_run
        search_terms = [f'{kw} OR' for kw in keywords[:-1]]
        search_terms.append(keywords[-1])
        search_terms = ' '.join(search_terms)
        self.search_terms = search_terms
        if language is not None:
            lang = f' lang:{language}'
        else:
            lang = ''
        self.language = lang
        if verified_only:
            verified = ' filter:verified'
        else:
            verified = ''
        self.verified_only = verified

    def get_production_data(self, start_timestamp, end_timestamp, save_checkpoint, overwrite):
        start_id = time_helpers.timestamp_to_tweet_id(start_timestamp)
        end_id = time_helpers.timestamp_to_tweet_id(end_timestamp)
        search = f"{self.search_terms} since_id:{start_id} max_id:{end_id}{self.language}{self.verified_only}"
        data = super().load_tweets(search, save_checkpoint=save_checkpoint, subfolder='generic_tweets',
                                   filename='generic_tweets.csv')
        data = data.sort_values(by='id')
        utils.save(data=data, subfolder='twitter', filename='twitter_generic.csv', overwrite=overwrite)
        data = data.sort_values(by='id')
        return data

    def get_training_data(self, start_timestamp, end_timestamp, save_checkpoint, overwrite):
        pass

    def get_data(self, start_timestamp, end_timestamp, save_checkpoint=False, overwrite=False):
        """
        Load generic tweets for specified dates containing provided keywords. Twitter operates in UTC timezone.
        :param start_date: 'yyyy-mm-dd'
        :param end_date: 'yyyy-mm-dd'
        :param save_checkpoint: for every 1000-th tweet, save the so far loaded data to prevent loss.
        :return: DataFrame
        """
        if self.dev_run:
            return self.get_training_data(start_timestamp, end_timestamp, save_checkpoint, overwrite)
        else:
            return self.get_production_data(start_timestamp, end_timestamp, save_checkpoint, overwrite)
