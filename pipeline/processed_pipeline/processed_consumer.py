from confluent_kafka import Consumer, KafkaException
import random
import json
import os


class ProcessedConsumer:
    def __init__(self, kafka_config, topic, output_file):
        self.consumer = Consumer(kafka_config)
        self.topic = topic
        self.consumer.subscribe([self.topic])
        self.output_file = output_file
        self.buffer = []
        self.chunk_size = 50

    def save_to_file(self):
        with open(self.output_file, 'a') as f:
            for record in self.buffer:
                f.write(json.dumps(record) + '\n')
        self.buffer = []

    def consume(self):
        try:
            while True:
                msg = self.consumer.poll(1.0)  # Timeout of 1 second
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        continue

                # Process the message
                data = json.loads(msg.value().decode('utf-8'))
                print(f"Consumed message: {data}")
                self.buffer.append(data)
                print(len(self.buffer))
                # Save in chunks
                if len(self.buffer) >= self.chunk_size:
                    self.save_to_file()
        except KeyboardInterrupt:
            pass
        finally:
            if self.buffer:
                self.save_to_file()
            self.consumer.close()