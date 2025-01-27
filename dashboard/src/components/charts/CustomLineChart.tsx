"use client";

import React from "react";
import { LineChart as ReLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { formatTimestamp, QueryData } from "@/utils/dataProcessor";
import CustomTooltip from "../CustomTooltip";

type CLC = {
  points : QueryData[];
  dataKey : string;
}

const CustomLineChart : React.FC<CLC> = ({points,dataKey}) => {
  return (
      <ResponsiveContainer width="100%" height={300}>
        <ReLineChart data={points}>
          <CartesianGrid strokeDasharray="3 3" stroke="gray" />
          <XAxis dataKey="arrival_timestamp" tickFormatter={formatTimestamp} stroke="white" />
          <YAxis stroke="white" />
          <Tooltip content={<CustomTooltip/>} />
          <Line type="monotone" dataKey={dataKey} stroke="#38bdf8" strokeWidth={2} />
        </ReLineChart>
      </ResponsiveContainer>
  );
};

export default CustomLineChart;
