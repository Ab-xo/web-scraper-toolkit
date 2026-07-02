# Web Scraper Toolkit

A lightweight web scraping toolkit with a FastAPI backend and a Vite + React frontend. The project provides modular components to fetch pages, parse DOM structures, and run queries over parsed content—useful for building scraping workflows, experiments, and small RAG/Retrieval prototypes.

## Features
- FastAPI backend with organized routers and services
- Modular services: `fetcher`, `dom_parser`, and `query_engine`
- Utilities for HTML cleaning and DOM inspection
- Minimal React frontend (Vite) for interacting with the scraper
- Unit tests for core components under `tests/`

## Tech stack
- Python + FastAPI
- Vite + React for frontend
- Tailwind for styling

## Quickstart
1. Backend: create and activate a virtualenv, then install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```
2. Frontend: install and run the dev server from `frontend/`:

```bash
cd frontend
npm install
npm run dev
```

See the source folders for implementation details: `backend/app/` and `frontend/src/`.

