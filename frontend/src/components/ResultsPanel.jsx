const card = {
  borderRadius: 10,
  background: "var(--surface)",
  border: "1px solid var(--border)",
  padding: "16px",
};

const label = {
  fontSize: 11,
  fontWeight: 600,
  color: "var(--muted)",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  marginBottom: 10,
};

export default function ResultsPanel({ status, result, error }) {
  if (status === "idle")
    return (
      <div style={{ ...card, padding: "60px 24px", textAlign: "center" }}>
        <div style={{ fontSize: 36, marginBottom: 12 }}>🕸️</div>
        <p style={{ color: "var(--muted)", fontSize: 13, margin: 0 }}>
          Enter a URL to start scraping.
        </p>
      </div>
    );

  if (status === "loading")
    return (
      <div
        style={{ ...card, display: "flex", flexDirection: "column", gap: 10 }}
      >
        {[120, 80, 100].map((w, i) => (
          <div
            key={i}
            style={{
              height: i === 0 ? 18 : 12,
              width: w,
              background: "var(--surface2)",
              borderRadius: 4,
              animation: "pulse 1.4s ease-in-out infinite",
            }}
          />
        ))}
        <p
          style={{
            fontSize: 12,
            color: "var(--muted)",
            marginTop: 4,
            textAlign: "center",
          }}
        >
          Fetching and parsing page…
        </p>
        <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }`}</style>
      </div>
    );

  if (status === "error")
    return (
      <div
        style={{
          ...card,
          background: "rgba(239,68,68,0.06)",
          borderColor: "rgba(239,68,68,0.3)",
        }}
      >
        <div
          style={{
            fontSize: 13,
            fontWeight: 600,
            color: "var(--red)",
            marginBottom: 6,
          }}
        >
          Scrape failed
        </div>
        <div
          style={{
            fontSize: 12,
            fontFamily: "var(--mono)",
            color: "rgba(239,68,68,0.8)",
          }}
        >
          {error}
        </div>
      </div>
    );

  if (!result) return null;

  const { title, url, text, links = [], method_used, html_length } = result;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {/* Summary card */}
      <div style={card}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 8,
          }}
        >
          <div style={{ minWidth: 0 }}>
            <div
              style={{
                fontSize: 15,
                fontWeight: 700,
                color: "var(--text)",
                marginBottom: 4,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {title || "Untitled page"}
            </div>
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                fontSize: 12,
                fontFamily: "var(--mono)",
                color: "#60a5fa",
                textDecoration: "none",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                display: "block",
              }}
            >
              {url}
            </a>
          </div>
          <span
            style={{
              fontSize: 10,
              fontWeight: 600,
              padding: "3px 8px",
              borderRadius: 99,
              background:
                method_used === "playwright"
                  ? "rgba(139,92,246,0.15)"
                  : "rgba(59,130,246,0.15)",
              color: method_used === "playwright" ? "#a78bfa" : "#60a5fa",
              border: `1px solid ${method_used === "playwright" ? "rgba(139,92,246,0.3)" : "rgba(59,130,246,0.3)"}`,
              whiteSpace: "nowrap",
              flexShrink: 0,
            }}
          >
            {method_used}
          </span>
        </div>

        <div
          style={{ display: "flex", gap: 20, marginTop: 12, flexWrap: "wrap" }}
        >
          <Stat value={links.length} label="links" color="var(--green)" />
          <Stat
            value={`${((text?.length ?? 0) / 1000).toFixed(1)}k`}
            label="chars"
            color="var(--green)"
          />
          <Stat
            value={`${(html_length / 1000).toFixed(1)}k`}
            label="html"
            color="var(--muted)"
          />
        </div>
      </div>

      {/* Extracted text */}
      {text && (
        <div style={card}>
          <div style={label}>Extracted Text</div>
          <p
            style={{
              fontSize: 13,
              color: "#94a3b8",
              lineHeight: 1.7,
              whiteSpace: "pre-wrap",
              maxHeight: 220,
              overflowY: "auto",
              margin: 0,
            }}
          >
            {text.slice(0, 2000)}
            {text.length > 2000 && (
              <span style={{ color: "var(--muted)" }}>
                {" "}
                … ({text.length - 2000} more chars)
              </span>
            )}
          </p>
        </div>
      )}

      {/* Links */}
      {links.length > 0 && (
        <div style={card}>
          <div style={label}>Links ({links.length})</div>
          <ul
            style={{
              margin: 0,
              padding: 0,
              listStyle: "none",
              display: "flex",
              flexDirection: "column",
              gap: 4,
              maxHeight: 220,
              overflowY: "auto",
            }}
          >
            {links.map((link, i) => (
              <li
                key={i}
                style={{ display: "flex", gap: 8, alignItems: "baseline" }}
              >
                <span
                  style={{
                    fontSize: 10,
                    color: "#334155",
                    fontFamily: "var(--mono)",
                    width: 22,
                    flexShrink: 0,
                  }}
                >
                  {i + 1}
                </span>
                <a
                  href={link.href || link}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    fontSize: 12,
                    color: "#60a5fa",
                    textDecoration: "none",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {link.text || link.href || link}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Stat({ value, label: lbl, color }) {
  return (
    <div style={{ display: "flex", alignItems: "baseline", gap: 4 }}>
      <span style={{ fontSize: 15, fontWeight: 700, color }}>{value}</span>
      <span style={{ fontSize: 11, color: "var(--muted)" }}>{lbl}</span>
    </div>
  );
}
