"use client";

import React from "react";
import { TooltipProps } from "recharts";
import { QueryData } from "@/utils/dataProcessor";

type CustomTooltipProps = TooltipProps<number, string> & {
  active?: boolean;
  payload?: { value: number; name: string; payload: QueryData }[];
  label?: string;
};

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="bg-gray-900 text-white p-3 rounded-lg shadow-md">
      <p className="font-semibold text-sm">Timestamp: {label}</p>
      {payload.map((entry, index) => (
        <p key={index} className="text-xs">
          <span className="font-semibold">{entry.name}: </span>
          {entry.value}
        </p>
      ))}
      <p className="text-xs text-green-400">Query ID: {payload[0].payload.query_id}</p>
    </div>
  );
};

export default CustomTooltip;
