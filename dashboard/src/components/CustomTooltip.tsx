"use client";

import { KafkaData } from "@/utils/KafkaData";
import React from "react";
import { TooltipProps } from "recharts";

type CustomTooltipProps = TooltipProps<number, string> & {
  active?: boolean;
  payload?: { value: number; name: string; payload: KafkaData }[];
  label?: string;
};

// ✅ Function to format timestamp (e.g., "2023-01-27 10:47:01" → "27 Jan")
const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toDateString(); // If required full time like YYYY.MM.DD HH:MM:SS
  // return date.toLocaleDateString("en-GB", { day: "2-digit", month: "short" });
};

const CustomTooltip: React.FC<CustomTooltipProps> = ({
  active,
  payload,
  label,
}) => {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="bg-gray-900 text-white p-3 rounded-lg shadow-md">
      <p className="font-semibold text-sm">
        Timestamp: {formatTimestamp(label)}
      </p>
      {payload.map((entry, index) => (
        <p key={index} className="text-xs">
          <span className="font-semibold">{entry.name}: </span>
          {entry.value}
        </p>
      ))}
    </div>
  );
};

export default CustomTooltip;
