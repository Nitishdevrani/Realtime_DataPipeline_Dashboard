# 🚀 **Kafka Real-Time Dashboard with Next.js**  

This project provides a **real-time streaming dashboard** using **Next.js, Kafka, and WebSockets**. It visualizes **live streaming data** processed from Kafka topics and WebSocket connections.  

![Screenshot 2025-02-03 191338](https://github.com/user-attachments/assets/d6527962-92c5-4d77-ba61-5ff738102517)
![Screenshot 2025-02-03 191349](https://github.com/user-attachments/assets/406352af-ba26-4105-8b51-edb53c82f49a)
![Screenshot 2025-02-03 191359](https://github.com/user-attachments/assets/d4b523da-839b-473f-aa39-351e1aadf1ce)


---

## 📌 **Prerequisites**  
Before running this project, ensure you have the following installed on your system:  
- **[Node.js](https://nodejs.org/)** (Recommended: v16 or higher)  
- **[npm](https://www.npmjs.com/)** (Comes with Node.js)  

---

## 🔥 **Installation & Setup**  

### 1️⃣ **Clone or Download the Repository**  
```sh
git clone https://github.com/Nitishdevrani/Realtime_DataPipeline_Dashboard
cd Realtime_DataPipeline_Dashboard
```

### 2️⃣ **Install Dependencies**  
Run the following command in the Realtime_DataPipeline_Dashboard/dashboard directory:  
```sh
npm install
```
This will install all required dependencies for the project.

---

## 🌎 **Environment Configuration**  

Before running the project, you need to set up environment variables for Kafka and WebSockets.  

### 3️⃣ **Create a `.env` file** in the root directory and add the following configurations:  

```ini
# ✅ Kafka Configuration
KAFKA_BROKER=localhost:9092
KAFKA_GROUP_ID=example_group
KAFKA_TOPIC=streamer_dreamers_processed_data

# ✅ WebSocket Configuration
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8080
```
- Replace `localhost:9092` with **your Kafka broker URL** if needed.  
- Replace `ws://localhost:8080` with **your WebSocket server URL**.

---

## 🚀 **Run the Development Server**  

### 4️⃣ **Start the Next.js Project**  
```sh
npm run dev
```
By default, this will start the project on **http://localhost:3000/**.

---

## 🔧 **Troubleshooting WebSocket Issues**  

If you **see the dashboard** but **get a WebSocket connection error**, follow these steps:

1. Open a **new browser tab** and visit:  
   ```
   http://localhost:3000/api/kafka
   ```
2. If you see a message saying **"WebSocket is running"**,  
   - **Go back to `http://localhost:3000`** and refresh the page.  
   - You should now see **real-time data updating on the dashboard.**  

---

## 📜 **How to Get Real-Time Kafka Data?**  

This project depends on **Kafka, Docker, and Backend Services** for data streaming.  
To learn more about setting up Kafka, running backend services, and using Docker for this project, **refer to the README in the parent directory**.  

---

## 🎯 **Key Features**  
✅ **Live Streaming Data** from Kafka using WebSockets  
✅ **Real-Time Query Metrics** with Predictions  
✅ **User-Specific Insights** for Query Analysis  
✅ **Alert System** for Critical Warnings  
✅ **Interactive Data Visualizations** using Charts  

---

## 💡 **Contributing**  
Feel free to contribute to this project by submitting **pull requests, feature requests, or bug reports**.  

---

## 🛠 **License**  
This project is licensed under the **MIT License**.  

---
