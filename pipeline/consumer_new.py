""" Kafka Consumer for raw data """

import json
from datetime import datetime
from typing import Any, Generator, List
from confluent_kafka import Consumer
import pandas as pd


class ConsumerClass:
    """Kafka Consumer for raw data"""

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

    def process_message(self, message) -> tuple[pd.DataFrame, str]:
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

        # Convert the data to a DataFrame
        df = pd.DataFrame([data])
        # Save the data by chunk number (to a CSV file)
        # self.save_to_csv(data, chunk_number)
        return df, chunk_number

    def get_chunk_number(self, timestamp) -> str:
        """Calculate the chunk number based on the timestamp."""
        if isinstance(timestamp, datetime):
            return timestamp.strftime(
                "%Y-%m-%d"
            )  # Format datetime as a date string
        return timestamp.split("T")[
            0
        ]  # If it's already a string, split by 'T'  # Use the date part as the chunk identifier

    def consume(self) -> Generator[tuple[pd.DataFrame, str], None, None]:
        """Consume messages from Kafka and process them."""
        try:
            while True:
                # print("into consumer")
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
                # print(msg)
                yield self.process_message(msg.value().decode("utf-8"))
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
