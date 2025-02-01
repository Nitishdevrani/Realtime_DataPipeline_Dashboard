"use client";

import { OverallData } from "@/utils/KafkaData";

type OverallDataBoxProps = {
  overallData: OverallData[];
};

const OverallDataBox: React.FC<OverallDataBoxProps> = ({ overallData }) => {
  // ✅ Get the latest overallData entry (last received)
  const latestData = overallData.length > 0 ? overallData[overallData.length - 1] : null;

  return (
    <div className="w-full max-w-7xl mx-auto bg-gray-900 p-6 rounded-lg shadow-xl">
      <h2 className="text-2xl font-bold text-center text-white mb-4">📊 Overall Metrics</h2>

      {latestData ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {Object.entries(latestData).map(([key, value]) => (
            <div key={key} className="bg-gray-800 text-white text-center border-2 border-gray-700 rounded-lg p-5 shadow-lg">
              <p className="text-lg font-semibold text-gray-400 capitalize">{key.replace(/_/g, " ")}</p>
              <p className="text-2xl font-bold text-blue-400">
                {typeof value === "number" ? value.toFixed(2) : value}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-400 text-center">No data available</p>
      )}
    </div>
  );
};

export default OverallDataBox;
