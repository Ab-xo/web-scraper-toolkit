import { useState } from "react";

const EXAMPLES = [
  { label: "All headings", query: "find all headings" },
  { label: "All links", query: "find all links" },
  { label: "Images", query: "extract all image URLs" },
  { label: "Prices", query: "get every product price" },
  { label: "Paragraphs", query: "extract body paragraphs" },
  { label: "Nav items", query: "list navigation menu items" },
  { label: "Author names", query: "find author names" },
  { label: "Dates", query: "find all dates and times" },
  { label: "Email addresses", query: "find all email addresses" },
  { label: "Code snippets", query: "find all code snippets" },
];

const card = {
  borderRadius: 10,
  background: "var(--surface)",
  border: "1px solid var(--border)",
  padding: "18px",
};

export default function QueryPanel({ result, onQuery }) {
  const [intent, setIntent] = useState("");
  const [queryResult, setQueryResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  const runQuery = async () => {
    if (!result?.html || !intent.trim()) return;
    setLoading(true);
    setErr(null);
    setQueryResult(null);
    try {
      const data = await onQuery(
        result.html,
        intent.trim(),
        result.url ?? null,
      );
      setQueryResult(data);
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (!result)
    return (
      <div style={{ ...card, padding: "60px 24px", textAlign: "center" }}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>⌖</div>
        <p style={{ color: "var(--muted)", fontSize: 13, margin: 0 }}>
          Scrape a page first, then query it here.
        </p>
      </div>
    );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {/* Input card */}
      <div style={card}>
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: "var(--muted)",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            marginBottom: 4,
          }}
        >
          Natural Language Query
        </div>
        <p style={{ fontSize: 12, color: "var(--muted)", margin: "0 0 12px" }}>
          Describe what to extract in plain English — AI understands your intent
          and finds the right content.
        </p>

        <input
          type="text"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runQuery()}
          placeholder='e.g. "find all article headings"'
          disabled={loading}
          style={{
            width: "100%",
            background: "var(--bg)",
            border: "1px solid var(--border2)",
            borderRadius: 7,
            padding: "10px 14px",
            fontSize: 13,
            color: "var(--text)",
            outline: "none",
            transition: "border-color 0.15s",
            opacity: loading ? 0.5 : 1,
            marginBottom: 12,
          }}
          onFocus={(e) => (e.target.style.borderColor = "#8b5cf6")}
          onBlur={(e) => (e.target.style.borderColor = "var(--border2)")}
        />

        {/* Example chips */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 6,
            marginBottom: 14,
          }}
        >
          {EXAMPLES.map((ex) => (
            <button
              key={ex.query}
              onClick={() => setIntent(ex.query)}
              style={{
                fontSize: 11,
                padding: "4px 10px",
                borderRadius: 99,
                background:
                  intent === ex.query
                    ? "rgba(139,92,246,0.2)"
                    : "var(--surface2)",
                color: intent === ex.query ? "#a78bfa" : "var(--muted)",
                border: `1px solid ${intent === ex.query ? "rgba(139,92,246,0.4)" : "var(--border)"}`,
                cursor: "pointer",
                transition: "all 0.15s",
              }}
            >
              {ex.label}
            </button>
          ))}
        </div>

        <button
          onClick={runQuery}
          disabled={loading || !intent.trim()}
          style={{
            width: "100%",
            padding: "9px",
            borderRadius: 7,
            border: "none",
            background:
              loading || !intent.trim()
                ? "var(--border2)"
                : "linear-gradient(135deg, #6d28d9, #4f46e5)",
            color: loading || !intent.trim() ? "var(--muted)" : "#fff",
            fontSize: 13,
            fontWeight: 600,
            cursor: loading || !intent.trim() ? "not-allowed" : "pointer",
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
              Running query…
            </>
          ) : (
            "⌖ Run Query"
          )}
        </button>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>

      {/* Error */}
      {err && (
        <div
          style={{
            ...card,
            background: "rgba(239,68,68,0.06)",
            borderColor: "rgba(239,68,68,0.3)",
            padding: "12px 16px",
          }}
        >
          <span style={{ fontSize: 12, color: "var(--red)" }}>{err}</span>
        </div>
      )}

      {/* Results card */}
      {queryResult && (
        <div style={card}>
          {/* Header: label + count + badges */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 12,
              flexWrap: "wrap",
              gap: 8,
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
              Results
            </span>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span
                style={{ fontSize: 12, color: "var(--green)", fontWeight: 600 }}
              >
                {queryResult.count} match{queryResult.count !== 1 ? "es" : ""}
              </span>

              {/* AI badge — Requirements 5.1 */}
              {queryResult.ai_powered && (
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: 99,
                    background:
                      "linear-gradient(135deg,rgba(139,92,246,0.25),rgba(99,102,241,0.25))",
                    color: "#a78bfa",
                    border: "1px solid rgba(139,92,246,0.4)",
                    letterSpacing: "0.04em",
                  }}
                >
                  ✦ AI
                </span>
              )}

              {/* Rule-based badge — Requirements 5.2 */}
              {queryResult.fallback && (
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 600,
                    padding: "2px 8px",
                    borderRadius: 99,
                    background: "rgba(100,116,139,0.15)",
                    color: "var(--muted)",
                    border: "1px solid rgba(100,116,139,0.3)",
                  }}
                >
                  Rule-based
                </span>
              )}

              {/* Pages fetched badge */}
              {queryResult.pages_fetched > 1 && (
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 600,
                    padding: "2px 8px",
                    borderRadius: 99,
                    background: "rgba(34,197,94,0.12)",
                    color: "#4ade80",
                    border: "1px solid rgba(34,197,94,0.25)",
                  }}
                >
                  {queryResult.pages_fetched} pages
                </span>
              )}
            </div>
          </div>

          {/* AI summary block — Requirements 5.3 (rendered above results list) */}
          {queryResult.summary && (
            <div
              style={{
                marginBottom: 12,
                padding: "10px 12px",
                borderRadius: 7,
                background: queryResult.ai_powered
                  ? "rgba(139,92,246,0.08)"
                  : "rgba(100,116,139,0.08)",
                border: `1px solid ${queryResult.ai_powered ? "rgba(139,92,246,0.2)" : "rgba(100,116,139,0.2)"}`,
              }}
            >
              <p
                style={{
                  margin: 0,
                  fontSize: 12,
                  color: "#94a3b8",
                  fontStyle: "italic",
                  lineHeight: 1.6,
                }}
              >
                {queryResult.summary}
              </p>
            </div>
          )}

          {/* Selector + mode — only show for AI results */}
          {queryResult.ai_powered && queryResult.selector && (
            <div
              style={{
                marginBottom: 12,
                display: "flex",
                alignItems: "center",
                gap: 8,
                flexWrap: "wrap",
              }}
            >
              <span style={{ fontSize: 11, color: "var(--muted)" }}>
                Selector:
              </span>
              <code
                style={{
                  fontSize: 11,
                  fontFamily: "var(--mono)",
                  color: "#c084fc",
                  background: "rgba(192,132,252,0.1)",
                  border: "1px solid rgba(192,132,252,0.2)",
                  padding: "2px 8px",
                  borderRadius: 5,
                }}
              >
                {queryResult.selector}
              </code>
              <span style={{ fontSize: 11, color: "var(--muted)" }}>mode:</span>
              <code
                style={{
                  fontSize: 11,
                  fontFamily: "var(--mono)",
                  color: "#34d399",
                  background: "rgba(52,211,153,0.1)",
                  border: "1px solid rgba(52,211,153,0.2)",
                  padding: "2px 8px",
                  borderRadius: 5,
                }}
              >
                {queryResult.extract_mode}
              </code>
            </div>
          )}

          {/* Results list */}
          {queryResult.count === 0 ? (
            <p
              style={{
                fontSize: 13,
                color: "var(--muted)",
                textAlign: "center",
                padding: "20px 0",
                margin: 0,
              }}
            >
              No matches found. Try a different query.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {queryResult.results.map((item, i) => {
                // Parse "Field: value\nField: value" into structured rows
                const lines = item.split("\n").filter(Boolean);
                const isStructured =
                  lines.length > 1 && lines[0].includes(": ");
                return (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      gap: 10,
                      alignItems: "flex-start",
                    }}
                  >
                    <span
                      style={{
                        fontSize: 10,
                        color: "#334155",
                        fontFamily: "var(--mono)",
                        paddingTop: 10,
                        width: 26,
                        flexShrink: 0,
                        textAlign: "right",
                      }}
                    >
                      {i + 1}
                    </span>
                    <div
                      style={{
                        flex: 1,
                        background: "var(--bg)",
                        border: "1px solid var(--border)",
                        borderRadius: 8,
                        overflow: "hidden",
                      }}
                    >
                      {isStructured ? (
                        <table
                          style={{ width: "100%", borderCollapse: "collapse" }}
                        >
                          <tbody>
                            {lines.map((line, li) => {
                              const colon = line.indexOf(": ");
                              const key =
                                colon > -1 ? line.slice(0, colon) : "Value";
                              const val =
                                colon > -1 ? line.slice(colon + 2) : line;
                              return (
                                <tr
                                  key={li}
                                  style={{
                                    borderBottom:
                                      li < lines.length - 1
                                        ? "1px solid var(--border)"
                                        : "none",
                                  }}
                                >
                                  <td
                                    style={{
                                      padding: "7px 12px",
                                      fontSize: 11,
                                      fontWeight: 600,
                                      color: "var(--muted)",
                                      whiteSpace: "nowrap",
                                      width: 90,
                                      verticalAlign: "top",
                                      borderRight: "1px solid var(--border)",
                                    }}
                                  >
                                    {key}
                                  </td>
                                  <td
                                    style={{
                                      padding: "7px 12px",
                                      fontSize: 13,
                                      color: "var(--text)",
                                      lineHeight: 1.5,
                                      wordBreak: "break-word",
                                    }}
                                  >
                                    {val}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      ) : (
                        <div
                          style={{
                            padding: "10px 14px",
                            fontSize: 13,
                            color: "var(--text)",
                            lineHeight: 1.6,
                            wordBreak: "break-word",
                          }}
                        >
                          {item}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
