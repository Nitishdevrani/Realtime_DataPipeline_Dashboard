"use client";

import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { QueryData } from "@/utils/dataProcessor";
import { getNextDataPoint } from "@/utils/sampleData";
import { formatTimestamp } from "@/utils/dataProcessor";
import CustomTooltip from "../CustomTooltip";

type Props = {
  dataKey: keyof QueryData;
  title: string;
};

const RealTimePredictionChart: React.FC<Props> = ({ dataKey, title }) => {
  const [data, setData] = useState<QueryData[]>([]);
  const [predictions, setPredictions] = useState<QueryData[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const { real, prediction } = getNextDataPoint();

      if (real) {
        setData((prevData) => [...prevData.slice(-50), real]);
      }

      if (prediction) {
        setPredictions((prevPredictions) => [...prevPredictions.slice(-50), prediction]); // ✅ Maintain all predictions
      }
    }, 8000); // ✅ Update every 2 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg">
      <h2 className="text-lg font-semibold text-center text-white mb-2">{title}</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={[...data, ...predictions]}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="arrival_timestamp" stroke="white" tickFormatter={formatTimestamp} />
          <YAxis stroke="white" />
          <Tooltip content={<CustomTooltip/>}/>
          <Legend />
          {/* ✅ Real-time data (solid line) */}
          <Line type="monotone" dataKey={dataKey} stroke="#38bdf8" strokeWidth={2} dot={{ r: 3 }} />
          {/* ✅ Predicted data (continuous dashed line) */}
          <Line
            type="monotone"
            dataKey={"predicted_num_scans"}
            stroke="#FF5733"
            strokeWidth={2}
            strokeDasharray="5 5"
            data={predictions} // ✅ Now includes full history of predictions
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RealTimePredictionChart;
