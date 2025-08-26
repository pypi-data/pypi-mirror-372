import os
from functools import partial
from canonical_transformer.functionals import pipe
from canonical_transformer.isomorphisms import validate_df_pseudo_isomorphism, validate_data_isomorphism
from .map_data import map_data_to_json
from .basis import standardize_file_name_for_csv

def map_df_to_data(df):
    df = df.copy()
    if not df.index.name:
        df.index.name = '__index__'
        df = df.reset_index()
    elif df.index.name=='index':
        df = df.reset_index()
    else:
        df = df.reset_index()
    data = df.to_dict(orient='records')
    return data

def map_df_to_csv(df, file_folder, file_name, encoding='utf-8-sig', option_verbose=True):
    df_ref = df
    df = df.copy()
    if df.index.name:
        df = df.reset_index()
    file_name = standardize_file_name_for_csv(file_name)
    file_path = os.path.join(file_folder, file_name)
    df.to_csv(file_path, index=False, encoding=encoding)
    if option_verbose:
        print(f"| Saved csv to {file_path}")
    from .map_csv import map_csv_to_df
    df_csv = map_csv_to_df(file_folder, file_name)
    is_isomorphism = validate_df_pseudo_isomorphism(df_ref, df_csv)
    if is_isomorphism:
        return df_csv
    else:
        raise ValueError(f"Failed to validate isomorphism between df and df_csv: {is_isomorphism}")

def map_df_to_json(df, file_folder, file_name):
    return pipe(
        map_df_to_data,
        partial(map_data_to_json, file_folder=file_folder, file_name=file_name)
    )(df)
