"use client";

import { BarChart as ReBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { formatTimestamp, QueryData } from "@/utils/dataProcessor";
import CustomTooltip from "../CustomTooltip";

type CLC = {
  points : QueryData[];
  dataKey : keyof QueryData;
}

const CustomBarChart : React.FC<CLC> = ({points, dataKey}) => {

  return (
      <ResponsiveContainer width="100%" height={300}>
        <ReBarChart data={points}>
          <CartesianGrid strokeDasharray="3 3" stroke="gray" />
          <XAxis dataKey="arrival_timestamp" stroke="white" tickFormatter={formatTimestamp} />
          <YAxis stroke="white" />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey={dataKey} fill="#22c55e" />
        </ReBarChart>
      </ResponsiveContainer>
  );
};

export default CustomBarChart;
