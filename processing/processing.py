"""
Load the cleaned data, process it and send to the dashboard.
"""

import time
import asyncio
import pandas as pd
from processing.helpers import get_rows, load_data, upload_data
from processing.workload_state import WorkloadState
from processing.prediction import RealTimePredictor

STATE_STORAGE_TIMER = 60
rt_predictor = RealTimePredictor(window_size=200, step_interval=100)


async def process_dataframe(
    df: pd.DataFrame, state: WorkloadState
) -> pd.DataFrame:
    """Process a DataFrame in a more efficient, batched fashion."""
    last_save_time = time.time()
    processed_states = []

    # itertuples usually faster than iterrows
    for row in df.itertuples(index=False, name="Row"):
        row_dict = row._asdict()
        updated_state = await asyncio.to_thread(state.update_state, row_dict)

        # Save state asynchronously.
        if time.time() - last_save_time >= STATE_STORAGE_TIMER:
            asyncio.create_task(state.save_state())
            last_save_time = time.time()

        # If the predictor is running on CPU
        updated_state = await asyncio.to_thread(
            rt_predictor.predict_rt_data, updated_state
        )
        processed_states.append(updated_state)

        # Let the event loop handle other tasks.
        await asyncio.sleep(0)

    return pd.concat(processed_states, ignore_index=True)


if __name__ == "__main__":
    partial_data = load_data("data/serverless/serverless_full.parquet", n=500)

    workload_state = WorkloadState()
    row_generator = get_rows(partial_data)

    for row in row_generator:
        data = process_dataframe(row, workload_state)
