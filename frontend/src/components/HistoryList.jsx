export default function HistoryList({ history, onSelect }) {
  if (!history.length) return null;

  const fmt = (iso) =>
    new Date(iso).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

  return (
    <div
      style={{
        borderRadius: 10,
        background: "var(--surface)",
        border: "1px solid var(--border)",
        padding: "14px",
      }}
    >
      <div
        style={{
          fontSize: 11,
          fontWeight: 600,
          color: "var(--muted)",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          marginBottom: 10,
        }}
      >
        Recent Scrapes
      </div>
      <ul
        style={{
          margin: 0,
          padding: 0,
          listStyle: "none",
          display: "flex",
          flexDirection: "column",
          gap: 2,
        }}
      >
        {history.map((item, i) => (
          <li key={i}>
            <button
              onClick={() => onSelect(item.url)}
              style={{
                width: "100%",
                textAlign: "left",
                background: "none",
                border: "none",
                borderRadius: 6,
                padding: "7px 8px",
                cursor: "pointer",
                transition: "background 0.1s",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.background = "var(--surface2)")
              }
              onMouseLeave={(e) => (e.currentTarget.style.background = "none")}
            >
              <div
                style={{
                  fontSize: 12,
                  color: "#60a5fa",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {item.title !== item.url
                  ? item.title
                  : new URL(item.url).hostname}
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: "var(--muted)",
                  fontFamily: "var(--mono)",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  marginTop: 2,
                }}
              >
                {item.url}
              </div>
              <div style={{ fontSize: 10, color: "#334155", marginTop: 2 }}>
                {fmt(item.timestamp)}
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
