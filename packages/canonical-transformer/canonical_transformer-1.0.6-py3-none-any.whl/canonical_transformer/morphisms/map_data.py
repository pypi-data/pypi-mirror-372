from functools import partial
import os
import json
import pandas as pd
import numpy as np
from canonical_transformer.isomorphisms import validate_data_isomorphism
from canonical_transformer.functionals import pipe
from .basis import standardize_file_name_for_json


def convert_nan_to_null(obj):
    if isinstance(obj, dict):
        return {key: convert_nan_to_null(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_nan_to_null(item) for item in obj]
    elif isinstance(obj, float) and np.isnan(obj):
        return None
    else:
        return obj


def map_data_to_df(data):
    df = pd.DataFrame(data)
    df = df.set_index(df.columns[0])
    if df.index.name=='index':
        df.index.name = None
    if df.index.name == '__index__':
        df.index.name = None
    return df

def map_data_to_json(data, file_folder, file_name, option_verbose=True):
    data_for_json = convert_nan_to_null(data)
    file_name = standardize_file_name_for_json(file_name)
    file_path = os.path.join(file_folder, file_name)    
    with open(file_path, 'w') as f:
        json.dump(data_for_json, f, indent=4, ensure_ascii=False)
    if option_verbose:
        print(f"| Saved json to {file_path}")
    from .map_json import map_json_to_data
    data_json = map_json_to_data(file_folder, file_name)
    if validate_data_isomorphism(data, data_json):
        return data_json
    else:
        raise ValueError(f"Failed to validate isomorphism between data and data_json")

def map_data_to_csv(data, file_folder, file_name, encoding='utf-8-sig', option_verbose=True):
    from .map_df import map_df_to_csv
    return pipe(
        map_data_to_df,
        partial(map_df_to_csv, file_folder=file_folder, file_name=file_name, encoding=encoding, option_verbose=option_verbose)
    )(data)