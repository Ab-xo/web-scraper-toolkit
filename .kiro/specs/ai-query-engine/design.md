# Design Document — AI-Powered Query Engine

## Overview

The existing rule-based query engine is replaced with a two-tier system:

1. **AI tier** — sends a compact DOM skeleton + user intent to Groq's LLM API (OpenAI-compatible). The LLM returns a CSS selector and a short summary of what it found.
2. **Fallback tier** — the existing token-scoring rule engine, used when the AI is unavailable, unconfigured, or returns an empty selector.

The change is entirely backend. The frontend receives two new fields in the query response (`ai_powered`, `fallback`, `summary`) and renders them as badges and a summary block.

---

## Architecture

```
User intent
    │
    ▼
QueryRequest (FastAPI POST /api/query)
    │
    ▼
ai_query_engine.run_query(html, intent)
    ├── GROQ_API_KEY set?
    │       │ yes
    │       ▼
    │   build_dom_skeleton(html)  ← strips scripts, truncates to 4000 chars
    │       │
    │       ▼
    │   call_groq_llm(skeleton, intent)
    │       │
    │       ├── success → (css_selector, summary)
    │       │       │
    │       │       ▼
    │       │   soup.select(css_selector) → results
    │       │       │
    │       │       ├── results found → return {ai_powered:true, results, summary}
    │       │       └── empty → fallback_engine + {fallback:true}
    │       │
    │       └── error/timeout → fallback_engine + {fallback:true}
    │
    └── no API key → fallback_engine + {fallback:true}
```

---

## Components and Interfaces

### `backend/app/services/ai_query_engine.py` (new)

Replaces `query_engine.py` as the entry point for `/api/query`.

```python
async def run_query(html: str, intent: str) -> dict:
    """Returns QueryResponse-compatible dict with ai_powered, fallback, summary fields."""
```

### `backend/app/services/dom_skeleton.py` (new)

Builds a stripped, compact HTML skeleton for the LLM prompt.

```python
def build_skeleton(html: str, max_chars: int = 4000) -> str:
    """Strip scripts/styles/events, keep tag names + id/class attrs, truncate."""
```

### `backend/app/services/groq_client.py` (new)

Thin async wrapper around the Groq OpenAI-compatible API.

```python
async def ask_groq(skeleton: str, intent: str) -> tuple[str, str]:
    """Returns (css_selector, summary). Raises on API error."""
```

### `backend/app/services/query_engine.py` (existing, unchanged)

Kept as-is — called when AI is unavailable.

### `backend/app/config.py` (updated)

Three new settings:

- `groq_api_key: str = ""`
- `ai_model: str = "openai/gpt-4o"`
- `ai_base_url: str = "https://api.groq.com/openai/v1"`

### `backend/app/models/schemas.py` (updated)

`QueryResponse` gains:

- `ai_powered: bool = False`
- `fallback: bool = False`
- `summary: str | None = None`

### Frontend `QueryPanel.jsx` (updated)

Renders:

- An **AI** badge (purple) when `ai_powered: true`
- A **Rule-based** badge (gray) when `fallback: true`
- A summary block (italic, muted) above results when `summary` is present

---

## Data Models

### LLM Prompt Template

```
You are a CSS selector expert. Given an HTML structure and a user's extraction intent,
return ONLY a valid CSS selector that targets the requested elements.

HTML structure (may be truncated):
<skeleton>

User intent: <intent>

Respond in this exact JSON format:
{"selector": "<css_selector>", "summary": "<one sentence describing what was found>"}

Rules:
- Return only one CSS selector
- Prefer class-based selectors over tag-only selectors when classes are available
- If nothing relevant exists, return {"selector": "", "summary": "No matching elements found."}
```

### Updated QueryResponse

```python
class QueryResponse(BaseModel):
    intent: str
    selector: str
    extract_mode: str
    count: int
    results: list[str]
    ai_powered: bool = False
    fallback: bool = False
    summary: str | None = None
```

---

## Correctness Properties

_A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees._

---

**Property 1: DOM skeleton length is always bounded**

_For any_ HTML document of any size, the DOM skeleton produced by `build_skeleton()` shall never exceed 4000 characters in length.

**Validates: Requirements 4.1, 4.3**

---

**Property 2: DOM skeleton contains no script or style content**

_For any_ HTML document that contains `<script>`, `<style>`, or inline `on*` event attributes, the skeleton produced by `build_skeleton()` shall contain none of those elements or attributes.

**Validates: Requirements 4.2**

---

**Property 3: AI-powered results are a subset of the document**

_For any_ HTML document and any intent, every string in `results` returned by `run_query()` shall be extractable from the original HTML document using the returned `selector`.

**Validates: Requirements 1.1, 1.2**

---

**Property 4: Missing API key always produces fallback response**

_For any_ HTML and intent, when `GROQ_API_KEY` is unset or empty, `run_query()` shall return a response where `fallback: true` and `ai_powered: false`.

**Validates: Requirements 3.4, 1.4**

---

**Property 5: Non-empty results always include a summary**

_For any_ query that returns one or more results, the `summary` field in the response shall be a non-empty string.

**Validates: Requirements 2.1**

---

## Error Handling

| Scenario                        | Behavior                                           |
| ------------------------------- | -------------------------------------------------- |
| `GROQ_API_KEY` not set          | Skip LLM, use rule engine, `fallback: true`        |
| Groq API timeout                | Catch exception, use rule engine, `fallback: true` |
| LLM returns malformed JSON      | Fall back to rule engine                           |
| LLM returns empty selector `""` | Fall back to rule engine                           |
| LLM selector matches nothing    | Fall back to rule engine                           |
| HTML too large (>5MB)           | Rejected at validation layer (existing)            |

No error details from the LLM or HTTP layer are exposed to the client — the response always has a clean structure.

---

## Testing Strategy

### Unit tests

- `test_dom_skeleton.py` — verify skeleton strips scripts/styles, respects 4000 char limit, handles empty HTML
- `test_ai_query_engine.py` — mock the Groq client, test fallback on error, fallback on no API key, correct response shape

### Property-based tests (using `hypothesis`)

- **Property 1** — `@given(html=st.text())` → `len(build_skeleton(html)) <= 4000`
- **Property 2** — `@given(html_with_scripts=...)` → skeleton contains no `<script>` or `on*` attrs
- **Property 3** — `@given(html, intent)` with mocked LLM → all results present in original HTML
- **Property 4** — `@given(html, intent)` with empty API key env var → `fallback: true`
- **Property 5** — `@given(html, intent)` with non-empty result → `summary` is non-empty string

Each property-based test runs a minimum of 100 iterations.

Tag format: `# Feature: ai-query-engine, Property N: <description>`
