export type DataPoint = {
    timestamp: number;
    execution_duration_ms: number;
  };
  
  export const generateFakeData = (): DataPoint => {
    const now = new Date();
    return {
      timestamp: now.getSeconds(),
      execution_duration_ms: Math.floor(Math.random() * 500) + 50, // Random (50-500ms)
    };
  };
  