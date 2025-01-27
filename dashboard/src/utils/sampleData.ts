import { QueryData, parseQueryData, sortByTimestamp } from "./dataProcessor";
import data from "./completeData.json";

const FULL_DATA: QueryData[] = parseQueryData(sortByTimestamp(data));

// ✅ Simulated Real-Time Streaming
let currentIndex = 0;

// ✅ Generate a single step-forward prediction at each update
export const getNextDataPoint = (): { real: QueryData | null; prediction: QueryData | null } => {
  if (currentIndex < FULL_DATA.length) {
    const realData = FULL_DATA[currentIndex];

    // ✅ Generate the next prediction using a simple logic
    const predictedData: QueryData = {
      ...realData,
      arrival_timestamp: new Date(new Date(realData.arrival_timestamp).getTime() + 60000).toISOString(), // Predict next minute
      query_id: `PRED-${currentIndex + 1}`,
      predicted_num_scans: realData.num_scans + Math.random() * 100 - 25, // Small fluctuation
    };

    currentIndex++;
    return { real: realData, prediction: predictedData };
  }

  return { real: null, prediction: null };
};
