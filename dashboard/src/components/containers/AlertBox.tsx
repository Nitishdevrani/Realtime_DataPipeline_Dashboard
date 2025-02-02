"use client";

import React, { useState, useEffect } from "react";

type Alert = {
  timestamp: number;
  alert: string;
};

type AlertPopupProps = {
  alerts: Alert[];
};

const AlertPopup: React.FC<AlertPopupProps> = ({ alerts }) => {
  const [recentAlert, setRecentAlert] = useState<Alert | null>(null);
  const [alertHistory, setAlertHistory] = useState<Alert[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    if (alerts.length > 0) {
      const latestAlert = alerts[alerts.length - 1];

      setRecentAlert(latestAlert);
      setAlertHistory((prev) => {
        const mergedAlerts = [...prev, latestAlert].reduce<Alert[]>((acc, curr) => {
          if (!acc.some((alert) => alert.timestamp === curr.timestamp)) {
            acc.push(curr);
          }
          return acc;
        }, []);

        return mergedAlerts.sort((a, b) => b.timestamp - a.timestamp);
      });

      const timer = setTimeout(() => {
        setRecentAlert(null);
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [alerts]);

  const closeAlert = () => {
    setRecentAlert(null);
  };

  return (
    <div className="fixed top-5 right-5 z-[9999] pointer-events-none">
      {/* 🔥 Recent Alert Popup */}
      {recentAlert && (
        <div className="bg-red-500 text-white px-5 py-3 rounded-lg shadow-lg flex items-center space-x-3 animate-slideIn pointer-events-auto">
          <div className="flex flex-col">
            <span className="text-lg font-semibold">{recentAlert.alert}</span>
            <span className="text-sm text-gray-200">
              {new Date(recentAlert.timestamp).toLocaleString()}
            </span>
          </div>
          <button onClick={closeAlert} className="text-white font-bold px-2">
            ✖
          </button>
        </div>
      )}

      {/* 🔥 Alert History Dropdown */}
      {!recentAlert && alertHistory.length > 1 && (
        <div className="relative mt-3 pointer-events-auto">
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg flex items-center"
          >
            ⚠️ View Alert History
          </button>
          {isDropdownOpen && (
            <div className="absolute top-12 right-0 bg-gray-900 text-white rounded-lg shadow-lg max-h-60 overflow-auto w-80 p-3 z-[9999]">
              {alertHistory.map((alert) => (
                <div key={alert.timestamp} className="border-b border-gray-700 py-2">
                  <p className="text-sm">{alert.alert}</p>
                  <p className="text-xs text-gray-400">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AlertPopup;
