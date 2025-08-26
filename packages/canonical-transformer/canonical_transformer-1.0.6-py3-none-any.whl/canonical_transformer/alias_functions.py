"""
This module provides alias functions for saving data in different formats.
"""

from .save_utils import save_df_as_csv, save_df_as_json, save_data_as_json, save_df_as_csv_including_korean
from .dataframe_utils import transform_df_to_data, transform_data_to_df, get_data_in_df, transform_df_to_data_including_index
from .loader_utils import load_csv_file, load_json_file

map_df_to_data = transform_df_to_data
map_data_to_df = transform_data_to_df
map_df_to_some_data = get_data_in_df
map_df_to_data_including_index = transform_df_to_data_including_index

# Aliases for saving DataFrame as CSV
map_df_to_csv = save_df_as_csv
map_dataframe_to_csv = save_df_as_csv
save_dataframe_as_csv = save_df_as_csv

map_df_to_csv_including_korean = save_df_as_csv_including_korean
map_dataframe_to_csv_including_korean = save_df_as_csv_including_korean
save_dataframe_as_csv_including_korean = save_df_as_csv_including_korean

# Aliases for saving DataFrame as JSON
map_df_to_json = save_df_as_json
map_dataframe_to_json = save_df_as_json
save_dataframe_as_json = save_df_as_json

# Alias for saving data as JSON
map_data_to_json = save_data_as_json

# Aliases for mapping DataFrame to data
map_dataframe_to_data = map_df_to_data
map_data_to_dataframe = map_data_to_df

# Aliases for loading data as DataFrame
map_csv_to_df = load_csv_file
map_csv_to_dataframe = load_csv_file
load_csv_as_df = load_csv_file
map_json_to_data = load_json_file
