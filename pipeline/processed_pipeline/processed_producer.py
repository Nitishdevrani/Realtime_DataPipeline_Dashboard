import json
from confluent_kafka import Producer
import pandas as pd


class ProcessedProducer:
    def __init__(self, kafka_host, topic):
        self.producer = Producer(
            {
                "bootstrap.servers": kafka_host,
                "queue.buffering.max.kbytes": 1048576,
            }
        )
        self.topic = topic

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def produce(self, data: pd.DataFrame):
        # for key, value in data.items():
        #     message = json.dumps({key: value})
        #     self.producer.produce(
        #         self.topic, value=message, callback=self.delivery_report
        #     )
        self.producer.produce(
            self.topic,
            value=data.to_json(orient="records")[0],
            callback=self.delivery_report,
        )
        self.producer.flush()
