import ujson as json_lib
import pandas as pd
import duckdb


class WorkloadState:
    """Class to store and manage the current workload state."""

    def __init__(self, db_path: str = "workload_state.duckdb"):
        # Dictionary of user_id -> user metrics
        self.users = {}
        # Dictionary for overall (global) metrics
        self.overall = {}
        self._cached_state = None
        self._state_dirty = True

        self.db_path = db_path
        self.last_backup_timestamp = None

        # Global counters to update overall metrics incrementally.
        self.global_query_count = 0
        self.global_total_exec_time = 0
        self.global_scanned = 0
        self.global_spilled = 0
        self.global_aborted = 0
        self.global_timestamp = pd.Timestamp.min

    # @property
    # def state(self) -> pd.DataFrame:
    #     """
    #     Return the full state, including user-level and overall metrics.
    #     If the state hasn’t changed, return a cached DataFrame.
    #     """
    #     if self._state_dirty or self._cached_state is None:
    #         self._cached_state = pd.DataFrame(
    #             {"users": [self.users], "overall": [self.overall]}, index=[0]
    #         )
    #         self._state_dirty = False
    #     return self._cached_state
    @property
    def state(self) -> pd.DataFrame:
        """
        Return the state as a single DataFrame where the overall metrics are flattened into columns,
        and user metrics are merged in (this is less common since they have different granularities).
        """
        return pd.DataFrame({"users": self.users, "overall": self.overall})

    def update_state(self, row: dict) -> pd.DataFrame:
        """
        Update all metrics based on an incoming row.
        Returns the entire state after updating.
        Expecting `row` to be a dict (e.g., obtained from a Pandas Series via to_dict()).
        """
        user_id = row.get("user_id")
        if pd.isna(user_id):
            print("Skipping row due to missing user_id.")
            return self.state

        if user_id not in self.users:
            self._init_user_metrics(user_id)

        # Update user metrics and derived metrics.
        self._update_user_metrics(user_id, row)
        self._update_user_derived_metrics(user_id, row)

        # Increment global counters based on the row contributions.
        self.global_query_count += 1
        exec_time = (
            row.get("compile_duration_ms", 0)
            + row.get("queue_duration_ms", 0)
            + row.get("execution_duration_ms", 0)
        )
        self.global_total_exec_time += exec_time
        self.global_scanned += row.get("mbytes_scanned", 0)
        self.global_spilled += row.get("mbytes_spilled", 0)
        if row.get("was_aborted", False):
            self.global_aborted += 1

        arrival_timestamp = row.get("arrival_timestamp", pd.Timestamp.min)
        if arrival_timestamp > self.global_timestamp:
            self.global_timestamp = arrival_timestamp

        # Update overall state in constant time (instead of iterating over all users).
        total_users = len(self.users)
        if total_users > 0:
            self.overall["avg_query_count"] = round(
                self.global_query_count / total_users, 2
            )
            self.overall["avg_execution_time"] = round(
                self.global_total_exec_time / total_users, 2
            )
            self.overall["avg_scanned"] = round(
                self.global_scanned / total_users, 2
            )
            self.overall["avg_spilled"] = round(
                self.global_spilled / total_users, 2
            )
            # Overall abort rate as a percentage (global aborted queries / global query count)
            self.overall["avg_abort_rate"] = (
                round((self.global_aborted / self.global_query_count) * 100, 2)
                if self.global_query_count > 0
                else 0
            )
            self.overall["timestamp"] = self.global_timestamp
            self.overall["total_queries"] = self.global_query_count
            self.overall["total_exec_time"] = self.global_total_exec_time
            self.overall["predicted_query_count"] = []  # or update as needed

        self._state_dirty = True
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
            "cluster_metrics": {},
            "aborted_queries": 0,
            "abort_rate": 0,
            "read_write_ratio": 0,
            "timestamp": pd.Timestamp.min,
            "serverless": False,
        }

    def _update_user_metrics(self, user_id: str, row: dict) -> None:
        """Update raw counters (no derived calculations) for a user."""
        user_data = self.users[user_id]

        # Basic increments.
        user_data["query_count"] += 1
        user_data["total_execution_time"] += (
            row.get("compile_duration_ms", 0)
            + row.get("queue_duration_ms", 0)
            + row.get("execution_duration_ms", 0)
        )
        user_data["scanned"] += row.get("mbytes_scanned", 0)
        user_data["spilled"] += row.get("mbytes_spilled", 0)

        # Query types.
        query_type = row.get("query_type", "unknown")
        user_data["query_type_counts"][query_type] = (
            user_data["query_type_counts"].get(query_type, 0) + 1
        )

        # Joins, aggregations.
        user_data["total_joins"] += row.get("num_joins", 0)
        user_data["total_aggregations"] += row.get("num_aggregations", 0)

        # Unique tables.
        table_ids = row.get("read_table_ids", []) or []
        user_data["unique_tables"].update(table_ids)

        # Cluster metrics.
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

        # Determine if serverless.
        user_data["serverless"] = row.get("cluster_size", 0) >= 0

        # Update the timestamp for this user.
        user_data["timestamp"] = max(
            row.get("arrival_timestamp", pd.Timestamp.min),
            user_data["timestamp"],
        )

        # Aborted queries.
        if row.get("was_aborted", False):
            user_data["aborted_queries"] += 1

    def _update_user_derived_metrics(self, user_id: str, row: dict) -> None:
        """Compute any user-level averages, ratios, or percentages."""
        user_data = self.users[user_id]
        qcount = user_data["query_count"]

        # Averages.
        if qcount:
            user_data["avg_spill"] = round(user_data["spilled"] / qcount, 2)
            user_data["avg_execution_time"] = round(
                user_data["total_execution_time"] / qcount, 2
            )
        else:
            user_data["avg_spill"] = 0
            user_data["avg_execution_time"] = 0

        # Execution efficiency.
        total_execution_time = user_data["total_execution_time"]
        queue_duration = row.get("queue_duration_ms", 0)
        if total_execution_time <= 0:
            user_data["queue_time_percentage"] = 0
        else:
            user_data["queue_time_percentage"] = round(
                (queue_duration / total_execution_time) * 100, 2
            )

        compile_duration = row.get("compile_duration_ms", 0)
        execution_duration = row.get("execution_duration_ms", 0)
        if execution_duration <= 0:
            user_data["compile_overhead_ratio"] = 0
        else:
            user_data["compile_overhead_ratio"] = round(
                compile_duration / execution_duration, 2
            )

        # Aborted rate.
        if qcount:
            user_data["abort_rate"] = round(
                (user_data["aborted_queries"] / qcount) * 100, 2
            )
        else:
            user_data["abort_rate"] = 0

        # Read/Write ratio.
        read_ops = len(row.get("read_table_ids", []) or [])
        write_ops = len(row.get("write_table_ids", []) or [])
        if write_ops == 0:
            user_data["read_write_ratio"] = float("inf") if read_ops > 0 else 0
        else:
            user_data["read_write_ratio"] = round(read_ops / write_ops, 2)

    def reset_state(self) -> None:
        """Reset all user data and overall metrics."""
        self.users = {}
        self.overall = {}
        self.global_query_count = 0
        self.global_total_exec_time = 0
        self.global_scanned = 0
        self.global_spilled = 0
        self.global_aborted = 0
        self.global_timestamp = pd.Timestamp.min

    async def save_state(self) -> None:
        """
        Append a snapshot of the current state to DuckDB.
        The backup is stored in a table 'state_backup' as JSON strings.
        """
        con = duckdb.connect(self.db_path)
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS state_backup (
                backup_time TIMESTAMP,
                users TEXT,
                overall TEXT
            )
            """
        )
        backup_time = pd.Timestamp.now()
        # # Use the chosen JSON library; convert sets to lists.
        # users_json = json_lib.dumps(
        #     self.users,
        #     default=lambda o: list(o) if isinstance(o, set) else o,
        #     check_circular=False,
        # )
        # overall_json = json_lib.dumps(
        #     self.overall, default=str, check_circular=False
        # )
        # con.execute(
        #     "INSERT INTO state_backup VALUES (?, ?, ?)",
        #     (backup_time, users_json, overall_json),
        # )
        con.close()
        print(f"Backup state saved at {backup_time}.")

    def load_state(self) -> None:
        """
        Load the most recent backup from DuckDB into memory.
        Converts lists back into sets for the 'unique_tables' field.
        """
        con = duckdb.connect(self.db_path)
        try:
            df = con.execute(
                "SELECT * FROM state_backup ORDER BY backup_time DESC LIMIT 1"
            ).df()
            if not df.empty:
                backup_row = df.iloc[0]
                self.users = json_lib.loads(backup_row["users"])
                self.overall = json_lib.loads(backup_row["overall"])
                # Convert unique_tables back to sets.
                for uid, metrics in self.users.items():
                    if "unique_tables" in metrics and isinstance(
                        metrics["unique_tables"], list
                    ):
                        metrics["unique_tables"] = set(metrics["unique_tables"])
                print(
                    f"Loaded state from backup at {backup_row['backup_time']}."
                )
            else:
                print("No backup found. Starting with an empty state.")
                self.reset_state()
        except Exception as e:
            print("Error loading state backup:", e)
            self.reset_state()
        finally:
            con.close()
