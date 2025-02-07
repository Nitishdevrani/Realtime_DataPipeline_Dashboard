"use client";

import React from "react";
import { KafkaDataStream, QueryTypeCounts, Users } from "@/utils/KafkaData";
import CustomLineChart from "./charts/CustomLineChart";
import CustomStackedBarChart from "./charts/CustomStackedBarGraph";
import CustomStackedAreaChart from "./charts/CustomStackedAreaChart";

type ChartGeneratorProps = {
  data: KafkaDataStream | Users | QueryTypeCounts;
  chartType: "line" | "bar" | "stackedBar" | "area" | "pie" | "scatter";
  dataKey?: string; // Optional for multi-line support
  multiKeys?: string[]; // Support for multiple lines
  title: string;
};

const ChartGenerator: React.FC<ChartGeneratorProps> = ({
  data,
  chartType,
  dataKey,
  title,
  multiKeys = [],
}) => {
  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg mb-4">
      <h2 className="text-lg font-semibold text-center text-white mb-2">
        {title}
      </h2>

      {/* Multi-line support in Line Chart */}
      {chartType === "line" && (
        <CustomLineChart
          points={data}
          dataKeys={multiKeys.length > 0 ? multiKeys : dataKey ? [dataKey] : []}
        />
      )}

      {chartType === "area" && (
        <CustomStackedAreaChart
          points={data}
          correlationKeys={multiKeys}
          dataKey={dataKey || ""}
        />
      )}

      {chartType === "stackedBar" && (
        <CustomStackedBarChart
          points={data}
          correlationKeys={multiKeys}
          dataKey={dataKey || ""}
        />
      )}
    </div>
  );
};

export default ChartGenerator;
