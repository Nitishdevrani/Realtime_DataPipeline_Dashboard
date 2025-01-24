"""
Load the cleaned data, process it and send to the dashboard.
"""

import time
import asyncio
from helpers import get_rows, load_data, upload_data
from workload_state import WorkloadState

STATE_STORAGE_TIMER = 60


async def process_data(generator):
    """Process the data and send to the dashboard."""
    workload_state = WorkloadState()
    # TODO: remove after testing
    # workload_state.load_state()
    workload_state.reset_state()

    last_save_time = time.time()

    for row in generator:
        # TODO: Process the data
        state = workload_state.update_state(row)

        # save the workload state
        if time.time() - last_save_time >= STATE_STORAGE_TIMER:
            asyncio.create_task(workload_state.save_state())
            last_save_time = time.time()

        print("uploading data")
        asyncio.create_task(upload_data(state))

        # allow other tasks to run
        await asyncio.sleep(0)


if __name__ == "__main__":
    df = load_data("data/serverless/serverless_full.parquet", n=500)
    row_generator = get_rows(df)
    asyncio.run(process_data(row_generator))
