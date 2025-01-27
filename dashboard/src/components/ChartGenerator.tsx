"use client";

import React, { useEffect, useState } from "react";
import { QueryData } from "@/utils/dataProcessor";
import { getNextDataPoint } from "@/utils/sampleData";
import CustomLineChart from "./charts/CustomLineChart";
import CustomBarChart from "./charts/CustomBarChart";
import CustomStackedAreaChart from "./charts/CustomStackedAreaChart";
import CustomPieChart from "./charts/CustomPieChart";
import CustomScatterChart from "./charts/CustomScatterChart";

type ChartGeneratorProps = {
  chartType: "line" | "bar" | "area" | "pie" | "scatter";
  dataKey: keyof QueryData;
  multiKeys?: string[];
  title: string;
  xKey?: keyof QueryData; // Required for scatter plot
  yKey?: keyof QueryData; // Required for scatter plot
};

const ChartGenerator: React.FC<ChartGeneratorProps> = ({ chartType, dataKey, title, multiKeys = [], xKey, yKey }) => {
  const [data, setData] = useState<QueryData[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const {real} = getNextDataPoint();
      if (real) {
        setData((prevData) => [...prevData.slice(-50), real]);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg">
      <h2 className="text-lg font-semibold text-center text-white mb-2">{title}</h2>
      {chartType === "line" && <CustomLineChart points={data} dataKey={dataKey} />}
      {chartType === "bar" && <CustomBarChart points={data} dataKey={dataKey} />}
      {chartType === "area" && <CustomStackedAreaChart points={data} correlationKeys={multiKeys} dataKey={dataKey} />}
      {chartType === "pie" && <CustomPieChart points={data} dataKey={dataKey} />}
      {chartType === "scatter" && xKey && yKey && <CustomScatterChart points={data} xKey={xKey} yKey={yKey} />}
    </div>
  );
};

export default ChartGenerator;
