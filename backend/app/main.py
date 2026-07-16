import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import scrape, query

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
)

# ── Security headers middleware ───────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    return response

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(scrape.router, prefix="/api", tags=["scrape"])
app.include_router(query.router,  prefix="/api", tags=["query"])

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/")
@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok", "service": settings.app_name}


@app.get("/api/config-check")
def config_check():
    """Debug endpoint — shows whether AI is configured (never exposes the key)."""
    return {
        "ai_configured": bool(settings.groq_api_key),
        "ai_model": settings.ai_model,
        "ai_base_url": settings.ai_base_url,
    }
