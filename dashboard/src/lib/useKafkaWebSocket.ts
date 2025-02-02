"use client";

import { KafkaData, KafkaDataStream, Users } from "@/utils/KafkaData";
import { useEffect, useState } from "react";

const useKafkaWebSocket = () => {
  const [incomingData, setIncomingData] = useState<KafkaDataStream>([]);
  // const [overallData, setOverallData] = useState<OverallData[]>([]);
  const [usersData, setUsersData] = useState<Users[]>([]);
  const [userList, setUserList] = useState<Record<string, Users[]>>({});
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
        // console.log('rawDATA',event);
        
        const KafkaDataIncoming: KafkaData = JSON.parse(event.data);
        // console.log('completeData',KafkaDataIncoming);
        const extractedInData = Object.values(KafkaDataIncoming)[0];
        const {users} = extractedInData;
        let currentUsers = Object.entries(users);
        
        setUserList((prev) => {
          let updatedUsers: Record<string, Users[]> = { ...prev };
        
          if (currentUsers.length > 0) {
            for (const [key, value] of currentUsers as [string, Users][]) {  // Explicitly cast value as Users
              if (key in updatedUsers) {
                updatedUsers[key] = [...updatedUsers[key].slice(-10), value]; // Append new data
              } else {
                updatedUsers[key] = [value]; // Create new array for a new user
              }
            }
          }
        
          return updatedUsers;
        });
        
        setUsersData((prev) => [...prev.slice(-10), users]); // Keep last 50 messages
        setIncomingData((prev) => [...prev.slice(-10), extractedInData]); // Keep last 50 messages

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

  return {incomingData, usersData, userList};
};

export default useKafkaWebSocket;
