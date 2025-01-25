import pandas as pd
import time
from confluent_kafka import Producer


class KafkaProducer:
    def __init__(self, broker, topic):
        self.producer = Producer({'bootstrap.servers': broker})
        self.topic = topic

    def load_data(self, file_path):
        self.data = pd.read_parquet(file_path)
        print(self.data.shape)
    def prepare_data(self):
        start_time = pd.Timestamp.now()
        end_time = start_time + pd.Timedelta(hours=3)
        original_start = self.data['arrival_timestamp'].min()
        original_end = self.data['arrival_timestamp'].max()
        
        self.data['arrival_timestamp'] = pd.to_datetime(self.data['arrival_timestamp'])
        
        self.data['simulated_timestamp'] = self.data['arrival_timestamp'].apply(
                lambda ts: start_time + ((ts - original_start) / (original_end - original_start)) * (end_time - start_time)
        )
        self.data = self.data.sort_values('simulated_timestamp')

    def send_data(self):
        for _, row in self.data.iterrows():
            message = row.to_json()
            self.producer.produce(self.topic, value=message)
            time.sleep(0.001)  # Adjust speed as needed
        self.producer.produce(self.topic, value="__END__")
        print("sent data signal")
        self.producer.flush()

"""      
kafka_host = "localhost:9092"
kafka_topic = "stream_dreamers_test_new_1"
producer = KafkaProducer(broker=kafka_host,
                             topic=kafka_topic)
producer.load_data('sample_0.001_serverless.parquet')
producer.prepare_data()
producer.send_data()
"""