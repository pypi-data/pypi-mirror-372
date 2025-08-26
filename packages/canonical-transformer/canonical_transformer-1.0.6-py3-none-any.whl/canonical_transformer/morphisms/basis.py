def standardize_file_name_for_csv(file_name):
    return f'dataset-{file_name.replace("dataset-", "").replace(".csv", "")}.csv'

def standardize_file_name_for_json(file_name):
    return f'json-{file_name.replace("json-", "").replace(".json", "")}.json'
