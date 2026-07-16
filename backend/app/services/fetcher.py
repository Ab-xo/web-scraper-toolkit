import httpx
import re
from typing import Tuple
from app.config import settings

MIN_HTML_LENGTH = 500       # raw HTML bytes
MIN_VISIBLE_TEXT = 100      # visible text chars after stripping tags


def looks_like_spa_shell(html: str) -> bool:
    """Return True if the page looks like an empty JS bundle with no real content."""
    if len(html) < MIN_HTML_LENGTH:
        return True
    text_only = re.sub(r"<[^>]+>", " ", html)
    text_only = re.sub(r"\s+", " ", text_only).strip()
    return len(text_only) < MIN_VISIBLE_TEXT


async def fetch_static(url: str) -> str:
    """Fast path: plain HTTP fetch for static/server-rendered sites."""
    headers = {"User-Agent": settings.user_agent}
    async with httpx.AsyncClient(
        timeout=settings.request_timeout,
        follow_redirects=True,
        verify=False,  # allow self-signed certs
    ) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


async def fetch_rendered(url: str) -> str:
    """Slow path: headless browser for JS-rendered pages."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(user_agent=settings.user_agent)
        await page.goto(
            url,
            timeout=settings.request_timeout * 1000,
            wait_until="networkidle",  # wait for JS to settle
        )
        html = await page.content()
        await browser.close()
        return html


async def fetch_html(url: str) -> Tuple[str, str]:
    """Fetch a page's HTML, picking the fastest method that actually works."""
    try:
        html = await fetch_static(url)
    except (httpx.HTTPError, httpx.TimeoutException, httpx.ConnectError, Exception) as exc:
        raise ValueError(f"Failed to fetch URL: {exc}") from exc

    if looks_like_spa_shell(html):
        try:
            html = await fetch_rendered(url)
        except Exception as exc:
            raise ValueError(f"Playwright render failed: {exc}") from exc
        return html, "playwright"

    return html, "httpx"


from urllib.parse import urljoin
from bs4 import BeautifulSoup


def find_next_page_url(html: str, current_url: str) -> str | None:
    """Find the 'next page' link in paginated HTML."""
    soup = BeautifulSoup(html, "lxml")
    # common patterns: rel=next, text contains Next, li.next a
    for selector in [
        "a[rel=next]",
        "li.next a",
        ".next a",
        "a.next",
    ]:
        tag = soup.select_one(selector)
        if tag and tag.get("href"):
            return urljoin(current_url, tag["href"])

    # fallback: any anchor whose text is "Next" or "→" or ">"
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True).lower()
        if text in ("next", "next »", "next→", "→", ">", "»"):
            return urljoin(current_url, a["href"])

    return None


async def fetch_pages(
    start_url: str,
    max_pages: int = 5,
) -> list[tuple[str, str]]:
    """
    Fetch up to max_pages pages starting from start_url, following next-page links.
    Returns list of (html, url) tuples.
    """
    pages: list[tuple[str, str]] = []
    current_url = start_url

    for _ in range(max_pages):
        try:
            html, _ = await fetch_html(current_url)
        except ValueError:
            break
        pages.append((html, current_url))
        next_url = find_next_page_url(html, current_url)
        if not next_url or next_url == current_url:
            break
        current_url = next_url

    return pages
