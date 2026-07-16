import { useState } from "react";
import { useScraper } from "./hooks/useScraper";
import StatusBar from "./components/StatusBar";
import ScrapeForm from "./components/ScrapeForm";
import ResultsPanel from "./components/ResultsPanel";
import QueryPanel from "./components/QueryPanel";
import HistoryList from "./components/HistoryList";

const TABS = [
  { id: "results", label: "Results", icon: "◈" },
  { id: "query", label: "Query", icon: "⌖" },
  { id: "raw", label: "Raw HTML", icon: "⟨⟩" },
];

export default function App() {
  const { status, result, error, history, scrape, query } = useScraper();
  const [tab, setTab] = useState("results");

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--bg)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <StatusBar />

      {/* Header */}
      <header
        style={{
          borderBottom: "1px solid var(--border)",
          padding: "16px 32px",
          display: "flex",
          alignItems: "center",
          gap: "12px",
          background: "var(--surface)",
        }}
      >
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: 8,
            background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 18,
            flexShrink: 0,
          }}
        >
          🕸️
        </div>
        <div>
          <div
            style={{
              fontWeight: 700,
              fontSize: 16,
              letterSpacing: "-0.3px",
              color: "var(--text)",
            }}
          >
            Web Scraper Toolkit
          </div>
          <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 1 }}>
            Fetch · Parse · Query — any page
          </div>
        </div>
      </header>

      {/* Main layout */}
      <div
        style={{
          flex: 1,
          display: "grid",
          gridTemplateColumns: "300px 1fr",
          gap: 0,
          maxWidth: 1280,
          width: "100%",
          margin: "0 auto",
          padding: "24px 24px",
          gap: "20px",
        }}
      >
        {/* Sidebar */}
        <aside style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <ScrapeForm onScrape={scrape} status={status} />
          <HistoryList history={history} onSelect={(url) => scrape(url)} />
        </aside>

        {/* Main panel */}
        <section
          style={{
            minWidth: 0,
            display: "flex",
            flexDirection: "column",
            gap: 16,
          }}
        >
          {/* Tabs */}
          <div
            style={{
              display: "flex",
              gap: 2,
              borderBottom: "1px solid var(--border)",
              paddingBottom: 0,
            }}
          >
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                style={{
                  padding: "8px 16px",
                  fontSize: 13,
                  fontWeight: tab === t.id ? 600 : 400,
                  color: tab === t.id ? "var(--text)" : "var(--muted)",
                  background: "none",
                  border: "none",
                  borderBottom:
                    tab === t.id
                      ? "2px solid var(--accent)"
                      : "2px solid transparent",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  marginBottom: -1,
                  transition: "color 0.15s",
                }}
              >
                <span style={{ fontFamily: "monospace", fontSize: 14 }}>
                  {t.icon}
                </span>
                {t.label}
              </button>
            ))}
          </div>

          {tab === "results" && (
            <ResultsPanel status={status} result={result} error={error} />
          )}
          {tab === "query" && <QueryPanel result={result} onQuery={query} />}
          {tab === "raw" && <RawPanel result={result} />}
        </section>
      </div>
    </div>
  );
}

function RawPanel({ result }) {
  if (!result?.html)
    return (
      <EmptyState icon="⟨⟩" text="Scrape a page first to view raw HTML." />
    );
  return (
    <div
      style={{
        borderRadius: 10,
        background: "var(--surface)",
        border: "1px solid var(--border)",
        padding: "16px",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <span
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: "var(--muted)",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
          }}
        >
          Raw HTML
        </span>
        <span
          style={{
            fontSize: 11,
            color: "var(--muted)",
            fontFamily: "var(--mono)",
          }}
        >
          {(result.html.length / 1000).toFixed(1)}k chars
        </span>
      </div>
      <pre
        style={{
          margin: 0,
          fontSize: 12,
          fontFamily: "var(--mono)",
          color: "#94a3b8",
          overflowX: "auto",
          overflowY: "auto",
          maxHeight: 560,
          whiteSpace: "pre-wrap",
          wordBreak: "break-all",
          lineHeight: 1.6,
        }}
      >
        {result.html}
      </pre>
    </div>
  );
}

export function EmptyState({ icon, text }) {
  return (
    <div
      style={{
        borderRadius: 10,
        background: "var(--surface)",
        border: "1px solid var(--border)",
        padding: "60px 24px",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 32, marginBottom: 12 }}>{icon}</div>
      <p style={{ color: "var(--muted)", fontSize: 13, margin: 0 }}>{text}</p>
    </div>
  );
}
