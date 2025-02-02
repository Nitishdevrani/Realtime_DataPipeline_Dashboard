"use client";

import { KafkaData, KafkaDataStream, Users } from "@/utils/KafkaData";
import { useEffect, useState } from "react";

const useKafkaWebSocket = () => {
  const [incomingData, setIncomingData] = useState<KafkaDataStream>([]);
  // const [overallData, setOverallData] = useState<OverallData[]>([]);
  // const [usersData, setUsersData] = useState<Users[]>([]);
  const [userList, setUserList] = useState<Record<string, Users[]>>({});
  const [avgQueryCount, setAvgQueryCount] = useState<
    { timestamp: number; avg_query_count: number; avg_spilled: number }[]
  >([]);
  const [predictedData, setPredictedData] = useState<
    { timestamp: number; predicted_value: number }[]
  >([]);
  const [realDataCounter, setRealDataCounter] = useState(0); // 🔥 Track real data count since last prediction append
  const [futurePredictions, setFuturePredictions] = useState<
    { timestamp: number; predicted_value: number }[]
  >([]);

  // Spilled States
  const [predictedDataSpilled, setPredictedDataSpilled] = useState<
    { timestamp: number; predicted_value: number }[]
  >([]);
  const [realDataCounterSpilled, setRealDataCounterSpilled] = useState(0); // 🔥 Track real data count since last prediction append
  const [futurePredictionsSpilled, setFuturePredictionsSpilled] = useState<
    { timestamp: number; predicted_value: number }[]
  >([]);

  const [alertsHistory, setAlertsHistory] = useState<
    { timestamp: number; alert: string }[]
  >([]);

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
        const {
          users,
          predicted_query_count,
          timestamp,
          avg_query_count,
          predicted_spill,
          avg_spilled,
          alerts,
        } = extractedInData;

        if(alerts.length > 0){
          setAlertsHistory((prev) => [
            ...prev,
            { timestamp: timestamp, alert: alerts[0] },
          ]);
        }

        let currentUsers = Object.entries(users);

        setUserList((prev) => {
          let updatedUsers: Record<string, Users[]> = { ...prev };

          if (currentUsers.length > 0) {
            for (const [key, value] of currentUsers as [string, Users][]) {
              // Explicitly cast value as Users
              if (key in updatedUsers) {
                updatedUsers[key] = [...updatedUsers[key].slice(-10), value]; // Append new data
              } else {
                updatedUsers[key] = [value]; // Create new array for a new user
              }
            }
          }

          return updatedUsers;
        });

        setAvgQueryCount((prev) => [
          ...prev.slice(-25),
          { timestamp, avg_query_count, avg_spilled },
        ]);

        setRealDataCounter((prev) => prev + 1); // Increment real data counter
        setRealDataCounterSpilled((prev) => prev + 1);
        // 🔥 2️⃣ Handle Predicted Data
        if (predicted_query_count.length > 0) {
          // Reset counter because a new prediction set arrived
          setRealDataCounter(0);

          const newPredictions = predicted_query_count.map(
            (value: number, index: number) => ({
              timestamp: timestamp + index * 10_000, // 🔹 Offset by 10 sec each
              predicted_value: value,
            })
          );

          // Store only 10 for immediate display, keep the rest for later
          setPredictedData(newPredictions.slice(0, 10)); // Show first 10 predictions
          setFuturePredictions(newPredictions.slice(10)); // Store remaining 90 for later
        } else {
          // 🔥 3️⃣ Append Future Predictions After 10 Real Data Points
          if (realDataCounter >= 10 && futurePredictions.length > 0) {
            setPredictedData(futurePredictions.slice(0, 10)); // Show next 10
            setFuturePredictions(futurePredictions.slice(10)); // Remove used ones
            setRealDataCounter(0); // Reset counter
          }
        }

        if (predicted_spill.length > 0) {
          // Reset counter because a new prediction set arrived
          setRealDataCounterSpilled(0);

          const newPredictions = predicted_spill.map(
            (value: number, index: number) => ({
              timestamp: timestamp + index * 10_000, // 🔹 Offset by 10 sec each
              predicted_value: value,
            })
          );

          // Store only 10 for immediate display, keep the rest for later
          setPredictedDataSpilled(newPredictions.slice(0, 10)); // Show first 10 predictions
          setFuturePredictionsSpilled(newPredictions.slice(10)); // Store remaining 90 for later
        } else {
          // 🔥 3️⃣ Append Future Predictions After 10 Real Data Points
          if (
            realDataCounterSpilled >= 10 &&
            futurePredictionsSpilled.length > 0
          ) {
            setPredictedDataSpilled(futurePredictions.slice(0, 10)); // Show next 10
            setFuturePredictionsSpilled(futurePredictions.slice(10)); // Remove used ones
            setRealDataCounterSpilled(0); // Reset counter
          }
        }
        // ======================================Prediction End

        // setUsersData((prev) => [...prev.slice(-10), users]); // Keep last 50 messages
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

  return {
    incomingData,
    userList,
    predictedData,
    avgQueryCount,
    predictedDataSpilled,
    alertsHistory
  };
};

export default useKafkaWebSocket;
