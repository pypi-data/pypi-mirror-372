from canonical_transformer.functionals import pipe

def iD_df(df):
    from canonical_transformer.morphisms import map_df_to_data, map_data_to_df
    return pipe(
        map_df_to_data,
        map_data_to_df,
    )(df)

def iD_data(data):
    from canonical_transformer.morphisms import map_data_to_df, map_df_to_data
    return pipe(
        map_data_to_df,
        map_df_to_data,
    )(data)

def is_df_isomorphic(df):
    return df.equals(iD_df(df))

def is_data_isomorphic(data):
    return data == iD_data(data)