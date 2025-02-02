$CONTAINER_NAME = "kafkaserver"

# Check if Docker is installed
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed or not in PATH. Please install Docker and try again." -ForegroundColor Red
    exit 1
}

# Check if the container exists
$containerExists = docker ps -aq -f "name=^$CONTAINER_NAME$"
if ($containerExists) {
    # Check if the container is running
    $containerRunning = docker ps -q -f "name=^$CONTAINER_NAME$"
    if ($containerRunning) {
        Write-Host "✅ Container '$CONTAINER_NAME' is already running."
    } else {
        Write-Host "🔄 Container '$CONTAINER_NAME' exists but is stopped. Starting it..."
        docker start $CONTAINER_NAME
    }
} else {
    Write-Host "🚀 Container '$CONTAINER_NAME' does not exist. Creating and starting it..."
    docker run -d --name $CONTAINER_NAME --network kafka-network `
        -e KAFKA_PROCESS_ROLES=broker,controller `
        -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER `
        -e KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 `
        -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 `
        -e KAFKA_NODE_ID=1 `
        -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 `
        -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 `
        -e KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1 `
        -e KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1 `
        -p 9092:9092 apache/kafka:latest
}
