from processed_producer import ProcessedProducer
from processed_consumer import ProcessedConsumer
import random
import os
import json


kafka_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'example_group',
        'auto.offset.reset': 'earliest'
    }
kafka_topic = "processed_data_topic"

if __name__ == "__main__":
    # Kafka Producer
    with open('data/fake_json_processed_data/example_data.json', 'r') as f:
        data = json.load(f)

    producer = ProcessedProducer(kafka_config,
                                 kafka_topic)
    producer.produce(data)
    os.makedirs('processed_chunks', exist_ok=True)
    # Kafka Consumer
    output_file = 'processed_chunks/output_data.json'
    consumer = ProcessedConsumer(kafka_config,
                                 kafka_topic,
                                 output_file)
    consumer.consume()