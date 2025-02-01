import { NextResponse } from "next/server";
import { Kafka } from "kafkajs";
import { WebSocketServer } from "ws";

// ✅ Initialize WebSocket Server
let wss: WebSocketServer | null = null;
if (!wss) {
  wss = new WebSocketServer({ port: 8080 });
}

wss.on("connection", (ws) => {
  console.log("🔗 WebSocket client connected");
  ws.on("close", () => console.log("❌ WebSocket client disconnected"));
});

// ✅ Kafka Consumer Setup
const kafka = new Kafka({
  clientId: "nextjs-consumer",
  brokers: [process.env.KAFKA_BROKER || "localhost:9092"],
});

const consumer = kafka.consumer({
  groupId: process.env.KAFKA_GROUP_ID || "example_group",
});

const topic = process.env.KAFKA_TOPIC || "stream_dreamers_processed";

// ✅ Kafka Consumer Function
const runConsumer = async () => {
  console.log("🚀 Kafka Consumer Starting...");
  await consumer.connect();
  await consumer.subscribe({ topic, fromBeginning: true });

  await consumer.run({
    eachMessage: async ({ message }) => {
      const receivedData = message.value?.toString() || "⚠️ Empty Message";
      // console.log(`📩 Kafka Log: ${receivedData}`);

      // ✅ Send log to all WebSocket clients
      wss?.clients.forEach((client) => {
        if (client.readyState === 1) {
          client.send(receivedData);
        }
      });
    },
  });
};

// ✅ Start Kafka Consumer (Run only once)
runConsumer().catch((err)=>{
  console.log('errrorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',err);
  
  // console.error
});

// ✅ API Route (Keep for Debugging)
export async function GET() {
  return new Response(JSON.stringify({ message: "WebSocket Server Running" }), { status: 200 });
}
