from src.data_scraper import time_helpers


class ProductionDataService:
    def __init__(self, interval_period_in_minutes, channels):
        self.interval_period_in_minutes = interval_period_in_minutes
        self.channels = channels

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
        for channel in self.channels:
            data[channel.name] = channel.get_data(start, end)
        return data


class TrainingDataService:
    def __init__(self, interval_period_in_minutes, channels, start_time, end_time):
        self.interval_period_in_minutes = interval_period_in_minutes
        self.channels = channels
        self.start_time = time_helpers.str_to_timestamp(start_time, format="date")
        self.end_time = time_helpers.str_to_timestamp(end_time, format="date")

        # First timestamp
        self.last_end_time = start_time

    def initialize(self):
        """
        Gets data between the start timestamp and the lookback configured.
        :return: Dictionary with data for each channel
        """
        print("Initializing Training Data Service")
        window_before_start_time = time_helpers.get_production_start_timestamp(self.start_time)
        for channel in self.channels:
            channel.load_from_disk(window_before_start_time, self.end_time)

        self.last_end_time = self.start_time

        return self.get_channel_data(window_before_start_time, self.start_time)

    def get_channel_data(self, start, end):
        data = {}
        for channel in self.channels:
            data[channel.name] = channel.get_stored_data(start, end)
        return data

    def get_data(self):
        """
        Gets data between the start timestamp and the interval_period_in_minutes.
        :return: Dictionary with data for each channel
        """
        start = self.last_end_time
        end = start + 1000 * 60 * self.interval_period_in_minutes
        self.last_end_time = end
        return self.get_channel_data(start, end)


