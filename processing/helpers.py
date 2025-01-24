"""
Some helper functions for the processing module.
"""

import asyncio
import time
from typing import Generator
import pandas as pd
from pyarrow.parquet import ParquetFile
import pyarrow as pa


def load_data(file_path: str, n: int = None) -> pd.DataFrame:
    """Load parquet file."""
    if n:
        rows = next(ParquetFile(file_path).iter_batches(batch_size=n))
        return pa.Table.from_batches([rows]).to_pandas()
    return pd.read_parquet(file_path)


def get_rows(df: pd.DataFrame) -> Generator[pd.Series, None, None]:
    """Get rows of a dataframe one by one."""
    for _, row in df.iterrows():
        time.sleep(1)
        yield row


async def upload_data(processed_data: pd.DataFrame) -> None:
    """Upload data to the dashboard."""
    # TODO: Implement this function with real upload logic.

    await asyncio.sleep(1)
    print(processed_data)
    # pass
