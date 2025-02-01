"use client";

import React, { useEffect, useState } from "react";
import { QueryData } from "@/utils/dataProcessor";
import { getNextDataPoint } from "@/utils/sampleData";
import CustomLineChart from "./charts/CustomLineChart";
import CustomBarChart from "./charts/CustomBarChart";
import CustomStackedAreaChart from "./charts/CustomStackedAreaChart";
import CustomPieChart from "./charts/CustomPieChart";
import CustomScatterChart from "./charts/CustomScatterChart";
import { KafkaData, OverallData, Users } from "@/utils/KafkaData";

type ChartGeneratorProps = {
  data : OverallData[] | Users[];
  chartType: "line" | "bar" | "area" | "pie" | "scatter";
  dataKey: keyof  OverallData;
  multiKeys?: string[];
  title: string;
  xKey?: keyof QueryData; // Required for scatter plot
  yKey?: keyof QueryData; // Required for scatter plot
};

const ChartGenerator: React.FC<ChartGeneratorProps> = ({ data, chartType, dataKey, title, multiKeys = [], xKey, yKey }) => {

  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg">
      <h2 className="text-lg font-semibold text-center text-white mb-2">{title}</h2>
      {chartType === "line" && <CustomLineChart points={data} dataKey={dataKey} />}
      {/* {chartType === "bar" && <CustomBarChart points={data} dataKey={dataKey} />}
      {chartType === "area" && <CustomStackedAreaChart points={data} correlationKeys={multiKeys} dataKey={dataKey} />}
      {chartType === "pie" && <CustomPieChart points={data} dataKey={dataKey} />}
      {chartType === "scatter" && xKey && yKey && <CustomScatterChart points={data} xKey={xKey} yKey={yKey} />} */}
    </div>
  );
};

export default ChartGenerator;
