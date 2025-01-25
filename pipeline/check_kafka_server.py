from confluent_kafka.admin import AdminClient

def check_broker_connection(broker):
    try:
        admin_client = AdminClient({'bootstrap.servers': broker})
        cluster_metadata = admin_client.list_topics(timeout=5)
        print(f"Connected to Kafka broker at {broker}. Available topics: {list(cluster_metadata.topics.keys())}")
    except Exception as e:
        print(f"Failed to connect to Kafka broker at {broker}: {e}")

if __name__ == "__main__":
    broker = 'localhost:9092'

    # Check Kafka broker connectivity
    check_broker_connection(broker)
