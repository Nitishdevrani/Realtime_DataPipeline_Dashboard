""" Kafka Producer for raw data """

import asyncio
from datetime import datetime, timedelta
import json
import duckdb
from confluent_kafka import Producer


class ProducerClassDuckDB:
    """Kafka Producer for raw data"""

    def __init__(
        self,
        kafka_host,
        kafka_topic,
        provisioned_file,
        serverless_file,
        table_name,
    ):
        self.producer = Producer(
            {
                "bootstrap.servers": kafka_host,
                "queue.buffering.max.kbytes": 1048576,
            }
        )

        self.topic = kafka_topic
        self.table_name = table_name

        # Connect to DuckDB
        self.conn = duckdb.connect("producer.duckdb")
        # Check if table exists
        table_exists = self.conn.execute(
            f"""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{table_name}'
        """
        ).fetchone()[0]

        if table_exists:
            print(
                f"Table '{table_name}' already exists. Skipping data loading."
            )
        else:
            print(
                f"Table '{table_name}' does not exist. Create and load data..."
            )
            # Load data directly from Parquet
            self.conn.execute(
                f"""
                CREATE TABLE {table_name} AS
                SELECT * FROM read_parquet('{provisioned_file}')
            """
            )
            self.conn.execute(
                f"""
                INSERT INTO {table_name}
                SELECT * FROM read_parquet('{serverless_file}')
            """
            )

        row_count = self.conn.execute(
            f"SELECT COUNT(*) FROM {table_name};"
        ).fetchall()
        print(f"Total rows in '{table_name}': {row_count[0][0]}")

    def _get_timestamp_range(self):
        """Fetch the minimum and maximum timestamps from the table."""

        query = f"""
            SELECT MIN(arrival_timestamp), MAX(arrival_timestamp)
            FROM {self.table_name};
        """
        min_timestamp, max_timestamp = self.conn.execute(query).fetchone()

        # Ensure min_timestamp and max_timestamp are datetime objects
        min_timestamp = datetime.fromisoformat(str(min_timestamp))
        max_timestamp = datetime.fromisoformat(str(max_timestamp))

        return min_timestamp, max_timestamp

    async def produce_data_in_chunks(
        self, chunk_size_minutes=30, chunk_size_seconds=0
    ):
        """
        Fetch and produce data to Kafka in chunks. This method offloads the
        blocking parts (querying, row processing, and flushing) to a separate thread.
        """
        min_datetime, max_datetime = self._get_timestamp_range()
        chunk_size = timedelta(
            minutes=chunk_size_minutes, seconds=chunk_size_seconds
        )

        current_start = min_datetime
        while current_start <= max_datetime:
            current_end = current_start + chunk_size

            # Offload the blocking chunk processing to a thread.
            await asyncio.to_thread(self.produce_chunk, current_start, current_end)

            # Yield to the event loop.
            await asyncio.sleep(0)
            current_start = current_end

        print("All chunks processed and sent to Kafka!")

    def produce_chunk(self, current_start: datetime, current_end: datetime):
        """
        This method runs in a separate thread. It queries DuckDB for the given
        time window, converts each row to JSON, produces messages to Kafka, and
        flushes the producer.
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE arrival_timestamp >= '{current_start.isoformat()}'
              AND arrival_timestamp < '{current_end.isoformat()}'
              ORDER BY arrival_timestamp ASC;
        """
        chunk = self.conn.execute(query).fetchall()
        # Cache the description so we don't recompute it on every row.
        column_names = [desc[0] for desc in self.conn.description]

        for row in chunk:
            # Create a dictionary for the row.
            row_dict = dict(zip(column_names, row))
            # Convert datetime objects to ISO strings.
            for key, value in row_dict.items():
                if isinstance(value, datetime):
                    row_dict[key] = value.isoformat()

            # Serialize the dictionary to JSON.
            message = json.dumps(row_dict)
            self.producer.produce(self.topic, value=message)

        # Flush the producer to ensure messages are sent.
        self.producer.flush()

    def close(self):
        """Close DuckDB connection and flush producer."""
        self.conn.close()
        self.producer.flush()
