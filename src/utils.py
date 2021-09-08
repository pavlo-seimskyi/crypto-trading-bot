import src.config as config
import datetime as dt


def get_current_timestamp():
    return int(round(dt.datetime.now(dt.timezone.utc).timestamp() * 1000))

def timestamp_to_datetime(timestamp):
    return dt.datetime.utcfromtimestamp(timestamp / 1000)

def timestamp_to_str(timestamp, format: ['date', 'exact_time']):
    if format == 'date':
        return dt.datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
    elif format == 'exact_time':
        return dt.datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    else:
        raise Exception('Format has to be either "date" or "exact_time".')