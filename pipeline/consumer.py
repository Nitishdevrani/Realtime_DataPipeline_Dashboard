import json
import csv
import os
from datetime import datetime
from confluent_kafka import Consumer


class ConsumerClassCSV:
    def __init__(self, kafka_broker, kafka_topic, group):
        self.kafka_topic = kafka_topic
        self.consumer = Consumer(
            {
                "bootstrap.servers": kafka_broker,
                "group.id": group,
                "auto.offset.reset": "earliest",
            }
        )
        self.consumer.subscribe([kafka_topic])
        print("Topic Subscribed")

    def process_message(self, message):
        """Process the consumed message."""
        # Deserialize the JSON message
        data = json.loads(message)

        # Ensure datetime values are converted back to datetime objects
        for key, value in data.items():
            if isinstance(value, str) and "T" in value:  # ISO format check
                try:
                    data[key] = datetime.fromisoformat(
                        value
                    )  # Convert to datetime object
                except ValueError:
                    pass  # Ignore if it's not a valid ISO string

        # Calculate chunk number based on the arrival timestamp
        chunk_number = self.get_chunk_number(data["arrival_timestamp"])

        # Save the data by chunk number (to a CSV file)
        self.save_to_csv(data, chunk_number)

    def get_chunk_number(self, timestamp):
        """Calculate the chunk number based on the timestamp."""
        if isinstance(timestamp, datetime):
            return timestamp.strftime(
                "%Y-%m-%d"
            )  # Format datetime as a date string
        return timestamp.split("T")[
            0
        ]  # If it's already a string, split by 'T'  # Use the date part as the chunk identifier

    def save_to_csv(self, data, chunk_number):
        """Save the message data to a CSV file by chunk."""
        # Define the CSV file name based on the chunk number
        chunk_file_name = f"chunk_{chunk_number}.csv"
        print(chunk_file_name)
        # Check if the file exists to determine if headers need to be written
        file_exists = os.path.isfile(chunk_file_name)

        # Define the header and data rows
        header = [
            "instance_id",
            "cluster_size",
            "user_id",
            "database_id",
            "query_id",
            "arrival_timestamp",
            "compile_duration_ms",
            "queue_duration_ms",
            "execution_duration_ms",
            "feature_fingerprint",
            "was_aborted",
            "was_cached",
            "cache_source_query_id",
            "query_type",
            "num_permanent_tables_accessed",
            "num_external_tables_accessed",
            "num_system_tables_accessed",
            "read_table_ids",
            "write_table_ids",
            "mbytes_scanned",
            "mbytes_spilled",
            "num_joins",
            "num_scans",
            "num_aggregations",
            "source",
        ]

        row = [
            data.get("instance_id"),
            data.get("cluster_size"),
            data.get("user_id"),
            data.get("database_id"),
            data.get("query_id"),
            data.get("arrival_timestamp"),
            data.get("compile_duration_ms"),
            data.get("queue_duration_ms"),
            data.get("execution_duration_ms"),
            data.get("feature_fingerprint"),
            data.get("was_aborted"),
            data.get("was_cached"),
            data.get("cache_source_query_id"),
            data.get("query_type"),
            data.get("num_permanent_tables_accessed"),
            data.get("num_external_tables_accessed"),
            data.get("num_system_tables_accessed"),
            data.get("read_table_ids"),
            data.get("write_table_ids"),
            data.get("mbytes_scanned"),
            data.get("mbytes_spilled"),
            data.get("num_joins"),
            data.get("num_scans"),
            data.get("num_aggregations"),
            data.get("source"),
        ]

        # Write data to the CSV file
        with open(
            chunk_file_name, mode="a", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)

            # Write the header only if the file is being created for the first time
            if not file_exists:
                writer.writerow(header)

            # Write the data row
            writer.writerow(row)

        print(f"Data written to chunk: {chunk_file_name}")

    def consume(self):
        """Consume messages from Kafka and process them."""
        try:
            while True:
                print("into consumer")
                # Poll for messages from Kafka
                msg = self.consumer.poll(
                    timeout=1.0
                )  # Adjust timeout if needed
                if msg is None:
                    print(None)
                    continue
                if msg.error():
                    print(f"Error: {msg.error()}")
                    continue

                # Process the message
                print(msg)
                self.process_message(msg.value().decode("utf-8"))
        except KeyboardInterrupt:
            print("Consumption stopped manually.")
        finally:
            self.consumer.close()


"""
if __name__ == "__main__":
    # Define parameters
    kafka_broker = 'localhost:9092'
    kafka_topic = "streamer_dreamers_raw_data"
    group_id = 'data-pipeline-group_2'
    consumer = ConsumerClassCSV(kafka_broker, kafka_topic, group_id)
    consumer.consume()
"""
