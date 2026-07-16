from fastapi import APIRouter, HTTPException
from app.models.schemas import ScrapeRequest, ScrapeResponse
from app.services.fetcher import fetch_html
from app.services.dom_parser import parse_html_to_tree, extract_title, extract_text, extract_links

router = APIRouter()

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(payload: ScrapeRequest):
    try:
        html, method = await fetch_html(str(payload.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    url_str = str(payload.url)

    return ScrapeResponse(
        url=url_str,
        method_used=method,
        html_length=len(html),
        dom_tree=parse_html_to_tree(html),
        title=extract_title(html),
        text=extract_text(html),
        links=extract_links(html, base_url=url_str),
        html=html,
    )