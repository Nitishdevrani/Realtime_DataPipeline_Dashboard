import json
from confluent_kafka import Producer


class ProcessedProducer:
    def __init__(self, kafka_config, topic):
        self.producer = Producer(kafka_config)
        self.topic = topic

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def produce(self, data):
        for key, value in data.items():
            message = json.dumps({key: value})
            self.producer.produce(
                self.topic, value=message, callback=self.delivery_report
            )
        self.producer.flush()
