"""Safe the state of the workload in a file."""

import pickle
import pandas as pd
import aiofiles


class WorkloadState:
    """Class to store and manage the current workload state."""

    def __init__(self, file_path: str = "workload_state.pkl"):
        self.file_path = file_path
        # Dictionary of user_id -> user metrics
        self.users = {}
        # Dictionary for overall (global) metrics
        self.overall = {}

    @property
    def state(self) -> dict:
        """
        Return the full state, including user-level and overall metrics.
        This makes it easy to pass a single object around if needed.
        """
        return {"users": self.users, "overall": self.overall}

    def update_state(self, row: pd.DataFrame) -> dict:
        """
        Main entry point to update all metrics based on an incoming row.
        Returns the entire state after updating.
        """
        user_id = row.get("user_id")
        if pd.isna(user_id):
            print("Skipping row due to missing user_id.")
            return self.state

        # Initialize user-specific metrics if new
        if user_id not in self.users:
            self._init_user_metrics(user_id)

        # Update the user's raw counters/metrics
        self._update_user_metrics(user_id, row)

        # Compute user-derived metrics (averages, ratios, etc.)
        self._update_user_derived_metrics(user_id, row)

        # Finally, update the overall (global) averages across all users
        self._update_overall_averages()

        return self.state

    def _init_user_metrics(self, user_id: str) -> None:
        """Initialize the metrics dictionary for a new user."""
        self.users[user_id] = {
            "query_count": 0,
            "total_execution_time": 0,
            "scanned": 0,
            "spilled": 0,
            "avg_spill": 0,
            "avg_execution_time": 0,
            "queue_time_percentage": 0,
            "compile_overhead_ratio": 0,
            "query_type_counts": {},
            "total_joins": 0,
            "total_aggregations": 0,
            "unique_tables": set(),
            "cluster_metrics": {},  # e.g. { cluster_size: { "query_count": X, "total_duration": Y } }
            "aborted_queries": 0,
            "abort_rate": 0,
            "read_write_ratio": 0,
            # "serverless": True,
        }

    def _update_user_metrics(self, user_id: str, row: pd.DataFrame) -> None:
        """Update raw counters (no derived calculations) for a user based on a single row."""
        user_data = self.users[user_id]

        # Basic increments
        user_data["query_count"] += 1
        user_data["total_execution_time"] += (
            row.get("compile_duration_ms", 0)
            + row.get("queue_duration_ms", 0)
            + row.get("execution_duration_ms", 0)
        )
        user_data["scanned"] += row.get("mbytes_scanned", 0)
        user_data["spilled"] += row.get("mbytes_spilled", 0)

        # Query types
        query_type = row.get("query_type", "unknown")
        user_data["query_type_counts"][query_type] = (
            user_data["query_type_counts"].get(query_type, 0) + 1
        )

        # Joins, aggregations
        user_data["total_joins"] += row.get("num_joins", 0)
        user_data["total_aggregations"] += row.get("num_aggregations", 0)

        # Unique tables
        table_ids = row.get("read_table_ids", []) or []
        user_data["unique_tables"].update(table_ids)

        # Cluster metrics
        cluster_size = row.get("cluster_size", "unknown")
        if pd.isna(cluster_size):
            cluster_size = "unknown"

        if cluster_size not in user_data["cluster_metrics"]:
            user_data["cluster_metrics"][cluster_size] = {
                "query_count": 0,
                "total_duration": 0,
            }
        user_data["cluster_metrics"][cluster_size]["query_count"] += 1
        user_data["cluster_metrics"][cluster_size]["total_duration"] += row.get(
            "execution_duration_ms", 0
        )

        # Aborted queries
        if row.get("was_aborted", False):
            user_data["aborted_queries"] += 1

    def _update_user_derived_metrics(
        self, user_id: str, row: pd.DataFrame
    ) -> None:
        """Compute any user-level averages, ratios, or percentages that depend on updated counters."""
        user_data = self.users[user_id]
        qcount = user_data["query_count"]

        # Averages
        user_data["avg_spill"] = (
            round(user_data["spilled"] / qcount, 2) if qcount else 0
        )
        user_data["avg_execution_time"] = (
            round(user_data["total_execution_time"] / qcount, 2)
            if qcount
            else 0
        )

        # Execution Efficiency
        total_execution_time = user_data["total_execution_time"]
        queue_duration = row.get("queue_duration_ms", 0)
        if total_execution_time > 0:
            user_data["queue_time_percentage"] = round(
                (queue_duration / total_execution_time) * 100, 2
            )
        else:
            user_data["queue_time_percentage"] = 0

        compile_duration = row.get("compile_duration_ms", 0)
        execution_duration = row.get(
            "execution_duration_ms", 1
        )  # avoid division by zero
        user_data["compile_overhead_ratio"] = round(
            compile_duration / execution_duration, 2
        )

        # Aborted rate
        user_data["abort_rate"] = (
            round((user_data["aborted_queries"] / qcount) * 100, 2)
            if qcount
            else 0
        )

        # Read/Write ratio
        read_ops = len(row.get("read_table_ids", []) or [])
        write_ops = len(row.get("write_table_ids", []) or [])
        user_data["read_write_ratio"] = round(read_ops / (write_ops or 1), 2)

    def _update_overall_averages(self) -> None:
        """Compute global averages across all users and store them in `self.overall`."""
        total_users = len(self.users)
        if total_users == 0:
            self.overall = {}
            return

        # Accumulators
        total_query_count = 0
        total_exec_time = 0
        total_scanned = 0
        total_spilled = 0
        total_abort_rate = 0

        # Sum over all users
        for user_data in self.users.values():
            total_query_count += user_data["query_count"]
            total_exec_time += user_data["total_execution_time"]
            total_scanned += user_data["scanned"]
            total_spilled += user_data["spilled"]
            total_abort_rate += user_data["abort_rate"]

        # Compute averages
        self.overall["avg_query_count"] = round(
            total_query_count / total_users, 2
        )
        self.overall["avg_execution_time"] = round(
            total_exec_time / total_users, 2
        )
        self.overall["avg_scanned"] = round(total_scanned / total_users, 2)
        self.overall["avg_spilled"] = round(total_spilled / total_users, 2)
        self.overall["avg_abort_rate"] = round(
            total_abort_rate / total_users, 2
        )

    def reset_state(self) -> None:
        """Reset all user data and overall metrics."""
        self.users = {}
        self.overall = {}

    def save_state_synchronous(self) -> None:
        """Save the entire state (users + overall) to file (blocking)."""
        with open(self.file_path, "wb") as f:
            # You can store just self.state or the entire instance
            pickle.dump(self, f)
        print("Saved current state synchronously.")

    async def save_state(self) -> None:
        """Save the entire state (users + overall) to file asynchronously."""
        async with aiofiles.open(self.file_path, "wb") as f:
            await f.write(pickle.dumps(self))
        print("Saved current state asynchronously.")

    def load_state(self) -> None:
        """Load the state from a file."""
        try:
            with open(self.file_path, "rb") as f:
                loaded_state = pickle.load(f)
            # Update local attributes from the loaded object
            self.users = loaded_state.users
            self.overall = loaded_state.overall
            print("Loaded previous state.")
        except FileNotFoundError:
            print("No previous state found. Starting fresh.")
