"""
Implements an online model that continually learns from the updated workload state.
A single global model is used, and it makes per-user predictions.
"""

from river import compose, linear_model, preprocessing


model_pipeline = compose.Pipeline(
    preprocessing.OneHotEncoder(),  # handles categorical features like user_id
    linear_model.LinearRegression(),  # online linear regression
)

last_user_features = {}
last_user_value = {}


def predict(state: dict) -> dict:
    """
    Given the current workload state (from WorkloadState), update our
    online model for each user and produce a prediction for the next
    "avg_execution_time" (as an example metric). The prediction is stored
    under: state["users"][user_id]["predicted_avg_execution_time"].

    :param state: A dictionary with the structure:
        {
          "users": {
             user_id: {
                "avg_execution_time": float,
                "query_count": int,
                "total_joins": int,
                ... other metrics ...
             },
             ...
          },
          "overall": { ... }
        }
    :return: The modified state with predictions included.
    """

    users_data = state.get("users", {})

    for user_id, metrics in users_data.items():
        X = {
            "user_id": str(user_id),  # it's string for OneHotEncoder
            "query_count": metrics["query_count"],
            "total_joins": metrics["total_joins"],
        }

        # This is our target variable for demonstration:
        new_value = metrics["avg_execution_time"]

        if user_id in last_user_features and user_id in last_user_value:
            # Learn from the previous step -> new value
            old_x = last_user_features[user_id]
            # old_y = last_user_value[user_id]

            # Train incrementally on the old feature vector and the newly observed value
            model_pipeline.learn_one(old_x, new_value)

            # Predict for the current step (X)
            pred = model_pipeline.predict_one(X)
            metrics["predicted_avg_execution_time"] = round(pred, 2)

        else:
            # If there's no history yet, we can't update the model with a previous step.
            # We'll just "predict" the current as a baseline or do nothing special.
            metrics["predicted_avg_execution_time"] = new_value

        # Update stored features/values for next iteration
        last_user_features[user_id] = X
        last_user_value[user_id] = new_value

    return state
