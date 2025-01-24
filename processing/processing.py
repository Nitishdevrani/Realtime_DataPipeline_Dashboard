"""
Load the cleaned data, process it and send to the dashboard.
"""

from helpers import load_data, upload_data


if __name__ == "__main__":
    df = load_data("data/serverless/serverless_full.parquet", n=10)

    # TODO: Process the data

    upload_data(df)
