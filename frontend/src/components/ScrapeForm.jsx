import { useState } from "react";

export default function ScrapeForm({ onScrape, status }) {
  const [url, setUrl] = useState("");
  const [usePlaywright, setUsePlaywright] = useState(false);
  const loading = status === "loading";

  const handleScrape = () => {
    const trimmed = url.trim();
    if (!trimmed) return;
    const finalUrl = /^https?:\/\//i.test(trimmed)
      ? trimmed
      : `https://${trimmed}`;
    onScrape(finalUrl, usePlaywright);
  };

  return (
    <div
      style={{
        borderRadius: 10,
        background: "var(--surface)",
        border: "1px solid var(--border)",
        padding: "18px",
      }}
    >
      <div
        style={{
          fontSize: 11,
          fontWeight: 600,
          color: "var(--muted)",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          marginBottom: 12,
        }}
      >
        Target URL
      </div>

      <div style={{ position: "relative", marginBottom: 12 }}>
        <span
          style={{
            position: "absolute",
            left: 10,
            top: "50%",
            transform: "translateY(-50%)",
            color: "var(--muted)",
            fontSize: 13,
            pointerEvents: "none",
          }}
        >
          🔗
        </span>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleScrape()}
          placeholder="https://example.com"
          disabled={loading}
          spellCheck={false}
          style={{
            width: "100%",
            background: "var(--bg)",
            border: "1px solid var(--border2)",
            borderRadius: 7,
            padding: "9px 10px 9px 30px",
            fontSize: 13,
            fontFamily: "var(--mono)",
            color: "#60a5fa",
            outline: "none",
            transition: "border-color 0.15s",
            opacity: loading ? 0.5 : 1,
          }}
          onFocus={(e) => (e.target.style.borderColor = "var(--accent)")}
          onBlur={(e) => (e.target.style.borderColor = "var(--border2)")}
        />
      </div>

      <label
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          cursor: "pointer",
          userSelect: "none",
          marginBottom: 14,
        }}
      >
        <input
          type="checkbox"
          checked={usePlaywright}
          onChange={(e) => setUsePlaywright(e.target.checked)}
          disabled={loading}
          style={{ accentColor: "var(--accent)", width: 14, height: 14 }}
        />
        <span style={{ fontSize: 12, color: "var(--muted)" }}>
          Use Playwright
          <span style={{ color: "#475569", marginLeft: 4 }}>
            (JS-heavy sites)
          </span>
        </span>
      </label>

      <button
        onClick={handleScrape}
        disabled={loading || !url.trim()}
        style={{
          width: "100%",
          padding: "9px",
          borderRadius: 7,
          border: "none",
          background:
            loading || !url.trim()
              ? "var(--border2)"
              : "linear-gradient(135deg, #2563eb, #7c3aed)",
          color: loading || !url.trim() ? "var(--muted)" : "#fff",
          fontSize: 13,
          fontWeight: 600,
          cursor: loading || !url.trim() ? "not-allowed" : "pointer",
          transition: "opacity 0.15s",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
        }}
      >
        {loading ? (
          <>
            <span
              style={{
                width: 13,
                height: 13,
                borderRadius: "50%",
                border: "2px solid rgba(255,255,255,0.25)",
                borderTopColor: "#fff",
                animation: "spin 0.7s linear infinite",
                display: "inline-block",
              }}
            />
            Scraping…
          </>
        ) : (
          "⚡ Scrape"
        )}
      </button>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
