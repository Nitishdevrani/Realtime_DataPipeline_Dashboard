"use client";

import React from "react";
import {
  PieChart,
  Pie,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from "recharts";
import { Users } from "@/utils/KafkaData";

// ✅ Define color palette
const COLORS = [
  "#8884d8",
  "#82ca9d",
  "#ffc658",
  "#ff7300",
  "#00C49F",
  "#D72638",
  "#FFBB28",
];

// ✅ Define a Type for Pie Chart Labels
type PieLabelProps = {
  cx: number;
  cy: number;
  midAngle: number;
  innerRadius: number;
  outerRadius: number;
  percent: number;
  index: number;
  name: string;
};

// ✅ Custom function to generate Pie labels with TypeScript
const renderCustomizedLabel = ({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
  name,
}: PieLabelProps) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5; // Adjust position
  const x = cx + radius * Math.cos(-midAngle * (Math.PI / 180));
  const y = cy + radius * Math.sin(-midAngle * (Math.PI / 180));

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize="12px"
      fontWeight="bold"
    >
      {name} ({(percent * 100).toFixed(0)}%)
    </text>
  );
};

type Props = {
  points: Users;
  dataKey: keyof Users;
};

const CustomPieChart: React.FC<Props> = ({ points, dataKey }) => {
  const aggregatedData = points.reduce((acc, entry) => {
    const key = entry[dataKey] as string;
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieData = Object.keys(aggregatedData).map((key, index) => ({
    name: key, // ✅ This name will be used for labels
    value: aggregatedData[key],
    fill: COLORS[index % COLORS.length],
  }));

  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={pieData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={100}
            fill="#8884d8"
            label={renderCustomizedLabel} // ✅ Add labels inside pie slices
            labelLine={false} // ✅ Hide connecting label lines
          >
            {pieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CustomPieChart;
