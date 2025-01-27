"""
Class file to store the current workload state.
"""

import pickle
import pandas as pd
import aiofiles


class WorkloadState:
    """Class to store the current workload state."""

    def __init__(self):
        self.state = {}
        self.file_path = "workload_state.pkl"

    def update_state(self, row: pd.DataFrame) -> None:
        """Update state with metrics from the current row."""
        instance_id = row["instance_id"]

        if instance_id not in self.state:
            self.state[instance_id] = {
                "query_count": 0,
                "total_execution_time": 0,
                "scanned": 0,
                "spilled": 0,
                "avg_spill": 0,
                "query_type_counts": {},
                "total_joins": 0,
                "total_aggregations": 0,
                "unique_tables": set(),
                "cluster_metrics": {},
                "aborted_queries": 0,
            }

        # Absolute metrics
        self.state[instance_id]["query_count"] += 1
        self.state[instance_id]["total_execution_time"] += (
            row["compile_duration_ms"]
            + row["queue_duration_ms"]
            + row["execution_duration_ms"]
        )
        self.state[instance_id]["scanned"] += row["mbytes_scanned"]
        self.state[instance_id]["spilled"] += row["mbytes_spilled"]

        # Average metrics
        self.state[instance_id]["avg_spill"] = round(
            self.state[instance_id]["spilled"]
            / self.state[instance_id]["query_count"],
            2,
        )
        self.state[instance_id]["avg_execution_time"] = round(
            self.state[instance_id]["total_execution_time"]
            / self.state[instance_id]["query_count"],
            2,
        )

        # Execution Efficiency
        self.state[instance_id]["queue_time_percentage"] = round(
            (
                row["queue_duration_ms"]
                / self.state[instance_id]["total_execution_time"]
            )
            * 100,
            2,
        )
        self.state[instance_id]["compile_overhead_ratio"] = round(
            row["compile_duration_ms"] / row["execution_duration_ms"], 2
        )

        # Query Types
        query_type = row["query_type"]
        query_type_counts = self.state[instance_id]["query_type_counts"]
        query_type_counts[query_type] = query_type_counts.get(query_type, 0) + 1

        # Joins and Aggregations
        self.state[instance_id]["total_joins"] += row["num_joins"]
        self.state[instance_id]["total_aggregations"] += row["num_aggregations"]

        # Unique Tables Accessed
        self.state[instance_id]["unique_tables"].update(row["read_table_ids"])

        # Read-Write Balance
        read_ops = len(row["read_table_ids"])
        write_ops = len(row["write_table_ids"])
        self.state[instance_id]["read_write_ratio"] = round(
            read_ops / (write_ops or 1), 2
        )

        # Cluster Metrics
        cluster_size = row["cluster_size"]
        cluster_metrics = self.state[instance_id].get("cluster_metrics", {})
        if cluster_size not in cluster_metrics:
            cluster_metrics[cluster_size] = {
                "query_count": 0,
                "total_duration": 0,
            }
        cluster_metrics[cluster_size]["query_count"] += 1
        cluster_metrics[cluster_size]["total_duration"] += row[
            "execution_duration_ms"
        ]
        self.state[instance_id]["cluster_metrics"] = cluster_metrics

        # Aborted Queries
        if row["was_aborted"]:
            self.state[instance_id]["aborted_queries"] += 1
        self.state[instance_id]["abort_rate"] = round(
            self.state[instance_id]["aborted_queries"]
            / self.state[instance_id]["query_count"]
            * 100,
            2,
        )

        return self.state

    def reset_state(self) -> None:
        """Reset the state (optional)."""
        self.state = {}

    def save_state_synchronous(self) -> None:
        """Save the state to file."""
        with open(self.file_path, "wb") as f:
            pickle.dump(self, f)
        print("Saved current state.")

    async def save_state(self) -> None:
        """Save the state to a file asynchronously."""
        async with aiofiles.open(self.file_path, "wb") as f:
            await f.write(pickle.dumps(self))
        print("Saved current state asynchronously.")

    def load_state(self) -> None:
        """Load the state from file."""
        try:
            with open(self.file_path, "rb") as f:
                loaded_state = pickle.load(f)

            # Update the current instance's attributes
            self.state = loaded_state.state
            print("Loaded previous state.")
        except FileNotFoundError:
            print("No previous state found.")
