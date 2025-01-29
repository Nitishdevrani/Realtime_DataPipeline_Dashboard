""" Module to predict future workload. """

from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import SGDRegressor

# ----------------------------------------------------------------------------
# GLOBAL MODEL STATE
# ----------------------------------------------------------------------------
MODEL = None
INITIALIZED = False
RECENT_FEATURES = []
RECENT_TARGETS = []
WINDOW_SIZE = 50  # maximum number of samples to keep in the rolling window


# ----------------------------------------------------------------------------
# 1) PARTIAL-FIT + PREDICT FUNCTION
# ----------------------------------------------------------------------------
def partial_fit_predict(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes in a DataFrame that must have columns:
      ['timestamp', 'query_count', 'total_execution_time',
       'avg_query_count', 'avg_execution_time'].
    Returns the same DataFrame with an additional 'prediction' column
    using an online (partial-fit) SGDRegressor.

    - We parse the hour_of_day from 'timestamp' and add it as a feature.
    - The target is 'query_count'.
    - The model is trained incrementally on each call, using a rolling window.
    """
    global MODEL, INITIALIZED, RECENT_FEATURES, RECENT_TARGETS

    # Ensure 'timestamp' is datetime, then extract hour_of_day
    df["hour_of_day"] = pd.to_datetime(df["timestamp"]).dt.hour

    # Build the feature matrix (X) and target vector (y)
    # We'll use: [query_count, total_execution_time, avg_query_count,
    #             avg_execution_time, hour_of_day] as features
    X_new = df[
        [
            "query_count",
            "total_execution_time",
            "avg_query_count",
            "avg_execution_time",
            "hour_of_day",
        ]
    ].values

    # We'll predict "query_count" itself
    y_new = df["query_count"].values

    # Add these rows to our in-memory rolling window
    for x, y in zip(X_new, y_new):
        RECENT_FEATURES.append(x)
        RECENT_TARGETS.append(y)

    # Remove oldest samples if we exceed the window size
    while len(RECENT_FEATURES) > WINDOW_SIZE:
        RECENT_FEATURES.pop(0)
        RECENT_TARGETS.pop(0)

    # Initialize model if this is the first time
    if not INITIALIZED:
        MODEL = SGDRegressor(random_state=42)
        # partial_fit can handle multiple samples at once:
        MODEL.partial_fit(np.array(RECENT_FEATURES), np.array(RECENT_TARGETS))
        INITIALIZED = True
    else:
        # Update the model with the recent window (or just new data)
        MODEL.partial_fit(np.array(RECENT_FEATURES), np.array(RECENT_TARGETS))

    # Use the updated model to predict on the newly provided DataFrame
    predictions = MODEL.predict(X_new)
    df["prediction"] = predictions

    return df


# ----------------------------------------------------------------------------
# 2) SYNTHETIC DATA GENERATOR (FOR DEMO)
# ----------------------------------------------------------------------------
def generate_synthetic_data(num_rows=100, start_time=None) -> pd.DataFrame:
    """
    Create a DataFrame with columns:
      ['timestamp', 'query_count', 'total_execution_time',
       'avg_query_count', 'avg_execution_time']
    to simulate streaming data. For each row, 'timestamp' increments by 1 minute.
    'query_count' drifts upward slightly plus random noise.
    """
    if start_time is None:
        start_time = datetime(2025, 1, 1, 0, 0, 0)

    data = []
    current_time = start_time
    base_qcount = 10

    for i in range(num_rows):
        # Mild upward trend + random noise
        qcount = max(0, int(base_qcount + 0.2 * i + random.gauss(0, 3)))
        total_exec_time = qcount * random.randint(100, 1000)

        row = {
            "timestamp": current_time,
            "query_count": qcount,
            "total_execution_time": float(total_exec_time),
            "avg_query_count": float(qcount),  # For example only
            "avg_execution_time": float(total_exec_time / (qcount + 1e-5)),
        }

        data.append(row)
        current_time += timedelta(minutes=1)  # increment by 1 minute

    return pd.DataFrame(data)


# ----------------------------------------------------------------------------
# 3) MAIN DEMO: PROCESS ROW-BY-ROW AND PLOT
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)

    # Generate 200 synthetic "time steps" of data
    df_data = generate_synthetic_data(num_rows=200)

    # We'll simulate a streaming environment by processing each row individually.
    # In a real pipeline, you might receive small batches or single rows at a time.
    predictions = []
    actuals = []
    times = []

    for i in range(len(df_data)):
        # Take the i-th row as a single DataFrame
        row_df = df_data.iloc[[i]].copy()

        # Pass it to our partial_fit_predict function
        result_df = partial_fit_predict(row_df)

        # Extract the predicted value and the actual for comparison
        pred = result_df["prediction"].values[0]
        actual = row_df["query_count"].values[0]
        print(pred, actual)

        predictions.append(pred)
        actuals.append(actual)
        times.append(row_df["timestamp"].values[0])

    # Now visualize predictions vs. actual
    plt.figure(figsize=(10, 6))
    plt.plot(
        times, actuals, label="Actual Query Count", marker="o", markersize=3
    )
    plt.plot(
        times,
        predictions,
        label="Predicted Query Count",
        marker="x",
        markersize=3,
    )
    plt.title("Online Partial-Fit with SGDRegressor")
    plt.xlabel("Time")
    plt.ylabel("Query Count")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
