import src.config as config
import datetime as dt
from dateutil import parser
from pytz import timezone
import os
os.environ['TZ'] = 'UTC'  # Set the default timezone to UTC

DATE_FMT = '%Y-%m-%d'
EXACT_TIME_FMT = "%Y-%m-%d %H:%M:%S"

def get_current_timestamp():
    """Timestamp in milliseconds. Will be used by all scrapers in this or another form."""
    return datetime_to_timestamp(dt.datetime.now())


def get_production_start_timestamp(end_timestamp):
    """Gets the production start timestamp X amount of minutes ago, specified in config.LATEST_DATA_LOOKBACK_MIN."""
    return end_timestamp - (1000 * 60 * config.LATEST_DATA_LOOKBACK_MIN)


def timestamp_to_datetime(timestamp):
    """Convert timestamp o datetime format."""
    if len(str(timestamp)) == 13:
        # In milliseconds
        return dt.datetime.fromtimestamp(int(timestamp) / 1000)
    return dt.datetime.fromtimestamp(int(timestamp))


def timestamp_to_str(timestamp, format: ['date', 'exact_time']):
    """
    Converts timestamp into the desired format.
    format = 'date' returns `2021-01-01` format.
    format = 'exact_time' returns `2021-01-01 00:00:00` format.
    """
    if format == 'date':
        return timestamp_to_datetime(timestamp).strftime(DATE_FMT)
    elif format == 'exact_time':
        return timestamp_to_datetime(timestamp).strftime(EXACT_TIME_FMT)  # UTC
    else:
        raise Exception('Format has to be either "date" or "exact_time".')


def timestamp_utc_to_cet(datetime):
    """
    Twitter API returns datetime in UTC format by default. Use this function to convert UTC to CET time for convenience
    if needed. Not necessary as right now we use UTC timezone everywhere.
    """
    utc_datetime = parser.parse(str(datetime))
    cet_datetime = utc_datetime.astimezone(timezone('CET'))
    return cet_datetime


def timestamp_to_tweet_id(timestamp):
    """
    Converts the current timestamp into the needed tweet_id. Used to find tweets for very specific time frames and
    make the data loading in production much faster. Twitter uses UTC timezone.
    """
    if timestamp <= 1288834974657:
        raise ValueError("Date is too early (before snowflake implementation)")
    return (timestamp - 1288834974657) << 22


def str_to_timestamp(string, format: ['date', 'exact_time']):
    """Convert string like '2021-01-01' or '2021-01-01 00:00:00' into a timestamp."""
    if format == 'date':
        return int(round(dt.datetime.strptime(string, DATE_FMT).timestamp())) * 1000
    elif format == 'exact_time':
        return int(round(dt.datetime.strptime(string, EXACT_TIME_FMT).timestamp())) * 1000
    else:
        raise Exception('Format has to be either "date" or "exact_time".')


def get_start_of_the_day(timestamp):
    """
    Replace the time of the provided timestamp with 00:00:00.
    """
    datetime = timestamp_to_datetime(timestamp)
    day_start_datetime = datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    return datetime_to_timestamp(day_start_datetime)


def get_end_of_the_day(timestamp):
    """
    Get the 23:59:00 time of the day of the timestamp.
    """
    datetime = timestamp_to_datetime(timestamp)
    day_end_datetime = datetime.replace(hour=23, minute=59, second=0, microsecond=0)
    return datetime_to_timestamp(day_end_datetime)


def adjust_last_possible_timestamp(timestamp):
    """
    Make any last possible timestamp 23:59 of yesterday.
    """
    last_possible_timestamp = get_end_of_the_day(timestamp - 24 * 60 * 60 * 1000)
    if timestamp > last_possible_timestamp:
        timestamp = last_possible_timestamp
    return timestamp


def datetime_to_timestamp(datetime):
    """
    Convert a datetime object to timestamp in milliseconds.
    """
    return int(round(datetime.timestamp() * 1000))


def slice_timestamps_in_chunks(start_timestamp, end_timestamp):
    """
    Slice the full timeframe between start and end timestamps into weekly chunks.
    The purpose is to avoid API crashes when loading large timeframes of data.
    If the total timeframe does not sum up to a round number of weeks, the last week is kept as it is.
    All starting timestamps in chunks are shifted by the production lookback window.
    :param start_timestamp: timestamp in ms
    :param end_timestamp: timestamp in ms
    :return: [[chunk_start, chunk_end], [chunk_start, chunk_end], ...]
    """
    one_week_ms = 1000 * 60 * 60 * 24 * 7  # ms * s * m * h * d
    full_weeks = (end_timestamp - start_timestamp) // one_week_ms
    total_weeks = (end_timestamp - start_timestamp) / one_week_ms

    # If total time frame is less than one week, return the original timestamps with a lookback window
    if total_weeks < 1:
        return [[start_timestamp, end_timestamp]]

    # Split complete weeks into one-week-chunks
    chunks = []
    for week in range(full_weeks):
        chunk_start = start_timestamp + (week * one_week_ms)
        chunk_end = chunk_start + one_week_ms
        chunks.append([chunk_start, chunk_end])

    # Append last incomplete week
    if not full_weeks == total_weeks:
        last_chunk_start = chunks[-1][-1]
        last_chunk_end = end_timestamp
        chunks.append([last_chunk_start, last_chunk_end])

    return chunks


def get_lookback_window():
    return 1000 * 60 * config.LATEST_DATA_LOOKBACK_MIN