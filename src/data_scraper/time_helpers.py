from typing import List

import src.config as config
import datetime as dt
from dateutil import parser
from pytz import timezone


def get_current_timestamp():
    """Timestamp in milliseconds. Will be used by all scrapers in this or another form."""
    return int(round(dt.datetime.now(dt.timezone.utc).timestamp() * 1000))


def get_training_start_timestamp(end_timestamp):
    """Gets the training starting timestamp X amount of days ago, specified in config.DAYS_BACK."""
    return end_timestamp - (1000 * 60 * 60 * 24 * config.DAYS_BACK)


def get_production_start_timestamp(end_timestamp):
    """Gets the production start timestamp X amount of minutes ago, specified in config.LATEST_DATA_LOOKBACK_MIN."""
    return end_timestamp - (1000 * 60 * config.LATEST_DATA_LOOKBACK_MIN)


def timestamp_to_datetime(timestamp):
    """Convert timestamp o datetime format."""
    if len(str(timestamp)) == 13:
        # In milliseconds
        return dt.datetime.utcfromtimestamp(int(timestamp) / 1000)
    return dt.datetime.utcfromtimestamp(int(timestamp))


def timestamp_to_str(timestamp, format: ['date', 'exact_time']):
    """
    Converts timestamp into the desired format.
    format = 'date' returns `2021-01-01` format.
    format = 'exact_time' returns `2021-01-01 00:00:00` format.
    """
    if format == 'date':
        return timestamp_to_datetime(timestamp).strftime('%Y-%m-%d')
    elif format == 'exact_time':
        return timestamp_to_datetime(timestamp).strftime('%Y-%m-%d %H:%M:%S+00:00')  # UTC
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
        return int(round(dt.datetime.strptime(string, "%Y-%m-%d").timestamp())) * 1000
    elif format == 'exact_time':
        return int(round(dt.datetime.strptime(string, "%Y-%m-%d %H:%M:%S").timestamp())) * 1000
    else:
        raise Exception('Format has to be either "date" or "exact_time".')


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
        return [[get_production_start_timestamp(start_timestamp), end_timestamp]]

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

    # Shift all start timestamps by the production lookback window
    chunks = [[get_production_start_timestamp(chunk[0]), chunk[1]] for chunk in chunks]

    # # ALTERNATIVE: Shift only the first start timestamp by the production lookback window
    # chunks[0][0] = time_helpers.get_production_start_timestamp(chunks[0][0])

    return chunks
