from producer import KafkaProducer
from consumer import KafkaConsumer
import random
import os

kafka_host = "dep-eng-data-s-heimgarten.hosts.utn.de:9092"
kafka_topic = "stream_dreamers_test"

if __name__ == "__main__":
    # Kafka Producer
    producer = KafkaProducer(broker=kafka_host,
                             topic=kafka_topic)
    producer.load_data('data/provisioned/sample_0.001_provisioned.parquet')
    producer.prepare_data()
    producer.send_data()
    os.makedirs('output_chunks', exist_ok=True)
    # Kafka Consumer
    consumer = KafkaConsumer(broker=kafka_host,
                            group_id='assignment5teachers' + str(random.random()),
                            topic=kafka_topic)
    consumer.consume_data()