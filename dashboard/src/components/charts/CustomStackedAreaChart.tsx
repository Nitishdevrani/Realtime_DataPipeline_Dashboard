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
import { Users } from "@/utils/KafkaData";
import { formatXAxisTimestamp } from "@/utils/TimeFormater";

type Props = {
  points: Users;
  correlationKeys: string[];
  dataKey: keyof Users;
};

const CustomStackedAreaChart: React.FC<Props> = ({
  points,
  correlationKeys,
  dataKey,
}) => {
  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg">
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart
          data={points}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey={dataKey}
            stroke="white"
            tickFormatter={(tick) => formatXAxisTimestamp([tick])[0]}
          />
          <YAxis stroke="white" />
          <Tooltip />
          {correlationKeys.map((key, index) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stackId="1"
              stroke={
                ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#d45087"][
                  index % 5
                ]
              }
              fill={
                ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#d45087"][
                  index % 5
                ]
              }
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CustomStackedAreaChart;
