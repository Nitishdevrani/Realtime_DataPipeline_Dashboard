""" Main script to run the producer and consumer tasks concurrently. """

import asyncio
from cleaning.clean_data_new import clean_data
from pipeline.producer_new import ProducerClassDuckDB
from pipeline.consumer_new import ConsumerClass
from pipeline.processed_pipeline.processed_producer import ProcessedProducer
from processing.processing import process_dataframe

KAFKA_HOST = "localhost:9092"
KAFKA_TOPIC_RAW = "streamer_dreamers_raw_data"
KAFKA_TOPIC_PROCESSED = "streamer_dreamers_processed_data"


async def main():
    """Main function to run the producer and consumer tasks concurrently."""
    # Instantiate Producer and Consumer for simulation rt-data
    producer = ProducerClassDuckDB(
        KAFKA_HOST,
        KAFKA_TOPIC_RAW,
        "data/provisioned/provisioned_full.parquet",
        "data/serverless/serverless_full.parquet",
        "raw_data",
    )
    producer_task = asyncio.create_task(
        producer.produce_data_in_chunks(
            chunk_size_minutes=0, chunk_size_seconds=10
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
    # init processed producer
    processed_producer = ProcessedProducer(KAFKA_HOST, KAFKA_TOPIC_PROCESSED)

    for data, chunk_number in consumer.consume():
        # Process each chunk as it arrives
        print(f"[Consumer] Received chunk #{chunk_number} with data:\n{data}\n")

        cleaned_data = clean_data(data)
        
        processed_data = await process_dataframe(cleaned_data)

        # print(f"[Consumer] Processed data:\n{processed_data}\n")
        processed_producer.produce(processed_data)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
