import { useState, useEffect } from "react";
import { checkHealth } from "../api/client";

export default function StatusBar() {
  const [online, setOnline] = useState(null);

  useEffect(() => {
    const ping = async () => {
      try {
        await checkHealth();
        setOnline(true);
      } catch {
        setOnline(false);
      }
    };
    ping();
    const id = setInterval(ping, 5000);
    return () => clearInterval(id);
  }, []);

  const color = online === null ? "#eab308" : online ? "#22c55e" : "#ef4444";
  const label =
    online === null
      ? "connecting"
      : online
        ? "backend online"
        : "backend offline";

  return (
    <div
      style={{
        background: "var(--surface)",
        borderBottom: "1px solid var(--border)",
        padding: "5px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-end",
        gap: 7,
      }}
    >
      <span
        style={{
          width: 7,
          height: 7,
          borderRadius: "50%",
          background: color,
          boxShadow: `0 0 6px ${color}`,
          display: "inline-block",
        }}
      />
      <span
        style={{
          fontSize: 11,
          color: "var(--muted)",
          fontFamily: "var(--mono)",
        }}
      >
        {label}
      </span>
    </div>
  );
}
