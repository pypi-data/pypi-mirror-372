from .dataframe_utils import get_data_in_df

def get_mapping_of_column_pairs(df, key_col, value_col):
    data = get_data_in_df(df, cols=[key_col, value_col])
    mapping = {datum[key_col]: datum[value_col] for datum in data}
    return mapping

def get_inverse_mapping(mapping):
    return {value: key for key, value in mapping.items()}