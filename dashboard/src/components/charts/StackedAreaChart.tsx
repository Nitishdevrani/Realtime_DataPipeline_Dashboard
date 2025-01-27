"use client";

import { QueryData } from "@/utils/dataProcessor";
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
import CustomTooltip from "../CustomTooltip";

type CLC = {
  points: QueryData[];
  coorelationKeys: string[];
  dataKey: keyof QueryData;
};

const StackedAreaChart: React.FC<CLC> = ({
  points,
  coorelationKeys,
  dataKey,
}) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart
        data={points}
        margin={{
          top: 10,
          right: 30,
          left: 0,
          bottom: 0,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={dataKey} />
        <YAxis />
        <Tooltip content={<CustomTooltip />} />
        {coorelationKeys.map((key, index) => (
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
  );
};
export default StackedAreaChart;
