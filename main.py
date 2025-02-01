""" Main script to run the producer and consumer tasks concurrently. """

import asyncio
import pickle
import time
from functools import lru_cache

import pandas as pd
from pipeline.producer_new import ProducerClassDuckDB
from pipeline.consumer_new import ConsumerClass
from pipeline.processed_pipeline.processed_producer import ProcessedProducer
from cleaning.clean_data_new import clean_data
from processing.processing import process_dataframe
from processing.workload_state import WorkloadState

KAFKA_HOST = "localhost:9092"
KAFKA_TOPIC_RAW = "streamer_dreamers_raw_data"
KAFKA_TOPIC_PROCESSED = "streamer_dreamers_processed_data"


@lru_cache(maxsize=128)
def clean_data_cached(df_pickle: bytes) -> pd.DataFrame:
    """Cache cleaning based on the bytes of the DataFrame."""
    df = pickle.loads(df_pickle)
    return clean_data(df)


def get_cleaned_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Convert into a hashable form and clean it using the cached function."""
    df_pickle = pickle.dumps(raw_df)
    return clean_data_cached(df_pickle)


async def main():
    """Main function to run the producer and consumer tasks concurrently."""
    producer = ProducerClassDuckDB(
        KAFKA_HOST,
        KAFKA_TOPIC_RAW,
        "data/provisioned/provisioned_full.parquet",
        "data/serverless/serverless_full.parquet",
        "raw_data",
    )
    producer_task = asyncio.create_task(
        producer.produce_data_in_chunks(
            chunk_size_minutes=60, chunk_size_seconds=0
        )
    )

    consumer = ConsumerClass(
        KAFKA_HOST, KAFKA_TOPIC_RAW, "data-pipeline-group_2"
    )
    consumer_task = asyncio.create_task(consume_and_process(consumer))

    # Run both tasks concurrently
    await asyncio.gather(producer_task, consumer_task)
    producer.close()


async def consume_and_process(consumer: ConsumerClass):
    """Continuously consume data from Kafka and process it."""
    processed_producer = ProcessedProducer(KAFKA_HOST, KAFKA_TOPIC_PROCESSED)

    workload_state = WorkloadState()
    window_duration = 10.0
    window_start_time = time.time()

    for data, _ in consumer.consume():
        cleaned_data = get_cleaned_data(data)

        processed_data = await process_dataframe(cleaned_data, workload_state)

        current_time = time.time()
        if current_time - window_start_time >= window_duration:
            processed_producer.produce(processed_data)
            print(f"Produced aggregated snapshot at {current_time}")

            workload_state.reset_state()
            window_start_time = current_time

        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
