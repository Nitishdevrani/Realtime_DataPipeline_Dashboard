"Main File to run the complete pipeline"
from pipeline.producer_new import ProducerClassDuckDB

KAFKA_HOST = "localhost:9092"
KAFKA_TOPIC = "streamer_dreamers_raw_data"

if __name__ == "__main__":
    # Kafka Producer for raw data
    producer = ProducerClassDuckDB(
        KAFKA_HOST,
        KAFKA_TOPIC,
        "data/provisioned/provisioned_full.parquet",
        "data/serverless/serverless_full.parquet",
        "raw_data",
    )
    print(producer._get_timestamp_range())