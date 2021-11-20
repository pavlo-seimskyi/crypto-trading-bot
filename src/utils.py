import src.config as config
import os
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa


def save_data(data, dataset_path) -> None:
    """
    Save the loaded data if in development/training in parquet, partitioned by week.
    :param data: pd.DataFrame
    :param dataset_path: Scraper folder (specify as an attribute of the scraper)
    :param dataset_name: Specific dataset of the scraper (specify as an attribute of the scraper)
    :return: None
    """
    os.makedirs(dataset_path, exist_ok=True)
    table = pa.Table.from_pandas(df=data)
    pq.write_to_dataset(table, root_path=dataset_path, partition_cols=['date'])
