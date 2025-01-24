"""
Some helper functions for the processing module.
"""

import pandas as pd


def load_data(file_path):
    """Load parquet file."""
    return pd.read_parquet(file_path)


def get_rows(df):
    """Get rows of a dataframe one by one."""
    for _, row in df.iterrows():
        yield row
