from fund_insight_engine import Portfolio
from canonical_transformer.morphisms import *
from canonical_transformer.path_director import FILE_FOLDER

# test data
p = Portfolio(fund_code='100004')
df = p.df
data = map_df_to_data(df)
data_json = map_json_to_data(FILE_FOLDER['morphism'], 'data.json')
df_data = map_data_to_df(data)
df_csv = map_csv_to_df(FILE_FOLDER['morphism'], 'df.csv')
df_json = map_data_to_df(data_json)

DATAFRAME_BUNDLE_FOR_TEST = [
    df, 
    df_data,
    df_json,
    df_csv
]

# test functions
def is_isomorphic_to_df(data_bundle=DATAFRAME_BUNDLE_FOR_TEST):
    df, df_data, df_json, df_csv = data_bundle
    df_ref = df.copy()
    return (
        df_ref.equals(df),
        df_ref.equals(df_data),
        df_ref.equals(df_json),
        df_ref.equals(df_csv)
    )


def is_isomorphic_to_df_data(data_bundle=DATAFRAME_BUNDLE_FOR_TEST):
    df, df_data, df_json, df_csv = data_bundle
    df_ref = df_data.copy()
    return (
        df_ref.equals(df),
        df_ref.equals(df_data),
        df_ref.equals(df_json),
        df_ref.equals(df_csv)
    )


def is_isomorphic_to_df_json(data_bundle=DATAFRAME_BUNDLE_FOR_TEST):
    df, df_data, df_json, df_csv = data_bundle
    df_ref = df_json.copy()
    return (
        df_ref.equals(df),
        df_ref.equals(df_data),
        df_ref.equals(df_json),
        df_ref.equals(df_csv)
    )

def is_isomorphic_to_df_csv(data_bundle=DATAFRAME_BUNDLE_FOR_TEST):
    df, df_data, df_json, df_csv = data_bundle
    df_ref = df_csv.copy()
    return (
        df_ref.equals(df),
        df_ref.equals(df_data),
        df_ref.equals(df_json),
        df_ref.equals(df_csv)
    )
