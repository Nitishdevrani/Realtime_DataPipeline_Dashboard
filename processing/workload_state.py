"""
Class file to store the current workload state.
"""

# import asyncio
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

        # print(row.keys())

        if instance_id not in self.state:
            self.state[instance_id] = {
                "query_count": 0,
                "total_execution_time": 0,
                "scanned": 0,
                "spilled": 0,
                "alerts": [],
            }

        # Update metrics
        self.state[instance_id]["query_count"] += 1
        self.state[instance_id]["total_execution_time"] += (
            row["compile_duration_ms"]
            + row["queue_duration_ms"]
            + row["execution_duration_ms"]
        )
        self.state[instance_id]["scanned"] += row["mbytes_scanned"]
        self.state[instance_id]["spilled"] += row["mbytes_spilled"]

        # Check for alerts
        if row["mbytes_spilled"] > 1024:
            self.state[instance_id]["alerts"].append(
                f"High data spill: {row['mbytes_spilled']} MB"
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
