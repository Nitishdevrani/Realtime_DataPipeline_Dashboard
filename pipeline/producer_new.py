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
                'batch.size': 32768,  # Set batch size to 32 KB
                'linger.ms': 500,     # Wait up to 100ms to fill the batch
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
        self, chunk_size_minutes=1, chunk_size_seconds=1, sleep_time=0
    ):
        """Fetch and produce data to Kafka in chunks."""

        # Get the timestamp range
        min_datetime, max_datetime = self._get_timestamp_range()
        chunk_size = timedelta(
            minutes=chunk_size_minutes, seconds=chunk_size_seconds
        )

        current_start = min_datetime
        while current_start <= max_datetime:
            current_end = current_start + chunk_size

            # Query the current chunk
            query = f"""
                SELECT * FROM {self.table_name}
                WHERE arrival_timestamp >= '{current_start.isoformat()}'
                AND arrival_timestamp < '{current_end.isoformat()}';
            """
            chunk = self.conn.execute(query).fetchall()
            # print(len(chunk))
            # i = 0
            for row in chunk:
                # Convert datetime objects to strings (ISO format),
                # in the row before serializing
                
                row_dict = dict(
                    zip([desc[0] for desc in self.conn.description], row)
                )
                # Convert datetime values to isoformat strings
                for key, value in row_dict.items():
                    if isinstance(value, datetime):
                        row_dict[key] = value.isoformat()

                # Serialize the dictionary to a JSON string
                message = json.dumps(row_dict)
                while len(self.producer) >90000:
                    self.producer.flush()

                self.producer.produce(self.topic, value=message)
                # i += 1
                # print(f"Produced: {message}")
            # print(f"Chunk {current_start} to {current_end} produced: {i}")
            self.producer.flush()
            await asyncio.sleep(sleep_time)
            current_start = current_end

        print("All chunks processed and sent to Kafka!")

    def close(self):
        """Close DuckDB connection and flush producer."""
        self.conn.close()
        self.producer.flush()
