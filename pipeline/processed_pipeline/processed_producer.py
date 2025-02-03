import json
from confluent_kafka import Producer
import pandas as pd


class ProcessedProducer:
    def __init__(self, kafka_host, topic):
        self.producer = Producer(
            {
                "bootstrap.servers": kafka_host,
                "queue.buffering.max.kbytes": 1048576, # increase the buffer size to 1Gb
            }
        )
        self.topic = topic

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def produce(self, data: pd.DataFrame):
        # send the data to the Kafka topic
        self.producer.produce(
            self.topic,
            value=data.to_json(orient="records"),
            callback=self.delivery_report,
        )
        # Ensures all messages in the producer's buffer
        #  are sent before proceeding
        self.producer.flush()
