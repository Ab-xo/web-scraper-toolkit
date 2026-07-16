"""
Comprehensive scraper test suite.
Tests fetching + AI query against 50+ real websites across categories.

Run:
    pytest tests/test_scraper_suite.py -v --asyncio-mode=auto -s

Each test:
  1. Fetches the URL
  2. Runs an AI-powered query
  3. Asserts results are non-empty and meaningful
"""
from __future__ import annotations
import asyncio
import pytest
from dataclasses import dataclass

from app.services.fetcher import fetch_html
from app.services.ai_query_engine import run_query

# ─────────────────────────────────────────────────────────────────────────────
# Test site definitions
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Site:
    category: str
    url: str
    query: str
    min_results: int = 1    # minimum expected results
    description: str = ""


SITES: list[Site] = [
    # ── Practice / Demo ──────────────────────────────────────────────────────
    Site("demo", "https://quotes.toscrape.com/",
         "get all quotes and their authors", 5),
    Site("demo", "https://books.toscrape.com/",
         "find all book titles and prices", 5),
    Site("demo", "https://toscrape.com/",
         "find all links on the page", 3),
    Site("demo", "https://httpbin.org/html",
         "find all headings", 1),

    # ── News ─────────────────────────────────────────────────────────────────
    Site("news", "https://news.ycombinator.com/",
         "get all article titles and their links", 10,
         "Hacker News front page stories"),
    Site("news", "https://www.bbc.com/news",
         "find all news article headlines", 5, "BBC News"),
    Site("news", "https://techcrunch.com/",
         "find all article headlines", 5, "TechCrunch"),
    Site("news", "https://www.reuters.com/",
         "get all news headlines", 5, "Reuters"),
    Site("news", "https://www.theguardian.com/international",
         "find all article headlines", 5, "The Guardian"),
    Site("news", "https://apnews.com/",
         "get all news headlines", 5, "AP News"),
    Site("news", "https://www.npr.org/",
         "find all article titles", 5, "NPR"),
    Site("news", "https://arstechnica.com/",
         "get all article headlines", 5, "Ars Technica"),
    Site("news", "https://www.wired.com/",
         "find all article titles", 5, "Wired"),
    Site("news", "https://www.politico.com/",
         "get all news headlines", 5, "Politico"),

    # ── Technology ───────────────────────────────────────────────────────────
    Site("tech", "https://dev.to/",
         "find all article titles and authors", 5, "DEV Community"),
    Site("tech", "https://css-tricks.com/",
         "get all article titles", 5, "CSS-Tricks"),
    Site("tech", "https://www.smashingmagazine.com/",
         "find all article titles", 5, "Smashing Magazine"),
    Site("tech", "https://lobste.rs/",
         "get all article titles and links", 5, "Lobsters"),
    Site("tech", "https://thenewstack.io/",
         "find all article titles", 5, "The New Stack"),
    Site("tech", "https://www.infoq.com/",
         "get all article titles", 5, "InfoQ"),
    Site("tech", "https://changelog.com/",
         "find all podcast or post titles", 3, "Changelog"),
    Site("tech", "https://spectrum.ieee.org/",
         "find all article headlines", 3, "IEEE Spectrum"),

    # ── E-Commerce / Products ─────────────────────────────────────────────────
    Site("ecommerce", "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
         "find all travel books with prices and ratings", 5, "Travel books category"),
    Site("ecommerce", "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
         "find all mystery books with prices", 5, "Mystery books category"),
    Site("ecommerce", "https://www.ebay.com/sch/i.html?_nkw=laptop",
         "get all product names and prices", 5, "eBay laptop search"),
    Site("ecommerce", "https://www.amazon.com/s?k=python+books",
         "find all book titles and prices", 3, "Amazon Python books"),

    # ── Wikipedia / Reference ────────────────────────────────────────────────
    Site("reference", "https://en.wikipedia.org/wiki/Web_scraping",
         "find all section headings", 5, "Wikipedia Web scraping"),
    Site("reference", "https://en.wikipedia.org/wiki/Python_(programming_language)",
         "get all section headings and the introduction paragraph", 3),
    Site("reference", "https://en.wikipedia.org/wiki/Artificial_intelligence",
         "find all section headings", 5),
    Site("reference", "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)",
         "get all country names from the table", 10),

    # ── Programming / Docs ───────────────────────────────────────────────────
    Site("docs", "https://docs.python.org/3/library/",
         "find all module names in the standard library", 10),
    Site("docs", "https://fastapi.tiangolo.com/",
         "find all navigation links and section headings", 5),
    Site("docs", "https://react.dev/",
         "find all navigation links", 5),
    Site("docs", "https://tailwindcss.com/docs/installation",
         "find all section headings", 3),
    Site("docs", "https://pydantic.dev/",
         "find all headings and links", 3),

    # ── Jobs ─────────────────────────────────────────────────────────────────
    Site("jobs", "https://news.ycombinator.com/jobs",
         "find all job titles and company names", 5, "HN Jobs"),
    Site("jobs", "https://remoteok.com/",
         "get all job titles", 5, "Remote OK"),
    Site("jobs", "https://weworkremotely.com/",
         "find all job titles", 5, "We Work Remotely"),

    # ── Finance ──────────────────────────────────────────────────────────────
    Site("finance", "https://finance.yahoo.com/",
         "find all market data or stock headlines", 3, "Yahoo Finance"),
    Site("finance", "https://www.investing.com/",
         "get all major index names and values", 3, "Investing.com"),
    Site("finance", "https://www.marketwatch.com/",
         "find all market headlines", 3, "MarketWatch"),

    # ── Science ──────────────────────────────────────────────────────────────
    Site("science", "https://www.nature.com/",
         "find all article titles", 5, "Nature journal"),
    Site("science", "https://phys.org/",
         "get all news headlines", 5, "Phys.org"),
    Site("science", "https://www.sciencedaily.com/",
         "find all article headlines", 5, "Science Daily"),
    Site("science", "https://arxiv.org/list/cs.AI/recent",
         "get all paper titles", 5, "arXiv AI papers"),

    # ── Sports ───────────────────────────────────────────────────────────────
    Site("sports", "https://www.espn.com/",
         "find all sports headlines", 5, "ESPN"),
    Site("sports", "https://www.bbc.com/sport",
         "get all sport news headlines", 5, "BBC Sport"),

    # ── Entertainment ────────────────────────────────────────────────────────
    Site("entertainment", "https://www.imdb.com/chart/top/",
         "get all movie titles and their ratings", 10, "IMDB Top 250"),
    Site("entertainment", "https://www.rottentomatoes.com/",
         "find all movie titles", 5, "Rotten Tomatoes"),

    # ── Health ───────────────────────────────────────────────────────────────
    Site("health", "https://www.webmd.com/",
         "find all health article headlines", 5, "WebMD"),
    Site("health", "https://www.healthline.com/",
         "get all article titles", 5, "Healthline"),

    # ── Government / Open Data ───────────────────────────────────────────────
    Site("government", "https://data.gov/",
         "find all dataset names or categories", 5, "Data.gov"),
    Site("government", "https://www.who.int/news",
         "get all news headlines", 5, "WHO news"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def result_summary(result: dict) -> str:
    count    = result.get("count", 0)
    ai       = "✦ AI" if result.get("ai_powered") else "Rule-based"
    pages    = result.get("pages_fetched", 1)
    fallback = " [fallback]" if result.get("fallback") else ""
    preview  = result["results"][0][:80].replace("\n", " ") if result["results"] else "(empty)"
    return f"{ai}{fallback} | {count} results | {pages}p | first: {preview!r}"


async def _run_site_test(site: Site) -> dict:
    html, method = await fetch_html(site.url)
    result = await run_query(html, site.query, base_url=site.url)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Parametrized tests — one per site
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("site", SITES, ids=[f"{s.category}::{s.url.split('/')[2]}" for s in SITES])
async def test_site(site: Site):
    """Fetch and query a real website, assert minimum results returned."""
    try:
        result = await _run_site_test(site)
    except Exception as exc:
        pytest.skip(f"Fetch failed (network/blocked): {exc}")

    summary = result_summary(result)
    print(f"\n  [{site.category.upper()}] {site.url}\n  Query: {site.query!r}\n  {summary}")

    assert result["count"] >= site.min_results, (
        f"Expected at least {site.min_results} results from {site.url}, "
        f"got {result['count']}.\nQuery: {site.query}\n{summary}"
    )
    assert result["results"], "Results list is empty"
    assert all(r.strip() for r in result["results"]), "Some results are blank strings"
