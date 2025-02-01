"use client";

import { KafkaData, KafkaDataStream, OverallData, Users } from "@/utils/KafkaData";
import { useEffect, useState } from "react";

const useKafkaWebSocket = () => {
  // const [messages, setMessages] = useState<KafkaDataStream>([]);
  const [overallData, setOverallData] = useState<OverallData[]>([]);
  const [usersData, setUsersData] = useState<Users[]>([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8080"); // WebSocket URL
    ws.onopen = () => {
        console.log("✅ Connected to WebSocket:", "ws://localhost:8080");
      };
  
      ws.onerror = (error) => {
        console.error("❌ WebSocket error:", error);
      };
    ws.onmessage = (event) => {
      try {
        const {users, overall}: KafkaData = JSON.parse(event.data);
        console.log('overall',overall);
        const extractedOverall = Object.values(overall)[0];

        setOverallData((prev) => [...prev.slice(-50), extractedOverall]); // Keep last 50 messages
        setUsersData((prev) => [...prev.slice(-50), users]); // Keep last 50 messages

      } catch (error) {
        console.error("Error parsing Kafka data:", error);
      }
    };
    ws.onclose = () => {
        console.log("❌ WebSocket closed. Reconnecting in 3s...");
        // setTimeout(() => useKafkaWebSocket(), 3000); // ✅ Auto-reconnect after 3s
      };
    return () => ws.close(); // Cleanup on unmount
  }, []);

  return {usersData, overallData};
};

export default useKafkaWebSocket;
