"use client";
import ChartGenerator from "@/components/ChartGenerator";
import useKafkaWebSocket from "@/lib/useKafkaWebSocket";
import OverallDataBox from "./containers/OverallDataBox";
import UserDropdown from "./containers/UserDropdown";
import AlertPopup from "./containers/AlertBox";
export default function Dashboard() {
  const {
    incomingData,
    userList,
    predictedData,
    avgQueryCount,
    predictedDataSpilled,
    alertsHistory,
  } = useKafkaWebSocket();
  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold text-center mb-6">
        🚀 Stream Dreamer's Dashboard
      </h1>
      <AlertPopup alerts={alertsHistory || []} />
      <OverallDataBox overallData={incomingData} />
      <div className="w-full max-w-7xl grid grid-cols-1 md:grid-cols-2 gap-6">
        <ChartGenerator
          chartType="line"
          data={[...avgQueryCount, ...predictedData].sort(
            (a, b) => a.timestamp - b.timestamp
          )} // 🔥 Sort by timestamp
          multiKeys={["avg_query_count", "predicted_value"]} // 🔥 Display 2 lines
          dataKey="timestamp"
          title="Avg Query Count & Predictions"
        />
        <ChartGenerator
          chartType="line"
          data={[...avgQueryCount, ...predictedDataSpilled].sort(
            (a, b) => a.timestamp - b.timestamp
          )} // 🔥 Sort by timestamp
          multiKeys={["avg_spilled", "predicted_value"]} // 🔥 Display 2 lines
          dataKey="timestamp"
          title="Avg Spill & Predictions"
        />
      </div>
      <UserDropdown userList={userList} overallData={incomingData} />
    </div>
  );
}
