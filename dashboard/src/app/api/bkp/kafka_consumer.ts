// import { NextResponse } from "next/server";
// import { Kafka } from "kafkajs";

// // ✅ Kafka Connection Setup
// const kafka = new Kafka({
//   clientId: "nextjs-consumer",
//   brokers: ["dep-eng-data-s-heimgarten.hosts.utn.de:9092"], // ✅ Use your Kafka broker
// });

// const consumer = kafka.consumer({
//   groupId: "example_group",
// });

// // const topic = "nytd";
// const topic = "stream_dreamers_processed";

// // ✅ Array to store logs temporarily
// let kafkaLogs: string[] = [];

// // ✅ Kafka Consumer Function
// const runConsumer = async () => {
//   await consumer.connect();
//   await consumer.subscribe({ topic, fromBeginning: true });

//   await consumer.run({
//     eachMessage: async ({ message }) => {
//       const receivedData = message.value?.toString() || "⚠️ Empty Message";
//       console.log(`📩 Kafka Log: ${receivedData}`);

//       // ✅ Store only the last 50 logs
//       kafkaLogs = [...kafkaLogs.slice(-49), receivedData];
//     },
//   });
// };

// // ✅ Start Kafka Consumer (Run only once)
// runConsumer().catch(console.error);

// // ✅ API Route: Serve Live Kafka Logs
// export async function GET() {
//   return NextResponse.json({ logs: kafkaLogs });
// }