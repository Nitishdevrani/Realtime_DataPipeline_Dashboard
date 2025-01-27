"use client";

import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { QueryData } from "@/utils/dataProcessor";

type Props = {
  points: QueryData[];
  correlationKeys: string[];
  dataKey: keyof QueryData;
};

const CustomStackedAreaChart: React.FC<Props> = ({ points, correlationKeys, dataKey }) => {
  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg">
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={points} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={dataKey} stroke="white" />
          <YAxis stroke="white" />
          <Tooltip />
          {correlationKeys.map((key, index) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stackId="1"
              stroke={["#8884d8", "#82ca9d", "#ffc658"][index % 3]}
              fill={["#8884d8", "#82ca9d", "#ffc658"][index % 3]}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CustomStackedAreaChart;
