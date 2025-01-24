"""
Load the cleaned data, process it and send to the dashboard.
"""
from helpers import load_data, get_rows

if __name__ == "__main__":
    df = load_data("data/serverless/serverless_full.parquet")
    for row in get_rows(df):
        print(row)
