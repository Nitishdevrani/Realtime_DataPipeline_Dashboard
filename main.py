import asyncio
from pipeline.producer_new import ProducerClassDuckDB
from pipeline.consumer_new import ConsumerClass

KAFKA_HOST = "localhost:9092"
KAFKA_TOPIC = "streamer_dreamers_raw_data"


async def main():
    """Main function to run the producer and consumer tasks concurrently."""
    # Instantiate Producer and Consumer
    producer = ProducerClassDuckDB(
        KAFKA_HOST,
        KAFKA_TOPIC,
        "data/provisioned/provisioned_full.parquet",
        "data/serverless/serverless_full.parquet",
        "raw_data",
    )
    producer_task = asyncio.create_task(
        producer.produce_data_in_chunks(
            chunk_size_minutes=0, chunk_size_seconds=10
        )
    )

    consumer = ConsumerClass(KAFKA_HOST, KAFKA_TOPIC, "data-pipeline-group_2")
    consumer_task = asyncio.create_task(consume_and_process(consumer))

    # Run both tasks concurrently
    await asyncio.gather(producer_task, consumer_task)
    producer.close()


async def consume_and_process(consumer: ConsumerClass):
    """Continuously consume data from Kafka and process it."""

    for data, chunk_number in consumer.consume():
        # Process each chunk as it arrives
        print(f"[Consumer] Received chunk #{chunk_number} with data:\n{data}\n")

        # Simulate processing time
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
