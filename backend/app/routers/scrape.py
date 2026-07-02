from fastapi import APIRouter, HTTPException
from app.models.schemas import ScrapeRequest, ScrapeResponse
from app.services.fetcher import fetch_html
from app.services.dom_parser import parse_html_to_tree

router = APIRouter()

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(payload: ScrapeRequest):
    try:
        html, method = await fetch_html(str(payload.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    dom_tree = parse_html_to_tree(html)

    return ScrapeResponse(
        url=str(payload.url),
        method_used=method,
        html_length=len(html),
        dom_tree=dom_tree,
    )