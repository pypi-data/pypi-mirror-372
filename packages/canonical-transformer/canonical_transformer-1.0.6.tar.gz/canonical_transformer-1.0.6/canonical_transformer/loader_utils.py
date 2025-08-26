import json
import pandas as pd
import os

def load_json_file(file_name, file_folder):
    """
    Load a JSON file and return its contents as a Python object.

    Args:
        file_name (str): The name of the JSON file to be loaded.
        file_folder (str): The folder where the JSON file is located.

    Returns:
        dict: The contents of the JSON file as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not a valid JSON.
    """
    file_path = os.path.join(file_folder, file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def load_csv_file(file_name, file_folder, add_index=False):
    """
    Load a CSV file and return its contents as a DataFrame.

    Args:
        file_name (str): The name of the CSV file to be loaded.
        file_folder (str): The folder where the CSV file is located.
        drop_index (bool, optional): Whether to drop the first column of the DataFrame. Defaults to False.

    Returns:
        pd.DataFrame: The contents of the CSV file as a DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        pd.errors.EmptyDataError: If the file is empty.
    """
    file_path = os.path.join(file_folder, file_name)
    df = pd.read_csv(file_path, index_col=0) if add_index else pd.read_csv(file_path)
    return df
