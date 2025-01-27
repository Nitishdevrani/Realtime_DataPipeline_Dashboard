"use client";

import React from "react";
import { PieChart, Pie, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { QueryData } from "@/utils/dataProcessor";

type Props = {
  points: QueryData[];
  dataKey: keyof QueryData;
};

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#00C49F"];

const CustomPieChart: React.FC<Props> = ({ points, dataKey }) => {
  const aggregatedData = points.reduce((acc, entry) => {
    const key = entry[dataKey] as string;
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieData = Object.keys(aggregatedData).map((key, index) => ({
    name: key,
    value: aggregatedData[key],
    fill: COLORS[index % COLORS.length],
  }));

  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} fill="#8884d8">
            {pieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CustomPieChart;
