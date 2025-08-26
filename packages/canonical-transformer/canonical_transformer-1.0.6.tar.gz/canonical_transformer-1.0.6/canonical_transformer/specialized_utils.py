from .dataframe_utils import transform_df_to_data

def transfrom_df_to_data_fits_universal_dataframe(df, rnd=2):
    """
    Transforms a DataFrame to a universal-dataframe-format with rounded values.

    Parameters:
    df (pandas.DataFrame): The input DataFrame to be transformed.
    rnd (int, optional): The number of decimal places to round to. Default is 2.

    Returns:
    data: The transformed data in a universal format.
    """
    df = round(df, rnd)
    data = transform_df_to_data(df, capitalize=True)
    return data