import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler, PolynomialFeatures

# ---------------------------------------------------------------------------
# GLOBALS for model state
# ---------------------------------------------------------------------------
MODEL = None
SCALER = None
POLY = None

INITIALIZED = False
BATCH_X = []
BATCH_y = []
BATCH_SIZE = 15  # how many single-row calls to accumulate before partial_fit

FIRST_TIMESTAMP = None
TOTAL_SAMPLES_SEEN = 0

MIN_SAMPLES_TO_FORECAST = (
    80  # must see at least 20 samples before trusting forecast
)

# We'll store whether we're using a log transform so we can invert predictions later
USE_LOG_TARGET = (
    True  # set to False if you want direct regression on total_queries
)


def predict_or_update(row_df: pd.DataFrame, forecast_steps: int = 0) -> list:
    """
    Ingests a single row at a time (row_df with columns: ['users', 'overall']),
    partial-fits the global model in small batches, and optionally returns an
    n-step future forecast.

    Constraints on row_df:
      row_df["overall"].iloc[0] is a dict-like with fields:
        [0, 'avg_query_count', 'avg_execution_time', 'avg_scanned',
         'avg_spilled', 'avg_abort_rate', 'timestamp',
         'total_queries', 'total_exec_time', ...]

    Steps:
      1) Parse the single row's time, convert to hours since the first timestamp.
      2) Build features, including polynomial expansion on time_in_hours.
      3) If USE_LOG_TARGET, transform total_queries -> log1p before partial-fit.
      4) Accumulate in a batch. Once full, partial-fit the model.
      5) If forecast_steps>0 and we have enough data, produce a multi-step forecast.

    Returns: a list of length `forecast_steps` if we can forecast, else [].
    """
    global MODEL, SCALER, POLY
    global INITIALIZED, BATCH_X, BATCH_y
    global BATCH_SIZE, FIRST_TIMESTAMP, TOTAL_SAMPLES_SEEN
    global MIN_SAMPLES_TO_FORECAST, USE_LOG_TARGET

    if len(row_df) != 1:
        raise ValueError("Please pass a DataFrame with exactly 1 row.")

    overall_data = row_df["overall"].iloc[0]

    # 1) Parse timestamp, track "first" so we can compute hours since start
    timestamp_str = overall_data["timestamp"]
    timestamp = pd.to_datetime(timestamp_str)
    if FIRST_TIMESTAMP is None:
        FIRST_TIMESTAMP = timestamp

    minutes_since_start = (timestamp - FIRST_TIMESTAMP).total_seconds() / 60.0
    time_hrs = (
        minutes_since_start / 60.0
    )  # keep time smaller for polynomial expansion

    # 2) Collect numeric features (you can add more if needed)
    avg_qcount = float(overall_data.get("avg_query_count", 0.0))
    avg_exec_time = float(overall_data.get("avg_execution_time", 0.0))
    avg_scanned = float(overall_data.get("avg_scanned", 0.0))
    avg_spilled = float(overall_data.get("avg_spilled", 0.0))
    avg_abort_rate = float(overall_data.get("avg_abort_rate", 0.0))
    total_exec_time = float(overall_data.get("total_exec_time", 0.0))

    # 3) Polynomial expansion on time_hrs
    #    We'll do degree=2 to capture mild curvature
    global POLY
    if POLY is None:
        POLY = PolynomialFeatures(degree=2, include_bias=False)
        POLY.fit([[time_hrs]])  # hack: fit on first row's time
    poly_time = POLY.transform([[time_hrs]])  # shape (1,2) for degree=2

    # Combine everything: 6 numeric fields + 2 polynomial time features = 8
    X_vec = np.hstack(
        [
            [
                avg_qcount,
                avg_exec_time,
                avg_scanned,
                avg_spilled,
                avg_abort_rate,
                total_exec_time,
            ],
            poly_time.ravel(),
        ]
    )  # shape: (8,)

    # 4) Target (log transform if desired)
    total_queries = float(overall_data.get("total_queries", 0.0))
    if USE_LOG_TARGET:
        # log(1 + y)
        y_val = np.log1p(max(0.0, total_queries))  # ensure positivity
    else:
        y_val = total_queries

    # Accumulate in a batch
    BATCH_X.append(X_vec)
    BATCH_y.append(y_val)
    TOTAL_SAMPLES_SEEN += 1

    # Partial-fit once batch is full
    if len(BATCH_X) >= BATCH_SIZE:
        X_arr = np.array(BATCH_X)
        y_arr = np.array(BATCH_y)

        if not INITIALIZED:
            # Init scaler + model
            SCALER = StandardScaler()
            SCALER.fit(X_arr)

            MODEL = SGDRegressor(
                loss="huber",
                epsilon=1.0,
                alpha=1e-4,  # moderate regularization
                learning_rate="invscaling",  # so step size decays over time
                eta0=1e-3,  # initial LR
                power_t=0.25,  # typical default
                random_state=42,
            )
            MODEL.partial_fit(SCALER.transform(X_arr), y_arr)
            INITIALIZED = True
        else:
            # partial-fit on subsequent batches
            X_scaled = SCALER.transform(X_arr)
            MODEL.partial_fit(X_scaled, y_arr)

        # clear batch
        BATCH_X.clear()
        BATCH_y.clear()

    # If forecast_steps=0 or not enough data yet, return []
    if forecast_steps <= 0:
        return []
    if not INITIALIZED or TOTAL_SAMPLES_SEEN < MIN_SAMPLES_TO_FORECAST:
        return []

    # 5) If we can forecast, do so for forecast_steps increments of 1 minute each
    future_preds = []
    last_time = timestamp

    for _ in range(forecast_steps):
        last_time += timedelta(minutes=1)
        mins_future = (last_time - FIRST_TIMESTAMP).total_seconds() / 60.0
        time_hrs_future = mins_future / 60.0

        # polynomial transform
        future_poly_time = POLY.transform([[time_hrs_future]])  # shape (1,2)

        # guess placeholders for the other features
        guess_avg_qcount = 10.0
        guess_avg_exec_time = 2000.0
        guess_scanned = 1000.0
        guess_spilled = 0.0
        guess_abort_rate = 0.0
        guess_total_exec = 20000.0

        X_fut = np.hstack(
            [
                [
                    guess_avg_qcount,
                    guess_avg_exec_time,
                    guess_scanned,
                    guess_spilled,
                    guess_abort_rate,
                    guess_total_exec,
                ],
                future_poly_time.ravel(),
            ]
        )

        X_fut_scaled = SCALER.transform([X_fut])
        y_pred_log = MODEL.predict(X_fut_scaled)[0]
        # Invert log transform if used
        if USE_LOG_TARGET:
            y_pred = np.expm1(y_pred_log)  # exp(y) - 1
        else:
            y_pred = y_pred_log
        future_preds.append(y_pred)

    return future_preds


# ---------------------------------------------------------------------------
# EXAMPLE USAGE + VISUALIZATION
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    def create_example_df(n=200):
        """
        Build a DataFrame with:
          - columns: "users", "overall"
          - each row["overall"] has keys like:
             0, 'avg_query_count', 'avg_execution_time', 'avg_scanned',
             'avg_spilled', 'avg_abort_rate', 'timestamp',
             'total_queries', 'total_exec_time'
        """
        rows = []
        current_time = datetime(2025, 1, 1, 0, 0, 0)
        for i in range(n):
            # mild upward trend in total_queries plus noise
            # but let's let it be somewhat exponential
            # e.g. total_queries ~ 100 * exp(i/100) + random
            # so we see a fast growth
            exp_factor = np.exp(i / 100.0)
            tq = int(100 * exp_factor + random.gauss(0, 5))

            data_overall = {
                0: "unused_key",
                "avg_query_count": 10 + 0.1 * i + random.gauss(0, 1),
                "avg_execution_time": float(2000 + random.randint(-50, 50)),
                "avg_scanned": float(random.randint(0, 2000)),
                "avg_spilled": 0.0,
                "avg_abort_rate": 0.0,
                "timestamp": str(current_time),
                "total_queries": tq,
                "total_exec_time": float(random.randint(1000, 10000)),
            }
            row_dict = {"users": {}, "overall": data_overall}
            rows.append(row_dict)
            current_time += timedelta(minutes=1)
        return pd.DataFrame(rows)

    df_data = create_example_df(200)

    # 1) Stream data row-by-row
    for i in range(len(df_data)):
        row_df = df_data.iloc[[i]]
        predict_or_update(row_df, forecast_steps=0)

    # 2) Evaluate final model on entire training set
    if not INITIALIZED:
        print("Model never got initialized (not enough data).")
    else:
        all_timestamps = []
        actual_list = []
        predicted_list = []

        for i in range(len(df_data)):
            row = df_data.iloc[[i]]
            overall_data = row["overall"].iloc[0]

            # Recreate the feature vector
            tstamp = pd.to_datetime(overall_data["timestamp"])
            all_timestamps.append(tstamp)

            mins_since = (tstamp - FIRST_TIMESTAMP).total_seconds() / 60.0
            time_hrs = mins_since / 60.0

            poly_time = POLY.transform([[time_hrs]])  # shape(1,2)
            X_vec = np.hstack(
                [
                    [
                        float(overall_data.get("avg_query_count", 0)),
                        float(overall_data.get("avg_execution_time", 0)),
                        float(overall_data.get("avg_scanned", 0)),
                        float(overall_data.get("avg_spilled", 0)),
                        float(overall_data.get("avg_abort_rate", 0)),
                        float(overall_data.get("total_exec_time", 0)),
                    ],
                    poly_time.ravel(),
                ]
            )
            X_scaled = SCALER.transform([X_vec])
            y_pred_log = MODEL.predict(X_scaled)[0]
            if USE_LOG_TARGET:
                y_pred = np.expm1(y_pred_log)
            else:
                y_pred = y_pred_log

            predicted_list.append(y_pred)
            actual_list.append(float(overall_data["total_queries"]))

        # Compute a cumulative RMSE
        rmse_list = []
        cum_preds = []
        cum_actuals = []
        for i in range(len(actual_list)):
            cum_preds.append(predicted_list[i])
            cum_actuals.append(actual_list[i])
            rmse = np.sqrt(
                np.mean((np.array(cum_preds) - np.array(cum_actuals)) ** 2)
            )
            rmse_list.append(rmse)

        # Plot 1: Actual vs. Predicted
        plt.figure(figsize=(10, 5))
        plt.plot(
            all_timestamps,
            actual_list,
            label="Actual",
            marker="o",
            markersize=3,
        )
        plt.plot(
            all_timestamps,
            predicted_list,
            label="Predicted",
            marker="x",
            markersize=3,
        )
        plt.title("Actual vs. Predicted (Final Model on Training Data)")
        plt.xlabel("Time")
        plt.ylabel("Total Queries")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        # plt.show()

        # Plot 2: RMSE Over Time
        plt.figure(figsize=(10, 5))
        plt.plot(
            all_timestamps,
            rmse_list,
            label="RMSE (cumulative)",
            marker="o",
            markersize=3,
        )
        plt.title("RMSE Over Time (Training Set, Final Model)")
        plt.xlabel("Time")
        plt.ylabel("RMSE")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
