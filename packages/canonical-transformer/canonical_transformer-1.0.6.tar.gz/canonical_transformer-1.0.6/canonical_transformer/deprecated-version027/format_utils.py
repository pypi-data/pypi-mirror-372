def rename_columns(df, mapping):
    """
    Rename columns of a DataFrame according to a given mapping and convert all column names to uppercase.

    Parameters:
    df (pandas.DataFrame): The DataFrame whose columns are to be renamed.
    mapping (dict): A dictionary mapping old column names to new column names.

    Returns:
    pandas.DataFrame: The DataFrame with renamed and capitalized columns.
    """
    df = df.rename(columns=mapping)
    df.columns = [col.upper() for col in df.columns]
    return df

def capitalize_column_names_in_df(df):
    """
    Convert all column names in a DataFrame to uppercase.

    Parameters:
    df (pandas.DataFrame): The DataFrame whose column names are to be capitalized.

    Returns:
    pandas.DataFrame: The DataFrame with capitalized column names.
    """
    cols_ref = df.columns
    df.columns = [col.upper() for col in cols_ref]
    return df