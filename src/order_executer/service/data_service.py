import datetime

from src.data_scraper import time_helpers


class DataServiceBuilder:
    @staticmethod
    def build(parameters, dev_run):
        if dev_run:
            return TrainingDataService(**parameters)
        else:
            return ProductionDataService(**parameters)


class DataService:
    def __init__(self, interval_period_in_minutes, channels):
        self.interval_period_in_minutes = interval_period_in_minutes
        self.channels = channels

    def get_channel_data(self, start, end):
        data = {}
        for channel in self.channels:
            data[channel.name] = channel.get_data(start, end)
        return data


class ProductionDataService(DataService):

    def get_data(self):
        """
        Gets data between actual timestamp and the interval_period_in_minutes.
        :return: Dictionary with data for each channel
        """
        end = time_helpers.get_current_timestamp()
        start = end - 1000 * 60 * self.interval_period_in_minutes
        print(datetime.datetime.fromtimestamp(start / 1000), datetime.datetime.fromtimestamp(end / 1000))

        return self.get_channel_data(start, end)

    def initialize(self):
        """
        Gets data between actual timestamp and the lookback configured.Used just in initialization.
        :return: Dictionary with data for each channel
        """
        end = time_helpers.get_current_timestamp()
        start = time_helpers.get_production_start_timestamp(end)
        return self.get_channel_data(start, end)


class TrainingDataService(DataService):
    def __init__(self, interval_period_in_minutes, channels, start_time, end_time):
        super().__init__(interval_period_in_minutes, channels)
        self.start_time = start_time
        self.end_time = end_time

        # First timestamp
        self.last_end_time = start_time

    def get_data(self):
        """
        Gets data between the start timestamp and the interval_period_in_minutes.
        :return: Dictionary with data for each channel
        """
        start = self.last_end_time
        end = start + 1000 * 60 * self.interval_period_in_minutes

        return self.get_channel_data(start, end)

    def initialize(self):
        """
        Gets data between the start timestamp and the lookback configured.
        :return: Dictionary with data for each channel
        """
        end = self.last_end_time
        start = time_helpers.get_production_start_timestamp(end)
        return self.get_channel_data(start, end)
