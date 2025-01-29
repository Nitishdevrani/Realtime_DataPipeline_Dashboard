"""
Load the cleaned data, process it and send to the dashboard.
"""

import time
import asyncio

import pandas as pd
from processing.helpers import get_rows, load_data, upload_data
from processing.prediction import predict
from processing.workload_state import WorkloadState

STATE_STORAGE_TIMER = 60


async def process_data(generator):
    """Process the data and send to the dashboard."""
    workload_state = WorkloadState()
    # TODO: remove after testing
    # workload_state.load_state()
    workload_state.reset_state()

    last_save_time = time.time()

    for row in generator:
        state = workload_state.update_state(row)

        # save the workload state
        if time.time() - last_save_time >= STATE_STORAGE_TIMER:
            asyncio.create_task(workload_state.save_state())
            last_save_time = time.time()

        state = predict(state)
        # TODO: Process the data

        asyncio.create_task(upload_data(state))

        # allow other tasks to run
        await asyncio.sleep(0)


# workload_state = WorkloadState()
# TODO: remove after testing
# workload_state.load_state()
# workload_state.reset_state()


async def process_dataframe(
    df: pd.DataFrame, state: WorkloadState
) -> pd.DataFrame:
    """Process the data and return."""

    last_save_time = time.time()

    processed_data = []
    for _, row in df.iterrows():
        state = state.update_state(row)

        # save the workload state
        if time.time() - last_save_time >= STATE_STORAGE_TIMER:
            asyncio.create_task(state.save_state())
            last_save_time = time.time()

        state = predict(state)
        processed_data.append(state)

        # allow other tasks to run
        await asyncio.sleep(0)
    return pd.DataFrame(processed_data)


if __name__ == "__main__":
    df = load_data("data/serverless/serverless_full.parquet", n=500)
    row_generator = get_rows(df)
    asyncio.run(process_data(row_generator))
