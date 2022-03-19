import os
from dateutil import parser
import pyarrow.parquet as pq
import pyarrow as pa
from src.data_scraper import time_helpers


def dataset_stored(dataset_path, start_time, end_time) -> bool:
    """
    Checks availability of stored data on disk for selected start and end dates.
    The data is available if requested start date >= saved start date and requested end date >= saved end date.
    """
    if os.path.exists(dataset_path):
        available_dates = os.listdir(dataset_path)
        available_dates = [date.split('date=')[-1] for date in available_dates if not date.startswith('.')]
        available_dates = [parser.parse(date).date() for date in available_dates]

        start_date = time_helpers.timestamp_to_datetime(start_time).date()
        end_date = time_helpers.timestamp_to_datetime(end_time).date()

        return start_date >= min(available_dates) and end_date <= max(available_dates)
    else:
        return False


def save_data(data, dataset_path) -> None:
    """
    Save the loaded data if in development/training in parquet, partitioned by day.
    :param data: pd.DataFrame
    :param dataset_path: Scraper folder (specify as an attribute of the scraper)
    :return: None
    """
    os.makedirs(dataset_path, exist_ok=True)
    table = pa.Table.from_pandas(df=data)
    pq.write_to_dataset(table, root_path=dataset_path, partition_cols=['date'])
