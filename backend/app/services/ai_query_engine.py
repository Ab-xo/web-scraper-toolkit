"""
AI-powered query engine.
- Passes base_url into skeleton builder so links section has full absolute URLs
- Follows AI-suggested navigation (using exact links from the page)
- Structured per-field extraction with pagination support
"""
from __future__ import annotations
import re
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from app.config import settings
from app.services.dom_skeleton import build_skeleton
from app.services.query_engine import run_query as rule_based_query
from app.services.groq_client import ask_groq

log = logging.getLogger(__name__)


def _extract_structured(html: str, container: str, fields: dict, limit: int = 200) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    results = []
    for el in soup.select(container)[:limit]:
        row = {}
        for fname, sel in fields.items():
            if sel == "self":
                val = el.get_text(separator=" ", strip=True)
            else:
                sub = el.select_one(sel)
                if sub:
                    # prefer title attr (book titles), else alt, else text
                    val = sub.get("title") or sub.get("alt") or sub.get_text(separator=" ", strip=True)
                else:
                    val = ""
            row[fname] = (val or "").strip()
        if any(row.values()):
            results.append(row)
    return results


def _parse_count(intent: str) -> int | None:
    m = re.search(r"\b(\d+)\b", intent)
    return int(m.group(1)) if m else None


def _resolve(url: str, base: str | None) -> str:
    if not url:
        return url
    return urljoin(base, url) if (base and not url.startswith("http")) else url


def _fmt(item) -> str:
    if isinstance(item, str):
        return item
    return "\n".join(
        f"{k.replace('_', ' ').title()}: {v}"
        for k, v in item.items() if v
    )


async def run_query(
    html: str,
    intent: str,
    base_url: str | None = None,
    max_results: int = 100,
) -> dict:

    if not settings.groq_api_key:
        base = rule_based_query(html, intent)
        base.update(ai_powered=False, fallback=True, summary=None, pages_fetched=1)
        return base

    try:
        from app.services.fetcher import fetch_html, find_next_page_url

        # Build skeleton with base_url so all link hrefs are absolute
        skeleton = build_skeleton(html, base_url=base_url or "")
        plan = await ask_groq(skeleton, intent)
        log.info("AI plan: container=%r follow_url=%r", plan["container"], plan["follow_url"])

        container  = plan["container"]
        fields     = plan["fields"]
        follow_url = plan.get("follow_url")
        summary    = plan["summary"]

        working_html = html
        working_url  = base_url
        navigated    = False

        # Navigate to category/filter page if AI identified one
        if follow_url:
            resolved = _resolve(follow_url, base_url)
            log.info("Navigating to: %s", resolved)
            try:
                working_html, _ = await fetch_html(resolved)
                working_url = resolved
                navigated = True
                # Re-ask with new page + new base_url so links are correct
                plan2 = await ask_groq(build_skeleton(working_html, base_url=resolved), intent)
                log.info("Post-nav plan: container=%r", plan2["container"])
                if plan2["container"]:
                    container = plan2["container"]
                    fields    = plan2["fields"]
                    summary   = plan2["summary"] or summary
            except Exception as e:
                log.warning("Navigation failed (%s): %s", resolved, e)
                working_html = html
                working_url  = base_url
                navigated    = False

        if not container:
            base = rule_based_query(html, intent)
            base.update(ai_powered=False, fallback=True,
                        summary="Could not determine what to extract. Try rephrasing.", pages_fetched=1)
            return base

        requested = _parse_count(intent) or max_results
        rows = _extract_structured(working_html, container, fields, limit=requested)
        pages = 1

        log.info("Extracted %d rows with selector %r", len(rows), container)

        # Paginate if we need more
        if working_url and len(rows) < requested:
            cur_html, cur_url = working_html, working_url
            for _ in range(20):
                if len(rows) >= requested:
                    break
                nxt = find_next_page_url(cur_html, cur_url)
                if not nxt:
                    break
                try:
                    cur_html, _ = await fetch_html(nxt)
                    cur_url = nxt
                    pages += 1
                    rows += _extract_structured(cur_html, container, fields,
                                                limit=requested - len(rows))
                    log.info("Page %d → %d total rows", pages, len(rows))
                except Exception as e:
                    log.warning("Pagination failed: %s", e)
                    break

        rows = rows[:requested]

        if not rows:
            base = rule_based_query(html, intent)
            base.update(ai_powered=False, fallback=True,
                        summary=f"AI found selector '{container}' but it matched nothing on the page. Used rule-based fallback.",
                        pages_fetched=1)
            return base

        nav_note  = f" (navigated to {working_url})" if navigated else ""
        page_note = f" — {pages} pages scraped" if pages > 1 else ""

        return {
            "intent":        intent,
            "selector":      container,
            "extract_mode":  "structured",
            "count":         len(rows),
            "results":       [_fmt(r) for r in rows],
            "ai_powered":    True,
            "fallback":      False,
            "summary":       f"{summary}{nav_note}{page_note}",
            "pages_fetched": pages,
        }

    except Exception as exc:
        log.warning("AI query failed: %s", exc)
        base = rule_based_query(html, intent)
        base.update(ai_powered=False, fallback=True, summary=None, pages_fetched=1)
        return base
