from confluent_kafka import Consumer, KafkaError
import json
import random

class KafkaConsumer:
    def __init__(self, broker, group_id, topic):
        self.consumer = Consumer({
            'bootstrap.servers': broker,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.topic = topic

    def consume_data(self):
        self.consumer.subscribe([self.topic])

        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        break

                print(f"Received message: {msg.value().decode('utf-8')}")
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()


# Example usage
"""
if __name__ == "__main__":
    consumer = KafkaConsumer(broker=kafka_host,
                            group_id='assignment5teachers' + str(random.random()),
                            topic=kafka_topic)
    consumer.consume_data()
"""
