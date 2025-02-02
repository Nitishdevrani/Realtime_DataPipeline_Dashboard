"use client";

import { KafkaDataStream } from "@/utils/KafkaData";
import { FaChartLine, FaClock, FaDatabase, FaExclamationTriangle, FaTasks, FaCalculator } from "react-icons/fa";

type OverallDataBoxProps = {
  overallData: KafkaDataStream;
};

// Mapping keys to icons
const ICONS: Record<string, JSX.Element> = {
  avg_query_count: <FaChartLine className="text-blue-400 text-3xl mb-2" />,
  avg_execution_time: <FaClock className="text-green-400 text-3xl mb-2" />,
  avg_scanned: <FaDatabase className="text-purple-400 text-3xl mb-2" />,
  avg_spilled: <FaExclamationTriangle className="text-red-400 text-3xl mb-2" />,
  avg_abort_rate: <FaTasks className="text-yellow-400 text-3xl mb-2" />,
  total_queries: <FaCalculator className="text-orange-400 text-3xl mb-2" />,
  total_exec_time: <FaClock className="text-teal-400 text-3xl mb-2" />,
};

const OverallDataBox: React.FC<OverallDataBoxProps> = ({ overallData }) => {
  const latestData =
    overallData.length > 0 ? overallData[overallData.length - 1] : null;

  return (
    <div className="w-full max-w-max mx-auto bg-gray-900 p-6 rounded-lg shadow-xl mb-4">
      <h2 className="text-2xl font-bold text-center text-white mb-4">
        Recent Overall Metrics
      </h2>

      {latestData ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
          {Object.entries(latestData).map(([key, value]) => {
            if (
              key === "alerts" ||
              key === "users" ||
              key === "predicted_query_count" ||
              key === "timestamp" ||
              key === "predicted_spill"
            )
              return null;

            return (
              <div
                key={key}
                className="bg-gray-800 text-white text-center border-2 border-gray-700 rounded-lg p-5 shadow-lg flex flex-col items-center justify-center min-h-[140px]"
              >
                {ICONS[key] || <FaChartLine className="text-gray-400 text-3xl mb-2" />}
                <p className="text-lg font-semibold text-gray-400 capitalize">
                  {key.replace(/_/g, " ")}
                </p>
                <p className="text-2xl font-bold text-blue-400">
                  {typeof value === "number" ? value.toFixed(2) : value}
                </p>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-gray-400 text-center">No data available</p>
      )}
    </div>
  );
};

export default OverallDataBox;
