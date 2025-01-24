"""
Load the cleaned data, process it and send to the dashboard.
"""

from helpers import get_rows, load_data, upload_data


if __name__ == "__main__":
    df = load_data("data/serverless/serverless_full.parquet", n=10)
    row_generator = get_rows(df)

    for row in row_generator:
        # TODO: Process the data
        processed_data = row.to_frame().T
        upload_data(processed_data)
