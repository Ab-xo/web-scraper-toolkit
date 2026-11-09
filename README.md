# Web Scraper Toolkit

An AI-assisted web scraping platform with a FastAPI backend and React frontend. Users describe what to extract in plain English, and the system creates a structured extraction plan, handles navigation and pagination, and returns organized results.

## Features

- Static and JavaScript-rendered page scraping
- Natural-language extraction queries through Groq
- Playwright fallback for dynamic websites
- Pagination and cross-page navigation
- Structured result cards and scrape history
- Rule-based fallback when AI configuration is unavailable
- Automated backend tests

## Technology

| Layer | Stack |
|---|---|
| Backend | Python, FastAPI, httpx, BeautifulSoup4, Playwright |
| AI | Groq-compatible API |
| Frontend | React 19, Vite, Tailwind CSS |
| Testing | pytest, Hypothesis |

## Getting started

```bash
python -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
playwright install chromium
cd frontend && npm install && npm run dev
```

Configure `GROQ_API_KEY` in `backend/.env` when AI extraction is desired. The rule-based engine remains available without a key.

## Usage

1. Open the frontend
2. Enter a URL and scrape it
3. Switch to the query view
4. Describe the fields or records to extract
5. Review the structured results

## Testing

```bash
cd backend
pytest tests/ -v --asyncio-mode=auto
```

## License

MIT
