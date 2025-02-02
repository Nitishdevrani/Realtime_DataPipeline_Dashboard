export type QueryData = {
  instance_id: string;
  cluster_size: string;
  user_id: string;
  database_id: string;
  query_id: string;
  arrival_timestamp: string;
  compile_duration_ms: number;
  queue_duration_ms: number;
  execution_duration_ms: number;
  feature_fingerprint: string;
  was_aborted: boolean;
  was_cached: boolean;
  cache_source_query_id: string;
  query_type: string;
  num_permanent_tables_accessed: number;
  num_external_tables_accessed: number;
  num_system_tables_accessed: number;
  read_table_ids: string;
  write_table_ids: string;
  mbytes_scanned: number;
  mbytes_spilled: number;
  num_joins: number;
  num_scans: number;
  predicted_num_scans : number;
  num_aggregations: number;
};

// ✅ Define a type for raw input data
type RawQueryData = {
  instance_id?: string;
  cluster_size?: string;
  user_id?: string;
  database_id?: string;
  query_id?: string;
  arrival_timestamp?: string;
  compile_duration_ms?: string;
  queue_duration_ms?: string;
  execution_duration_ms?: string;
  feature_fingerprint?: string;
  was_aborted?: string;
  was_cached?: string;
  cache_source_query_id?: string;
  query_type?: string;
  num_permanent_tables_accessed?: string;
  num_external_tables_accessed?: string;
  num_system_tables_accessed?: string;
  read_table_ids?: string;
  write_table_ids?: string;
  mbytes_scanned?: string;
  mbytes_spilled?: string;
  num_joins?: string;
  num_scans?: string;
  num_aggregations?: string;
};

// ✅ Utility function to safely parse numbers
const safeParseFloat = (value: string, defaultValue: number = 0): number => {
  const num = parseFloat(value);
  return isNaN(num) ? defaultValue : parseFloat(num.toFixed(2)); // Ensure 2 decimal places
};

// ✅ Function to process and clean data
export const parseQueryData = (rawData: RawQueryData[]): QueryData[] => {
  return rawData.map((item) => ({
    instance_id: item.instance_id || "unknown",
    cluster_size: item.cluster_size || "unknown",
    user_id: item.user_id || "unknown",
    database_id: item.database_id || "unknown",
    query_id: item.query_id || "unknown",
    arrival_timestamp: item.arrival_timestamp || new Date().toISOString(),
    compile_duration_ms: safeParseFloat(item.compile_duration_ms || "0"),
    queue_duration_ms: safeParseFloat(item.queue_duration_ms || "0"),
    execution_duration_ms: safeParseFloat(item.execution_duration_ms || "0"),
    feature_fingerprint: item.feature_fingerprint || "",
    was_aborted: item.was_aborted === "1",
    was_cached: item.was_cached === "1",
    cache_source_query_id: item.cache_source_query_id || "",
    query_type: item.query_type || "unknown",
    num_permanent_tables_accessed: safeParseFloat(item.num_permanent_tables_accessed || "0"),
    num_external_tables_accessed: safeParseFloat(item.num_external_tables_accessed || "0"),
    num_system_tables_accessed: safeParseFloat(item.num_system_tables_accessed || "0"),
    read_table_ids: item.read_table_ids || "",
    write_table_ids: item.write_table_ids || "",
    mbytes_scanned: safeParseFloat(item.mbytes_scanned || "0"),
    mbytes_spilled: safeParseFloat(item.mbytes_spilled || "0"),
    num_joins: safeParseFloat(item.num_joins || "0"),
    num_scans: safeParseFloat(item.num_scans || "0"),
    predicted_num_scans: safeParseFloat(item.num_scans || "0"),
    num_aggregations: safeParseFloat(item.num_aggregations || "0"),
  }));
};

// ✅ Function to format timestamp (e.g., "2023-01-27 10:47:01" → "27 Jan")
export const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toDateString();
  // return date.toLocaleDateString("en-GB", { day: "2-digit", month: "short" });
};

// ✅ Function to sort data by `arrival_timestamp`
export const sortByTimestamp = (data: QueryData[]): QueryData[] => {
  return [...data].sort(
    (a, b) => new Date(a.arrival_timestamp).getTime() - new Date(b.arrival_timestamp).getTime()
  );
};