from confluent_kafka import Consumer, KafkaError
from datetime import datetime, timedelta
import random
import json
import csv
import os


class KafkaConsumer:
    def __init__(self, broker, group_id, topic, output_dir):
        self.consumer = Consumer({
            'bootstrap.servers': broker,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.topic = topic
        self.output_dir = output_dir
        self.max_chunks = 20
        self.max_rows_per_chunk = 10000
        self.chunk_index = 0
        self.chunk_files = []

    def consume_data(self):
        print(self.topic)
        self.consumer.subscribe([self.topic])
        chunk_row_count = 0
        chunk_file = None
        csv_writer = None

        try:
            while True:
                msg = self.consumer.poll(1.0)
                print(msg)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        break

                try:
                    data = msg.value().decode('utf-8', errors='replace')
                    if data == "__END__":
                        print("End of data signal received. Stopping consumer.")
                        break

                    data_dict = json.loads(data)  # Convert JSON string to dictionary
                    #print(data_dict)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}. Skipping message.")
                    continue

                # Create a new chunk file if necessary
                if chunk_row_count == 0 or chunk_row_count >= self.max_rows_per_chunk:
                    if chunk_file:
                        chunk_file.close()

                    self.chunk_index += 1
                    if len(self.chunk_files) >= self.max_chunks:
                        # Overwrite the oldest chunk file
                        oldest_chunk = self.chunk_files.pop(0)
                        os.remove(oldest_chunk)

                    chunk_file_path = os.path.join(self.output_dir, f"chunk_{self.chunk_index}.csv")
                    self.chunk_files.append(chunk_file_path)

                    chunk_file = open(chunk_file_path, mode='w', newline='', encoding='utf-8')
                    csv_writer = csv.DictWriter(chunk_file, fieldnames=data_dict.keys())
                    csv_writer.writeheader()
                    chunk_row_count = 0

                # Write the row to the current chunk
                csv_writer.writerow(data_dict)
                chunk_row_count += 1

        except KeyboardInterrupt:
            pass
        finally:
            if chunk_file:
                chunk_file.close()
            self.consumer.close()
"""
kafka_host = "localhost:9092"
kafka_topic = "stream_dreamers_test_new_1"
consumer = KafkaConsumer(broker=kafka_host,
                            group_id='assignment5teachers' + str(random.random()),
                            topic=kafka_topic,
                            output_dir ='output/')
consumer.consume_data()
"""