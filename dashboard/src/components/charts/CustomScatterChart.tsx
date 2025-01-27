"use client";

import React from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { QueryData } from "@/utils/dataProcessor";
import CustomTooltip from "../CustomTooltip";

type Props = {
  points: QueryData[];
  xKey: keyof QueryData;
  yKey: keyof QueryData;
};

const CustomScatterChart: React.FC<Props> = ({ points, xKey, yKey }) => {
  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg">
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" dataKey={xKey} name={xKey} stroke="white" />
          <YAxis type="number" dataKey={yKey} name={yKey} stroke="white" />
          <Tooltip content={<CustomTooltip />} />
          <Scatter name="Query Data" data={points} fill="#8884d8" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CustomScatterChart;
