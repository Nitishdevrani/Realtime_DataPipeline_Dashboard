from confluent_kafka import Producer
import duckdb
import json
import pandas as pd
from datetime import datetime, timedelta


class ProducerClassDuckDB:
    def __init__(
        self,
        kafka_broker,
        kafka_topic,
        provisioned_file,
        serverless_file,
        table_name,
    ):
        self.producer = Producer(
            {
                "bootstrap.servers": kafka_broker,
                "queue.buffering.max.kbytes": 1048576,
            }
        )
        self.topic = kafka_topic
        self.kafka_topic = kafka_topic
        self.table_name = table_name
        provisioned = pd.read_parquet(provisioned_file)
        provisioned["source"] = "provisioned"
        serverless = pd.read_parquet(serverless_file)
        serverless["source"] = "serverless"
        concatenated_file = pd.concat([provisioned, serverless])
        print(concatenated_file.shape)
        self.conn = duckdb.connect("producer.duckdb")
        self.conn.execute(f"DROP TABLE IF EXISTS {table_name} ;")
        self.conn.register("full_data", concatenated_file)
        self.conn.execute(
            f"CREATE TABLE '{table_name}' AS SELECT * FROM full_data;"
        )
        result = self.conn.execute(
            f"SELECT COUNT(*) FROM {table_name};"
        ).fetchall()
        print(result)

    def _get_timestamp_range(self):
        """Fetch the minimum and maximum timestamps from the table."""
        query = f"SELECT MIN(arrival_timestamp), MAX(arrival_timestamp) FROM {self.table_name};"
        min_timestamp, max_timestamp = self.conn.execute(query).fetchone()

        # Ensure min_timestamp and max_timestamp are datetime objects
        min_timestamp = datetime.fromisoformat(str(min_timestamp))
        max_timestamp = datetime.fromisoformat(str(max_timestamp))

        return min_timestamp, max_timestamp

    def produce_data_in_chunks(self, chunk_size_days=1):
        """Fetch and produce data to Kafka in chunks."""
        # Get the timestamp range
        min_datetime, max_datetime = self._get_timestamp_range()
        chunk_size = timedelta(days=chunk_size_days)

        current_start = min_datetime
        while current_start <= max_datetime:
            current_end = current_start + chunk_size

            # Query the current chunk
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE arrival_timestamp >= '{current_start.isoformat()}' 
                AND arrival_timestamp < '{current_end.isoformat()}';
            """
            chunk = self.conn.execute(query).fetchall()
            print(len(chunk))
            for row in chunk:
                # Convert datetime objects to strings (ISO format) in the row before serializing
                row_dict = dict(
                    zip([desc[0] for desc in self.conn.description], row)
                )
                # Convert datetime values to isoformat strings
                for key, value in row_dict.items():
                    if isinstance(value, datetime):
                        row_dict[key] = value.isoformat()

                # Serialize the dictionary to a JSON string
                message = json.dumps(row_dict)
                self.producer.produce(self.kafka_topic, value=message)
                # print(f"Produced: {message}")

            self.producer.flush()
            current_start = current_end

        print("All chunks processed and sent to Kafka!")

    def close(self):
        """Close DuckDB connection and flush producer."""
        self.conn.close()
        self.producer.flush()


"""
if __name__ == "__main__":
    kafka_host = "localhost:9092"
    kafka_topic = "streamer_dreamers_raw"

    serverless_file = "sample_0.001_serverless.parquet"
    provisioned_file = "sample_0.001_provisioned.parquet"
    producer = ProducerClassDuckDB(kafka_host, kafka_topic, provisioned_file,serverless_file, 'aws_data1')
    producer.produce_data_in_chunks(1)
"""
