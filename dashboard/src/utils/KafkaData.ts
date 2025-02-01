export interface QueryTypeCounts {
  analyze?: number;
  ctas?: number;
  update?: number;
  delete?: number;
  select?: number;
  insert?: number;
  copy?: number;
  other?: number;
  unload?: number;
  vacuum?: number;
}

export interface ClusterMetrics {
  [clusterId: string]: {
    query_count: number;
    total_duration: number;
  };
}

export interface UserQueryData {
  query_count: number;
  total_execution_time: number;
  scanned: number;
  spilled: number;
  avg_spill: number;
  avg_execution_time: number;
  queue_time_percentage: number;
  compile_overhead_ratio: number;
  query_type_counts: QueryTypeCounts;
  total_joins: number;
  total_aggregations: number;
  unique_tables: string[];
  cluster_metrics: ClusterMetrics;
  aborted_queries: number;
  abort_rate: number;
  read_write_ratio: number | null;
  predicted_avg_execution_time: number;
}

export interface UserData {
  [userId: string]: UserQueryData;
}

export interface Users {
  [instanceId: string]: UserData;
}

export interface OverallData {
//   [clusterId: string]: {
    avg_query_count: number;
    avg_execution_time: number;
    avg_scanned: number;
    avg_spilled: number;
    avg_abort_rate: number;
//   };
}

export interface KafkaData {
  users: Users;
  overall: OverallData;
}

/** ✅ This represents the full array of streaming Kafka data */
export type KafkaDataStream = KafkaData[];
