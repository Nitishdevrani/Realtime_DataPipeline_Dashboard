import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, acf, pacf


# Function to check stationarity using the Augmented Dickey-Fuller test
def check_stationarity(timeseries):
    result = adfuller(timeseries)
    print("ADF Statistic:", result[0])
    print("p-value:", result[1])
    print("Critical Values:", result[4])
    return result[1] < 0.05  # If p-value < 0.05, data is stationary


# Function to difference a time series to achieve stationarity
def difference_series(series, order=1):
    return np.diff(series, n=order)


# Function to determine ARIMA model parameters based on ACF and PACF
def find_arima_params(series):
    nlags = min(len(series) // 2, 10)  # Ensure nlags is valid
    lag_acf = acf(series, nlags=nlags)
    lag_pacf = pacf(series, nlags=nlags)

    p = (
        np.where(
            lag_pacf < 1.96 / np.sqrt(len(series)), 0, np.arange(len(lag_pacf))
        )[1]
        if len(lag_pacf) > 1
        else 1
    )
    q = (
        np.where(
            lag_acf < 1.96 / np.sqrt(len(series)), 0, np.arange(len(lag_acf))
        )[1]
        if len(lag_acf) > 1
        else 1
    )

    d = 0
    while not check_stationarity(series) and d < 2:
        series = difference_series(series, order=1)
        d += 1

    return p, d, q


# Function to train the ARIMA model
def train_arima(series, p, d, q):
    model = ARIMA(series, order=(p, d, q))
    model_fit = model.fit()
    return model_fit


# Function to predict future values without iteration
def predict_future(model_fit, steps=10):
    forecast = model_fit.forecast(steps=steps)
    return forecast


# Function to visualize the results with sub-predictions
def visualize_results_with_subpredictions(
    original_series, subpredictions, step_interval
):
    plt.figure(figsize=(10, 5))
    plt.plot(
        range(len(original_series)),
        original_series,
        label="Historical Data",
        marker="o",
    )
    for i, subprediction in enumerate(subpredictions):
        start_idx = (
            step_interval * i
            + len(original_series)
            - len(subpredictions) * step_interval
        )
        plt.plot(
            range(start_idx, start_idx + len(subprediction)),
            subprediction,
            label=f"Subprediction {i + 1}",
            marker="x",
            linestyle="dashed",
        )
    plt.xlabel("Time Steps")
    plt.ylabel("Query Counts")
    # plt.legend()
    plt.title("Real-Time Workload Prediction Using ARIMA")
    plt.show()


# Simulate real-time data and subpredictions
np.random.seed(42)
x = np.linspace(0, 20, 1000)
query_counts = (
    2 * x**3
    - 5 * x**2
    + 3 * x
    + 50
    + 50 * np.sin(2 * np.pi * x / 5)
    + np.random.normal(0, 20, len(x))
)
query_counts = query_counts.astype(int).tolist()

# Parameters for real-time simulation
window_size = 50  # Number of points before retraining
step_interval = 10  # Number of steps to predict each time

subpredictions = []
historical_data = []

for i in range(0, len(query_counts), step_interval):
    # Append the current incoming data
    historical_data.extend(query_counts[i : i + step_interval])

    # Only train when the historical data reaches the window size
    if len(historical_data) >= window_size:
        train_data = historical_data[-window_size:]

        # Find ARIMA parameters
        p, d, q = find_arima_params(train_data)

        # Train the model
        model_fit = train_arima(train_data, p, d, q)

        # Predict future steps
        future_pred = predict_future(model_fit, steps=step_interval)
        subpredictions.append(future_pred)

# Visualize the results
visualize_results_with_subpredictions(
    historical_data, subpredictions, step_interval
)
