""" This module cleans the data in the DataFrame. """

import math
import time
import pandas as pd

pd.set_option("future.no_silent_downcasting", True)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the data in the DataFrame."""
    try:
        # Handle missing values
        df.fillna(0, inplace=True)
        df.infer_objects(copy=False)

        # numns to the appropriate type
        df["compile_duration_ms"] = (
            pd.to_numeric(df["compile_duration_ms"], errors="coerce")
            .fillna(0)
            .astype(int)
        )
        df["execution_duration_ms"] = (
            pd.to_numeric(df["execution_duration_ms"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

        # Ensure the 'arrival_timestamp' column is correctly handled
        if "arrival_timestamp" in df.columns:
            df["arrival_timestamp"] = pd.to_datetime(
                df["arrival_timestamp"],
                format="%m/%d/%Y %I:%M %p",
                errors="coerce",
            )

        # Calculate the percentage of execution time that accounts for compilation
        valid_data = df[
            (df["compile_duration_ms"] > 0) & (df["execution_duration_ms"] > 0)
        ]
        ratios = (
            valid_data["compile_duration_ms"]
            / valid_data["execution_duration_ms"]
        )
        average_ratio = ratios.mean()

        # Check if average_ratio is finite
        if math.isfinite(average_ratio) and average_ratio > 0:
            # Apply this average ratio to estimate compile_duration_ms where it's currently 0
            df.loc[df["compile_duration_ms"] == 0, "compile_duration_ms"] = (
                (df["execution_duration_ms"] * average_ratio)
                .round()
                .astype(int)
            )

            # print(
            #     f"Applied estimated compilation times based on {average_ratio:.2%} of execution durations."
            # )
        return df

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
        return df
