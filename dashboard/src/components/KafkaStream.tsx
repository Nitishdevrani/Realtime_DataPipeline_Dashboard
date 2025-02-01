"use client"; // ✅ This must be a Client Component

import React from "react";
import useKafkaWebSocket from "@/lib/useKafkaWebSocket";

const KafkaStream: React.FC = () => {
  const messages = useKafkaWebSocket();
  console.log('messages',messages);
  
  return (
    <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg text-white">
      <h2 className="text-lg font-semibold text-center">🔥 Real-Time Kafka Stream</h2>
      <div className="h-64 overflow-y-auto mt-4 border border-gray-700 p-3">
        {/* {messages.length === 0 ? (
          <p className="text-center text-gray-400">Waiting for messages...</p>
        ) : (
          messages.map((msg, index) => (
            <p key={index} className="text-sm border-b border-gray-700 py-1">{msg}</p>
          ))
        )} */}
      </div>
    </div>
  );
};

export default KafkaStream;
// ===============================================
// "use client";

// import React, { useEffect, useState } from "react";

// const KafkaStream: React.FC = () => {
//   const [logs, setLogs] = useState<string[]>([]);

//   useEffect(() => {
//     const fetchLogs = async () => {
//       try {
//         const response = await fetch("/api/kafka");
//         const data = await response.json();
//         setLogs(data.logs);
//       } catch (error) {
//         console.error("❌ Failed to fetch logs:", error);
//       }
//     };

//     // ✅ Auto-refresh logs every 2 seconds
//     const interval = setInterval(fetchLogs, 2000);

//     return () => clearInterval(interval);
//   }, []);

//   return (
//     <div className="w-full bg-gray-800 p-4 rounded-lg shadow-lg text-white">
//       <h2 className="text-lg font-semibold text-center">🔥 Live Kafka Logs</h2>
//       <div className="h-64 overflow-y-auto mt-4 border border-gray-700 p-3">
//         {logs.length === 0 ? (
//           <p className="text-center text-gray-400">Waiting for logs...</p>
//         ) : (
//           logs.map((log, index) => (
//             <p key={index} className="text-sm border-b border-gray-700 py-1">{log}</p>
//           ))
//         )}
//       </div>
//     </div>
//   );
// };

// export default KafkaStream;
