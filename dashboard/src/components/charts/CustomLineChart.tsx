"use client";

import React from "react";
import {
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { formatXAxisTimestamp } from "@/utils/TimeFormater";
import { KafkaDataStream, Users } from "@/utils/KafkaData";

type CLC = {
  points: KafkaDataStream | Users;
  dataKeys: string[]; // ✅ Support for multiple lines
};

const CustomLineChart: React.FC<CLC> = ({ points, dataKeys }) => {

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ReLineChart data={points}>
        <CartesianGrid strokeDasharray="3 3" stroke="gray" />
        <XAxis
          dataKey="timestamp"
          stroke="white"
          tickFormatter={(tick) => formatXAxisTimestamp([tick])[0]}
        />
        <YAxis stroke="white" />
        <Tooltip />

        {/* ✅ Render multiple lines dynamically */}
        {dataKeys.map((key, index) => (
          <Line
            connectNulls
            key={key}
            type="monotone"
            dataKey={key}
            stroke={
              [
                "#38bdf8",
                "#FF5733",
                "#82ca9d",
                "#ff7300",
                "#8884d8",
                "#ffc658",
              ][index % 5]
            } // Cycle colors
            strokeWidth={2}
            // Below line is for dashed line.
            // strokeDasharray="3 4 5 2"
          />
        ))}
      </ReLineChart>
    </ResponsiveContainer>
  );
};

export default CustomLineChart;
