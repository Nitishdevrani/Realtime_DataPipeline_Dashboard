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

export interface UserMetrics {
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
  timestamp: number;
  serverless: boolean;
}

export interface Users {
  [userId: string]: UserMetrics;
}

export interface KafkaData {
  alerts: string[];
  avg_query_count: number;
  avg_execution_time: number;
  avg_scanned: number;
  avg_spilled: number;
  avg_abort_rate: number;
  timestamp: number;
  total_queries: number;
  total_exec_time: number;
  predicted_query_count: number[]; // Can be updated if structure is known
  predicted_spill: number[];
  users: Users;
}

export type KafkaDataStream = KafkaData[];