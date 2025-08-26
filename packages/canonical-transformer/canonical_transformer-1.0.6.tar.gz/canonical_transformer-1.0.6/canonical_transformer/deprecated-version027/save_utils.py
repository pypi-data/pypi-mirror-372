import os
import json
from .dataframe_utils import transform_df_to_data

def save_df_as_csv(df, file_folder, file_name, include_index=False):
    """
    Save a DataFrame as a CSV file.

    Parameters:
    df (pandas.DataFrame): The DataFrame to save.
    file_folder (str): The folder where the file will be saved.
    file_name (str): The name of the file.
    include_index (bool): Whether to include the DataFrame index in the CSV file. Default is False.

    Returns:
    None
    """
    df = df.reset_index() if include_index else df
    df.to_csv(os.path.join(file_folder, file_name), index=False)
    print(f"| Saved csv to {os.path.join(file_folder, file_name)}")
    return None

def save_data_as_json(data, file_folder, file_name):
    """
    Save data as a JSON file.

    Parameters:
    data (dict): The data to save.
    file_folder (str): The folder where the file will be saved.
    file_name (str): The name of the file.

    Returns:
    None
    """
    with open(os.path.join(file_folder, file_name), 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"| Saved json to {os.path.join(file_folder, file_name)}")
    return None

def save_df_as_json(df, file_folder, file_name):
    """
    Transform a DataFrame to JSON data and save it as a JSON file.

    Parameters:
    df (pandas.DataFrame): The DataFrame to transform and save.
    file_folder (str): The folder where the file will be saved.
    file_name (str): The name of the file.

    Returns:
    None
    """
    data = transform_df_to_data(df)
    
    print("| Transformed df to json data")
    save_data_as_json(data, file_folder, file_name)
    print(f"| Saved json to {os.path.join(file_folder, file_name)}")
    return None


def save_df_as_csv_including_korean(df, file_folder, file_name, include_index=False):
    """
    Save a DataFrame as a CSV file.

    Parameters:
    df (pandas.DataFrame): The DataFrame to save.
    file_folder (str): The folder where the file will be saved.
    file_name (str): The name of the file.
    include_index (bool): Whether to include the DataFrame index in the CSV file. Default is False.

    Returns:
    None
    """
    df = df.reset_index() if include_index else df
    df.to_csv(os.path.join(file_folder, file_name), index=False, encoding='utf-8-sig')
    print(f"| Saved csv to {os.path.join(file_folder, file_name)}")
    return None