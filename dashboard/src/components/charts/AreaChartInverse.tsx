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

type ChartDataPoint = {
    name: string;
    uv: number;
    pv: number;
    amt: number;
  };

type AreaChartProps = {
  data: ChartDataPoint[];
  width?: number | string;
  height?: number | string;
};

const sampleData: ChartDataPoint[] = [
    { name: "Page A", uv: 4000, pv: 2400, amt: 2400 },
    { name: "Page B", uv: 3000, pv: 1398, amt: 2210 },
    { name: "Page C", uv: -1000, pv: 9800, amt: 2290 },
    { name: "Page D", uv: 500, pv: 3908, amt: 2000 },
    { name: "Page E", uv: -2000, pv: 4800, amt: 2181 },
    { name: "Page F", uv: -250, pv: 3800, amt: 2500 },
    { name: "Page G", uv: 3490, pv: 4300, amt: 2100 },
  ];

const getGradientOffset = (data: ChartDataPoint[]) => {
  const dataMax = Math.max(...data.map((i) => i.uv));
  const dataMin = Math.min(...data.map((i) => i.uv));

  if (dataMax <= 0) return 0;
  if (dataMin >= 0) return 1;
  return dataMax / (dataMax - dataMin);
};

const AreaChartInverse: React.FC<AreaChartProps> = ({ data = sampleData, width = "100%", height = 400 }) => {
  const offset = getGradientOffset(data);

  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg">
      <h2 className="text-lg font-semibold text-center text-white mb-2">Area Chart Example</h2>
      <ResponsiveContainer width={width} height={height}>
        <AreaChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="gray" />
          <XAxis dataKey="name" stroke="white" />
          <YAxis stroke="white" />
          <Tooltip />
          <defs>
            <linearGradient id="splitColor" x1="0" y1="0" x2="0" y2="1">
              <stop offset={offset} stopColor="green" stopOpacity={1} />
              <stop offset={offset} stopColor="red" stopOpacity={1} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="uv"
            stroke="#000"
            fill="url(#splitColor)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AreaChartInverse;
