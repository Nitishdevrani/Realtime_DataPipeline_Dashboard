""" Main script to run the producer and consumer tasks concurrently. """

import asyncio
import pickle
from functools import lru_cache

import pandas as pd
from pipeline.producer_new import ProducerClassDuckDB
from pipeline.consumer_new import ConsumerClass
from pipeline.processed_pipeline.processed_producer import ProcessedProducer
from cleaning.clean_data import clean_data
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

    # Automatic Replay
    producer = ProducerClassDuckDB(
        KAFKA_HOST,
        KAFKA_TOPIC_RAW,
        "data/provisioned/provisioned_full.parquet",
        "data/serverless/serverless_full.parquet",
        "raw_data",
    )
    producer_task = asyncio.create_task(
        producer.produce_data_in_chunks(
            chunk_size_minutes=5, chunk_size_seconds=0
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

    # Initialize the processed data producer to send data to the dashboard
    processed_producer = ProcessedProducer(KAFKA_HOST, KAFKA_TOPIC_PROCESSED)

    # Keeps track of the accumulated data for each user and overall data
    workload_state = WorkloadState()
    # Defines how big the window of aggregation is before resetting the state
    window_duration = 10.0

    for data, _ in consumer.consume():
        # Clean the data
        cleaned_data = get_cleaned_data(data)

        # Process the data
        processed_data = await process_dataframe(cleaned_data, workload_state)

        # Send to the dashboard asynchronously and save the state
        overall_ts = processed_data["timestamp"].iloc[0]
        if overall_ts is not None:
            # convert to a Python datetime if type = pandas Timestamp
            overall_dt = (
                overall_ts.to_pydatetime()
                if isinstance(overall_ts, pd.Timestamp)
                else overall_ts
            )

            # if this is the first valid timestamp
            if workload_state.last_backup_timestamp is None:
                print("initializing last_backup_timestamp")
                workload_state.last_backup_timestamp = overall_dt
            # Calculate the elapsed time in seconds.
            elapsed = (
                overall_dt - workload_state.last_backup_timestamp
            ).total_seconds()

            # Save and send the data if the window duration has passed
            if elapsed >= window_duration:
                # Upload the processed data to the dashboard
                processed_producer.produce(processed_data)
                print(f"Produced aggregated snapshot at {overall_ts}")

                # Reset the state and save it
                workload_state.reset_state()
                asyncio.create_task(workload_state.save_state())
                workload_state.last_backup_timestamp = overall_ts

        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
