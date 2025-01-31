"""
Load the cleaned data, process it and send to the dashboard.
"""

import time
import asyncio

import pandas as pd
from processing.helpers import get_rows, load_data, upload_data
from processing.prediction import partial_fit_predict
from processing.workload_state import WorkloadState

STATE_STORAGE_TIMER = 60


async def process_dataframe(
    df: pd.DataFrame, state: WorkloadState
) -> pd.DataFrame:
    """Process the data and return."""

    last_save_time = time.time()

    processed_data = []
    for _, df_row in df.iterrows():
        state = state.update_state(df_row)

        # save the workload state
        if time.time() - last_save_time >= STATE_STORAGE_TIMER:
            asyncio.create_task(state.save_state())
            last_save_time = time.time()

        state = partial_fit_predict(state)
        processed_data.append(state)

        # allow other tasks to run
        await asyncio.sleep(0)
    return pd.DataFrame(processed_data)


if __name__ == "__main__":
    partial_data = load_data("data/serverless/serverless_full.parquet", n=500)

    workload_state = WorkloadState()  # create aggregator
    row_generator = get_rows(partial_data)

    for row in row_generator:
        data = process_dataframe(row, workload_state)
