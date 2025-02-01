"use client";
import ChartGenerator from "@/components/ChartGenerator";
import RealTimePredictionChart from "./charts/RealTimePredictionChart";
import useKafkaWebSocket from "@/lib/useKafkaWebSocket";
import { KafkaDataStream } from "@/utils/KafkaData";
import OverallDataBox from "./containers/OverallDataBox";

export default function Dashboard() {
  const { overallData } = useKafkaWebSocket();
  // console.log('incomingData',overallData[overallData.length-1]['avg_query_count']);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold text-center mb-6">
        🚀 Stream Dreamer's Dashboard
      </h1>
      <OverallDataBox overallData={overallData} />
      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* <ChartGenerator data={overallData} chartType="line" dataKey={"avg_query_count"} title="Avg Query Count" /> */}
        {/* <ChartGenerator chartType="area" multiKeys={["num_permanent_tables_accessed","num_external_tables_accessed","num_system_tables_accessed"]} title="DB Table accessed" dataKey={"database_id"}/>
        <ChartGenerator chartType="pie" title="Types of Query" dataKey={"query_type"}/>
        <RealTimePredictionChart dataKey="num_scans" title="Number of scans with Predictions" /> */}
        {/* <ChartGenerator chartType="bar" dataKey={"queue_duration_ms"} title="Queue Duration (ms)" />
        <ChartGenerator chartType="bar" dataKey={"num_aggregations"} title="Num of aggregations" />
        <ChartGenerator chartType="scatter" title="Spilled Queries" dataKey={"cluster_size"} xKey="mbytes_scanned" yKey="mbytes_spilled"/> */}
      </div>
    </div>
  );
}
