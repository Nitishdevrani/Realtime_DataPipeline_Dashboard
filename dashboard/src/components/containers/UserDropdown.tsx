"use client";
import { useState } from "react";
import { KafkaDataStream, KafkaData, Users } from "@/utils/KafkaData";
import ChartGenerator from "../ChartGenerator";

const QUERY_TYPE_NAMES = [
  "analyze",
  "copy",
  "ctas",
  "delete",
  "insert",
  "other",
  "select",
  "update",
  "vacuum",
  "unload",
];
const UserDropdown = ({
  userList,
  overallData,
}: {
  userList: Record<string, Users[]>;
  overallData: KafkaDataStream;
}) => {
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);

  // Extract user IDs
  const userIds = Object.keys(userList);

  // Get selected user's logs
  const selectedUserData = selectedUserId ? userList[selectedUserId] : null;

  // Extract query type counts and dynamically include cluster metrics
const query_type =
selectedUserId && selectedUserData
  ? selectedUserData.map((val) => ({
      ...val?.query_type_counts,
      ...Object.fromEntries(
        Object.entries(val.cluster_metrics || {}).map(([key, value]) => [
          `cluster_${key}`, // Dynamic key naming
          value.query_count, // Extract query_count for each cluster
        ])
      ),
      timestamp: val.timestamp,
    }))
  : [];
  console.log('query_type',query_type);
  
  const multiCluster = Array.from(
    new Set(
      query_type.flatMap((entry) =>
        Object.keys(entry).filter(
          (key) => key !== "timestamp" && !QUERY_TYPE_NAMES.includes(key)
        )
      )
    )
  );
      console.log('multiCluster',multiCluster);
    
      // cluster_metrics
    
  // ✅ Fix: Properly aligning user query count with avg query count
  // const queryCountComparison =
  //   selectedUserId && selectedUserData
  //     ? selectedUserData.map((userEntry) => {
  //         const matchingAvgData = overallData.find(
  //           (overallEntry) => overallEntry.timestamp === userEntry.timestamp
  //         ) as KafkaData | undefined;

  //         return {
  //           timestamp: userEntry.timestamp,
  //           user_query_count: userEntry.query_count, // User's query count
  //           avg_query_count: matchingAvgData ? matchingAvgData.avg_query_count : null, // Avg query count from overallData
  //         };
  //       })
  //     : [];

  return (
    <div className="w-full max-w-7xl mx-auto bg-gray-900 p-6 rounded-lg shadow-xl">
      <h2 className="text-2xl font-bold text-center text-white mb-4">
        📊 User Logs
      </h2>

      {/* Dropdown for selecting a user */}
      <select
        className="w-full p-3 bg-gray-800 text-white border border-gray-700 rounded-xl mb-4"
        onChange={(e) => setSelectedUserId(e.target.value)}
        defaultValue=""
      >
        <option value="" disabled>
          Select a User ID
        </option>
        {userIds.map((userId) => (
          <option key={userId} value={userId}>
            User {userId}
          </option>
        ))}
      </select>

      {/* Display selected user's logs */}
      {selectedUserData ? (
        <div className="w-full text-white p-5 rounded-lg shadow-lg">
          <h3 className="text-xl font-semibold text-blue-400 mb-3">
            User {selectedUserId}'s Data
          </h3>

          <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 gap-6">
            {/* Line Chart: User's Query Count vs. Avg Query Count */}
            <ChartGenerator
              chartType="line"
              data={selectedUserData}
              dataKey="timestamp"
              multiKeys={["query_count", "total_joins", "total_aggregations"]}
              title="User Query Count"
            />

            {/* Stacked Bar Chart: Types of Query */}
            <ChartGenerator
              chartType="stackedBar"
              data={query_type}
              dataKey="timestamp"
              multiKeys={QUERY_TYPE_NAMES}
              title="Types of Query"
            />

            {/* Cluster matrice */}
{/* Stacked Bar Chart: Types of Query */}
<ChartGenerator
              chartType="stackedBar"
              data={query_type}
              dataKey="timestamp"
              multiKeys={multiCluster}
              title="Cluster Used"
            />
            {/* <ChartGenerator
              data={selectedUserData}
              chartType="pie"
              title="Cluster Type"
              dataKey={"serverless"}
            /> */}
          </div>
        </div>
      ) : (
        <p className="text-gray-400 text-center">No user selected</p>
      )}
    </div>
  );
};

export default UserDropdown;
