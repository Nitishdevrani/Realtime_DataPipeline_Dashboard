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
    return model.fit()


# Function to predict future values without iteration
def predict_future(model_fit, steps=100):
    forecast = model_fit.forecast(steps=steps)
    return forecast


# Function to visualize the results
def visualize_results(original_series, forecasted_values):
    plt.figure(figsize=(10, 5))
    plt.plot(
        range(len(original_series)),
        original_series,
        label="Historical Data",
        marker="o",
    )
    plt.plot(
        range(
            len(original_series), len(original_series) + len(forecasted_values)
        ),
        forecasted_values,
        label="Predicted",
        marker="x",
        linestyle="dashed",
    )
    plt.xlabel("Time Steps")
    plt.ylabel("Query Counts")
    plt.legend()
    plt.title("Workload Prediction Using ARIMA")
    plt.show()


# Generate a polynomial workload dataset with a repeating pattern
np.random.seed(42)
x = np.linspace(0, 20, 10)
query_counts = (
    2 * x**3
    - 3 * x**2
    + 2 * x
    + 10
    + 50 * np.sin(2 * np.pi * x / 5)
    + np.random.normal(0, 20, len(x))
)
query_counts = query_counts.astype(int).tolist()

# Find optimal ARIMA parameters
p, d, q = find_arima_params(query_counts)
print(f"Optimal ARIMA parameters: p={p}, d={d}, q={q}")

# Train the ARIMA model
model_fit = train_arima(query_counts, p, d, q)

# Predict future workload demand
future_predictions = predict_future(model_fit, steps=100)
print(f"Predicted next workload query counts: {future_predictions}")

# Visualize the results
visualize_results(query_counts, future_predictions)
