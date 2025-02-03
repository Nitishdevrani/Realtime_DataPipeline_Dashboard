"""
Load the cleaned data, process it and send to the dashboard.
"""

import asyncio
import pandas as pd
from processing.billing_processing import BillingCalculator
from processing.helpers import get_rows, load_data
from processing.workload_state import WorkloadState
from processing.prediction import RealTimePredictor
from processing.prediction_spill import RealTimePredictor as SpillPredictor

rt_predictor = RealTimePredictor(window_size=200, step_interval=100)
spill_predictor = SpillPredictor(
    window_size=200, step_interval=100, threshold=15000
)
billing_calculator = BillingCalculator()


async def process_dataframe(
    df: pd.DataFrame, state: WorkloadState
) -> pd.DataFrame:
    """Process a DataFrame in a more efficient, batched fashion."""
    processed_states = []

    # itertuples usually faster than iterrows
    for row in df.itertuples(index=False, name="Row"):
        row_dict = row._asdict()

        updated_state = await asyncio.to_thread(state.update_state, row_dict)

        # Predict query count
        updated_state = await asyncio.to_thread(
            rt_predictor.predict_rt_data, updated_state
        )

        # Predict spill amount
        updated_state = await asyncio.to_thread(
            spill_predictor.predict_rt_data, updated_state
        )

        # Calculate billing for all users
        updated_state = await asyncio.to_thread(
            billing_calculator.calculate_all_users_billing, updated_state
        )

        # Add the updated state to the list
        processed_states.append(updated_state)

        # Let the event loop handle other tasks.
        await asyncio.sleep(0)

    # Combine all processed states into a single DataFrame and return
    return pd.concat(processed_states, ignore_index=True)


if __name__ == "__main__":
    partial_data = load_data("data/serverless/serverless_full.parquet", n=500)

    # Simulate incoming realtime data
    workload_state = WorkloadState()
    row_generator = get_rows(partial_data)

    for raw_row in row_generator:
        data = process_dataframe(raw_row, workload_state)
