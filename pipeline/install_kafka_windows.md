# How to Install Apache Kafka on Windows (Without WSL or Docker)

## Step 1: Install Java
1. Download **JDK (Java Development Kit)** from the [AdoptOpenJDK website](https://adoptopenjdk.net/) or Oracle.
2. Install Java and set the `JAVA_HOME` environment variable:
   - **Variable Name**: `JAVA_HOME`
   - **Variable Value**: Path to your Java installation (e.g., `C:\Program Files\AdoptOpenJDK\jdk-11.0.10.9-hotspot`).
   - Add `%JAVA_HOME%\bin` to the **Path** variable under **System Variables**.
3. Verify Java installation by running the following command in the **Command Prompt**:
   ```bash
   java -version


## Step 2: Download, Extract, and Manage Kafka
1. Download the latest Kafka release from the [Apache Kafka Downloads page](https://kafka.apache.org/downloads).
2. Extract the Kafka archive (e.g., `kafka_2.13-2.8.0.tgz`) to a folder (e.g., `C:\kafka`).
3. To stop Kafka or Zookeeper after running them:
   - Go to the respective Command Prompt window and press **Ctrl + C**.

---

## Step 3: Install Zookeeper (Kafka Dependency)
Kafka requires **Zookeeper**, which is bundled with Kafka. No separate installation is necessary:
1. Navigate to the Kafka folder (`C:\kafka`) and open the `config` directory.
2. Locate the `zookeeper.properties` file, which is already configured for basic usage.

---

## Step 4: Start Zookeeper
1. Open **Command Prompt** and navigate to your Kafka directory:
   ```bash
   cd C:\kafka\kafka_2.13-2.8.0
   ```
2. Start Zookeeper using the following command:
    ```bash   
    bin\windows\zookeeper-server-start.bat config\zookeeper.properties
    ```

## Step 5: Start Kafka Server

1. Open a **new Command Prompt window** and navigate to your Kafka directory:
   ```bash
   cd C:\kafka\kafka_2.13-2.8.0
   ```
2. Start the Kafka server using the following command:
    ```bash
    bin\windows\kafka-server-start.bat config\server.properties

    ```
3. The Kafka server will start and run on localhost:9092 by default. You should see logs indicating that the server has started successfully.

4. Leave this Command Prompt window open while using Kafka.






