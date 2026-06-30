from fastapi import APIRouter, HTTPException
from app.models.schemas import ScrapeRequest, ScrapeResponse
from app.services.fetcher import fetch_html

router = APIRouter()

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(payload: ScrapeRequest):
    try:
        html, method = await fetch_html(str(payload.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return ScrapeResponse(
        url=str(payload.url),
        method_used=method,
        html_length=len(html),
    )