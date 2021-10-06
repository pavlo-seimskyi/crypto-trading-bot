import src.config as config
import os
import pandas as pd


def save(data, subfolder, filename, overwrite=False):
    """WIP. Save the loaded data. If a file already exists, it will try to append to it by columns or indexes.
    If duplicates exist, it will only preserve the last, remove the previous ones, and save the file again."""
    os.makedirs(os.path.join(config.FOLDER_TO_SAVE, subfolder), exist_ok=True)
    if overwrite:
        data.to_csv(os.path.join(config.FOLDER_TO_SAVE, subfolder, filename), index=False)
    else:
        if filename in os.listdir(os.path.join(config.FOLDER_TO_SAVE, subfolder)):
            saved_data = pd.read_csv(os.path.join(config.FOLDER_TO_SAVE, subfolder, filename))
            data = data.astype(object)
            saved_data = saved_data.astype(object)
            if sorted(data.columns.tolist()) == sorted(saved_data.columns.tolist()):
                data = pd.merge(data, saved_data, how='outer', on=data.columns.tolist())
            else:
                # Find common columns to merge on
                common_cols = data.columns[data.columns.isin(saved_data.columns)].tolist()
                data = data.merge(saved_data, how='outer', on=common_cols, copy=False)

        data = data.groupby(config.MERGE_DATA_ON).last().reset_index()
        data = data.sort_values(by=config.MERGE_DATA_ON)
        data.to_csv(os.path.join(config.FOLDER_TO_SAVE, subfolder, filename), index=False)


def load_from_checkpoint(subfolder, filename, start_time, end_time):
    """WIP"""
    if filename in os.listdir(os.path.join(config.FOLDER_TO_SAVE, subfolder)):
        test = pd.read_csv(f'{config.FOLDER_TO_SAVE}/{subfolder}/{filename}')
        # If the last timestamp in the saved file > specified end timestamp
        if test['exact_time'].astype('datetime64[ns]').iloc[-1] > end_time:
            if test.iloc[0]['exact_time'] < start_time:
                print('File already saved.')
            else:
                end_time = int(test.iloc[0]['exact_time'])

        # If the last timestamp in the saved file > specified start timestamp, use the df's latest one
        if test['exact_time'].iloc[-1] > start_time:
            if test['exact_time'].iloc[0] < start_time:
                start_time = int(test.iloc[-2]['exact_time'])

    return start_time, end_time
