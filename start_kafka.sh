#!/bin/bash

CONTAINER_NAME="kafkaserver"

# Check if the container exists
if [ $(sudo docker ps -aq -f name=^${CONTAINER_NAME}$) ]; then
    # Check if the container is running
    if [ $(sudo docker ps -q -f name=^${CONTAINER_NAME}$) ]; then
        echo "Container '${CONTAINER_NAME}' is already running."
    else
        echo "Container '${CONTAINER_NAME}' exists but is stopped. Starting it..."
        sudo docker start ${CONTAINER_NAME}
    fi
else
    echo "Container '${CONTAINER_NAME}' does not exist. Creating and starting it..."
    sudo docker run -d --name kafkaserver --network kafka-network \
        -e KAFKA_PROCESS_ROLES=broker,controller \
        -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER \
        -e KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
        -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 \
        -e KAFKA_NODE_ID=1 \
        -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
        -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
        -e KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1 \
        -e KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1 \
        -p 9092:9092 apache/kafka:latest
fi
