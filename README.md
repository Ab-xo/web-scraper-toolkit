# Web Scraper Toolkit

An AI-powered web scraping tool with a FastAPI backend and React frontend. You type a plain-English query like _"find all travel books"_ or _"get the first 20 quotes and their authors"_ — and the AI figures out what to extract, navigates to the right page if needed, follows pagination, and returns clean structured results.

Built as a portfolio project to demonstrate full-stack development, LLM integration, and professional software engineering practices.

---

## What it does

- **Scrape any URL** — static or JS-rendered (via Playwright fallback)
- **AI-powered queries** — describe what you want in plain English; Groq LLM maps your intent to precise CSS selectors
- **Smart navigation** — AI detects when content is on a different page (e.g. a category) and navigates there automatically
- **Pagination support** — ask for "first 50 books" and it follows next-page links across multiple pages
- **Structured results** — each result renders as a labeled card (Title / Price / Rating / Author etc.)
- **Rule-based fallback** — works without an API key using a built-in keyword matcher
- **Modern dark UI** — real-time status indicator, scrape history, query chips, AI/fallback badges

---

## Tech stack

| Layer    | Technology                                               |
| -------- | -------------------------------------------------------- |
| Backend  | Python 3.11+, FastAPI, httpx, BeautifulSoup4, Playwright |
| AI       | Groq API (llama-3.3-70b-versatile) — OpenAI-compatible   |
| Frontend | React 19, Vite 8, Tailwind CSS v4                        |
| Testing  | pytest, hypothesis (property-based tests)                |

---

## Project structure

```
web-scraper-toolkit/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, security headers
│   │   ├── config.py            # Settings loaded from .env
│   │   ├── models/schemas.py    # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── scrape.py        # POST /api/scrape
│   │   │   └── query.py         # POST /api/query
│   │   └── services/
│   │       ├── fetcher.py       # httpx + Playwright fetcher, pagination
│   │       ├── dom_parser.py    # BeautifulSoup DOM tree + link/text extraction
│   │       ├── dom_skeleton.py  # Compact HTML skeleton for LLM prompts
│   │       ├── groq_client.py   # Groq API client — returns extraction plan
│   │       ├── ai_query_engine.py  # Orchestrator: navigate → extract → paginate
│   │       └── query_engine.py  # Rule-based fallback engine
│   ├── tests/
│   │   ├── test_dom_skeleton.py    # Property tests: skeleton size, script stripping
│   │   └── test_ai_query_engine.py # Property tests: fallback, results subset, summary
│   ├── .env.example             # Copy to .env and add your Groq key
│   └── requirements.txt
└── frontend/
    └── src/
        ├── components/
        │   ├── ScrapeForm.jsx   # URL input + Playwright toggle
        │   ├── ResultsPanel.jsx # Scraped page summary, links, text
        │   ├── QueryPanel.jsx   # AI query input, chips, structured result cards
        │   ├── HistoryList.jsx  # Recent scrapes sidebar
        │   └── StatusBar.jsx    # Live backend health indicator
        ├── hooks/useScraper.js  # State management for scrape + query
        └── api/client.js        # Axios API client
```

---

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A free [Groq API key](https://console.groq.com) (optional — works without one)

### 1. Clone the repo

```bash
git clone https://github.com/Ab-xo/web-scraper-toolkit.git
cd web-scraper-toolkit
```

### 2. Backend setup

```powershell
# Create venv inside backend/
python -m venv backend\.venv
backend\.venv\Scripts\activate   # Windows
# source backend/.venv/bin/activate  # Mac/Linux

pip install -r backend/requirements.txt

# Install Playwright browser (needed for JS-heavy sites)
playwright install chromium
```

Set up your environment:

```powershell
copy backend\.env.example backend\.env
# Open backend/.env and add your GROQ_API_KEY
```

Start the backend:

```powershell
cd backend
uvicorn app.main:app --reload
# Runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

---

## Usage

1. Open `http://localhost:5173`
2. Paste any URL and click **Scrape**
3. Switch to the **Query** tab
4. Type a plain-English query, e.g.:
   - `find all travel books`
   - `get the first 20 quotes and their authors`
   - `show all product prices`
   - `find all navigation links`
5. Hit **Run Query** — the ✦ AI badge means Groq powered it; **Rule-based** means the fallback ran

### Verify AI is configured

Visit `http://localhost:8000/api/config-check` — should return `"ai_configured": true`.

---

## Running tests

```powershell
cd backend
..\.venv\Scripts\pytest tests/ -v --asyncio-mode=auto
```

---

## Environment variables

| Variable       | Default                          | Description                |
| -------------- | -------------------------------- | -------------------------- |
| `GROQ_API_KEY` | _(empty)_                        | Your Groq API key          |
| `AI_MODEL`     | `llama-3.3-70b-versatile`        | Any Groq-compatible model  |
| `AI_BASE_URL`  | `https://api.groq.com/openai/v1` | OpenAI-compatible endpoint |

---

## License

MIT
