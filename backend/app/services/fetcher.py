import httpx
import re
from typing import Tuple
from app.config import settings

MIN_CONTENT_LENGTH = 500  # bytes; SPA shells are often nearly empty

async def fetch_static(url: str) -> str:
    """Fast path: plain HTTP fetch for static/server-rendered sites."""
    headers = {"User-Agent": settings.user_agent}
    async with httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


import re

def looks_like_spa_shell(html: str) -> bool:
    if len(html) < MIN_CONTENT_LENGTH:
        return True
    text_only = re.sub(r"<[^>]+>", " ", html)
    text_only = re.sub(r"\s+", " ", text_only).strip()
    return len(text_only) < 50


async def fetch_rendered(url: str) -> str:
    """Slow path: headless browser for JS-rendered pages."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(user_agent=settings.user_agent)
        await page.goto(url, timeout=settings.request_timeout * 1000, wait_until="domcontentloaded")
        html = await page.content()
        await browser.close()
        return html


async def fetch_html(url: str) -> Tuple[str, str]:
    """Fetch a page's HTML, picking the fastest method that actually works."""
    try:
        html = await fetch_static(url)
    except httpx.HTTPError as exc:
        raise ValueError(f"Failed to fetch URL: {exc}") from exc

    if looks_like_spa_shell(html):
        html = await fetch_rendered(url)
        return html, "playwright"

    return html, "httpx"