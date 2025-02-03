"use client";

import { KafkaData, KafkaDataStream, Users } from "@/utils/KafkaData";
import { useEffect, useState } from "react";

/**
 * Custom React hook to handle real-time Kafka WebSocket data.
 * This manages incoming Kafka data, user lists, average query counts,
 * predicted data, spilled predictions, and alert history.
 */
const useKafkaWebSocket = () => {
  // Stores the latest streaming Kafka data
  const [incomingData, setIncomingData] = useState<KafkaDataStream>([]);

  // Stores users and their data history
  const [userList, setUserList] = useState<Record<string, Users[]>>({});

  // Stores average query count and spilled values over time
  const [avgQueryCount, setAvgQueryCount] = useState<
    { timestamp: number; avg_query_count: number; avg_spilled: number }[]
  >([]);

  // Stores predicted query count data (future values)
  const [predictedData, setPredictedData] = useState<
    { timestamp: number; predicted_value: number }[]
  >([]);
  const [realDataCounter, setRealDataCounter] = useState(0); // Tracks real data count since last prediction append
  const [futurePredictions, setFuturePredictions] = useState<
    { timestamp: number; predicted_value: number }[]
  >([]);

  // Stores predicted spilled data (future values)
  const [predictedDataSpilled, setPredictedDataSpilled] = useState<
    { timestamp: number; predicted_value: number }[]
  >([]);
  const [realDataCounterSpilled, setRealDataCounterSpilled] = useState(0);
  const [futurePredictionsSpilled, setFuturePredictionsSpilled] = useState<
    { timestamp: number; predicted_value: number }[]
  >([]);

  // Stores alert messages with timestamps
  const [alertsHistory, setAlertsHistory] = useState<
    { timestamp: number; alert: string }[]
  >([]);

  /**
   * Establish WebSocket connection to listen for real-time Kafka data.
   */
  useEffect(() => {
    const ws = new WebSocket(
      process.env.NEXT_PUBLIC_WEBSOCKET_URL || "ws://localhost:8080"
    ); // WebSocket URL

    ws.onopen = () => {
      console.log(
        "✅ Connected to WebSocket:",
        process.env.NEXT_PUBLIC_WEBSOCKET_URL
      );
    };

    ws.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
    };

    ws.onmessage = (event) => {
      try {
        // Parse incoming Kafka message
        const KafkaDataIncoming: KafkaData = JSON.parse(event.data);
        const extractedInData = Object.values(KafkaDataIncoming)[0];

        // Destructure key values from Kafka data
        const {
          users,
          predicted_query_count,
          timestamp,
          avg_query_count,
          predicted_spill,
          avg_spilled,
          alerts,
        } = extractedInData;

        // 🔥 Handle Alerts: Store only unique alerts
        if (alerts?.length > 0) {
          setAlertsHistory((prev) => [
            ...prev,
            { timestamp: timestamp, alert: alerts[0] },
          ]);
        }

        // 🔥 Manage Users: Append new data for existing users & add new users dynamically
        setUserList((prev) => {
          let updatedUsers: Record<string, Users[]> = { ...prev };
          let currentUsers = Object.entries(users);

          if (currentUsers?.length > 0) {
            for (const [key, value] of currentUsers as [string, Users][]) {
              if (key in updatedUsers) {
                updatedUsers[key] = [...updatedUsers[key].slice(-10), value]; // Keep only last 10 entries
              } else {
                updatedUsers[key] = [value]; // Create new user entry
              }
            }
          }
          return updatedUsers;
        });

        // 🔥 Store Average Query Count
        setAvgQueryCount((prev) => [
          ...prev.slice(-25),
          { timestamp, avg_query_count, avg_spilled },
        ]);

        setRealDataCounter((prev) => prev + 1); // Increment counter for real data
        setRealDataCounterSpilled((prev) => prev + 1);

        // 🔥 Handle Predicted Query Count Data
        if (predicted_query_count?.length > 0) {
          setRealDataCounter(0); // Reset counter when new predictions arrive

          const newPredictions = predicted_query_count.map(
            (value: number, index: number) => ({
              timestamp: timestamp + index * 10_000, // Offset by 10 sec each
              predicted_value: value,
            })
          );

          setPredictedData(newPredictions.slice(0, 10)); // Show first 10 predictions
          setFuturePredictions(newPredictions.slice(10)); // Store remaining 90 for later
        } else {
          // Append Future Predictions Every 10 Real Data Points
          if (realDataCounter >= 10 && futurePredictions?.length > 0) {
            setPredictedData(futurePredictions.slice(0, 10)); // Show next 10
            setFuturePredictions(futurePredictions.slice(10)); // Remove used ones
            setRealDataCounter(0);
          }
        }

        // 🔥 Handle Predicted Spilled Data
        if (predicted_spill?.length > 0) {
          setRealDataCounterSpilled(0);

          const newPredictions = predicted_spill.map(
            (value: number, index: number) => ({
              timestamp: timestamp + index * 10_000,
              predicted_value: value,
            })
          );

          setPredictedDataSpilled(newPredictions.slice(0, 10)); // Show first 10 predictions
          setFuturePredictionsSpilled(newPredictions.slice(10)); // Store remaining 90 for later
        } else {
          if (
            realDataCounterSpilled >= 10 &&
            futurePredictionsSpilled?.length > 0
          ) {
            setPredictedDataSpilled(futurePredictionsSpilled.slice(0, 10)); // Show next 10
            setFuturePredictionsSpilled(futurePredictionsSpilled.slice(10)); // Remove used ones
            setRealDataCounterSpilled(0);
          }
        }

        // 🔥 Store Latest Incoming Data (keep last 10)
        setIncomingData((prev) => [...prev.slice(-10), extractedInData]);
      } catch (error) {
        console.error("Error parsing Kafka data:", error);
      }
    };

    ws.onclose = () => {
      console.log("❌ WebSocket closed. Reconnecting in 3s...");
      // setTimeout(() => useKafkaWebSocket(), 3000); // Auto-reconnect (if needed)
    };

    return () => ws.close(); // Cleanup WebSocket on unmount
  }, []);

  /**
   * Return the updated state to be used in the Dashboard.
   */
  return {
    incomingData,
    userList,
    predictedData,
    avgQueryCount,
    predictedDataSpilled,
    alertsHistory,
  };
};

export default useKafkaWebSocket;
