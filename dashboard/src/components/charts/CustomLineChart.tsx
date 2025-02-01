"use client";

import React from "react";
import { LineChart as ReLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { formatTimestamp, QueryData } from "@/utils/dataProcessor";
import CustomTooltip from "../CustomTooltip";
import { OverallData, Users } from "@/utils/KafkaData";

type CLC = {
  points : OverallData[] | Users[];
  dataKey : keyof OverallData;
}

const CustomLineChart : React.FC<CLC> = ({points,dataKey}) => {
  console.log('points',points);
  
  return (
      <ResponsiveContainer width="100%" height={300}>
        <ReLineChart data={points}>
          <CartesianGrid strokeDasharray="3 3" stroke="gray" />
          <XAxis dataKey="avg_execution_time" stroke="white" />
          <YAxis stroke="white" />
          <Tooltip content={<CustomTooltip/>} />
          <Line type="monotone" dataKey={dataKey} stroke="#38bdf8" strokeWidth={2} />
        </ReLineChart>
      </ResponsiveContainer>
  );
};

export default CustomLineChart;
