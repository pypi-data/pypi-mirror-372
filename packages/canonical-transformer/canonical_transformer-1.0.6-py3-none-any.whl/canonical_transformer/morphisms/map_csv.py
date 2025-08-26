import pandas as pd
import os
from canonical_transformer.functionals import pipe
from functools import partial
from .map_df import map_df_to_data, map_df_to_json

def map_csv_to_df(file_folder, file_name):
    file_path = os.path.join(file_folder, file_name)
    return pd.read_csv(file_path, index_col=0)

def map_csv_to_data(file_folder, file_name):
    return pipe(
        map_csv_to_df,
        map_df_to_data
    )(file_folder, file_name)

def map_csv_to_json(file_folder, file_name, file_folder_json=None, file_name_json=None):
    file_folder_json = file_folder if file_folder_json is None else file_folder_json
    file_name_json = file_name.replace('.csv', '.json').replace('dataset-', 'json-') if file_name_json is None else file_name_json
    df = map_csv_to_df(file_folder, file_name)
    return map_df_to_json(df, file_folder_json, file_name_json)