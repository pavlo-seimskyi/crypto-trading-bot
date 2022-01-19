from src.data_scraper import time_helpers
from src import config


class ProductionDataService:
    def __init__(self, interval_period_in_minutes, channels):
        self.interval_period_in_minutes = interval_period_in_minutes
        self.channels = {channel.name: channel for channel in channels}

    def get_data(self):
        """
        Gets data between actual timestamp and the interval_period_in_minutes.
        :return: Dictionary with data for each channel
        """
        end = time_helpers.get_current_timestamp()
        start = end - 1000 * 60 * self.interval_period_in_minutes

        return self.get_channel_data(start, end)

    def initialize(self):
        """
        Gets data between actual timestamp and the lookback configured.Used just in initialization.
        :return: Dictionary with data for each channel
        """
        end = time_helpers.get_current_timestamp()
        start = time_helpers.get_production_start_timestamp(end)
        return self.get_channel_data(start, end)

    def get_channel_data(self, start, end):
        data = {}
        for channel in self.channels.values():
            data[channel.name] = channel.get_data(start, end)
        return data


class TrainingDataService:
    def __init__(self, interval_period_in_minutes, channels, start_date, end_date):
        """
        Tries loading saved data from disk if possible. Otherwise, scrapes it first.
        The starting exact time will be 00:00 of the requested start date and 23:59 of the end date.
        :param interval_period_in_minutes: Time interval between data samples
        :param channels: Data scrapers of choice
        :param start_date: YYYY-MM-DD date written as string
        :param end_date: YYYY-MM-DD date written as string
        """
        self.interval_period_in_minutes = interval_period_in_minutes
        self.channels = {channel.name: channel for channel in channels}
        self.start_timestamp = time_helpers.str_to_timestamp(start_date, format='date')
        self.start_timestamp = time_helpers.get_start_of_the_day(self.start_timestamp)  # Start will be at 00:00

        self.end_timestamp = time_helpers.str_to_timestamp(end_date, format='date')
        self.end_timestamp = time_helpers.get_end_of_the_day(self.end_timestamp)
        self.end_timestamp = time_helpers.adjust_last_possible_timestamp(self.end_timestamp)  # End will be at 23:59

        # First timestamp
        self.last_end_timestamp = self.start_timestamp

    def initialize(self):
        """
        Gets data between the start timestamp and the lookback configured.
        :return: Dictionary with data for each channel
        """
        print("Initializing Training Data Service")
        window_after_start_time = time_helpers.add_lookback_window(self.start_timestamp)
        for channel in self.channels.values():
            channel.load_from_disk(self.start_timestamp, self.end_timestamp)

        self.last_end_timestamp = window_after_start_time

        return self.get_channel_data(self.start_timestamp, window_after_start_time)

    def get_channel_data(self, start, end):
        data = {}
        for channel in self.channels.values():
            data[channel.name] = channel.get_stored_data(start, end)
        return data

    def get_data(self):
        """
        Gets data between the start timestamp and the interval_period_in_minutes.
        :return: Dictionary with data for each channel
        """
        start = self.last_end_timestamp
        end = start + 1000 * 60 * self.interval_period_in_minutes
        self.last_end_timestamp = end
        return self.get_channel_data(start, end)


