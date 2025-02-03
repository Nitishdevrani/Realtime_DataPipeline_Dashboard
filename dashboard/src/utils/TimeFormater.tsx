export const formatXAxisTimestamp = (timestamps: number[]): string[] => {
  if (timestamps.length === 0) return [];

  // Convert timestamps to Date objects
  const dates = timestamps.map((ts) => new Date(ts));

  // Find the time range
  const minTime = Math.min(...timestamps);
  const maxTime = Math.max(...timestamps);
  const timeDiffHours = (maxTime - minTime) / (1000 * 60 * 60); // Convert ms to hours

  // If data is within a single day, use hours
  if (timeDiffHours < 24) {
    return dates.map((date) =>
      date.toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    );
  } else {
    // Data spans multiple days, use dates
    const formattedDates: string[] = [];
    let lastFormattedDate = "";

    dates.forEach((date) => {
      const formattedDate = date.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
      });

      // Only push unique days to avoid repeating the same date on the x-axis
      if (formattedDate !== lastFormattedDate) {
        formattedDates.push(formattedDate);
        lastFormattedDate = formattedDate;
      } else {
        formattedDates.push(""); // Empty string for non-unique dates to avoid repetition
      }
    });

    return formattedDates;
  }
};
