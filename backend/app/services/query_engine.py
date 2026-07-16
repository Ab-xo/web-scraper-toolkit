"""
Natural-language query engine.
Token-scoring approach: split intent into words, score every rule by keyword
overlap, pick the best match. Far more forgiving than full-string regex.
"""

from __future__ import annotations
import re
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Rules: (keywords, css_selector, extract_mode)
# keywords  – ANY of these words in the intent trigger this rule (higher
#             overlap = higher score, so broad phrases still win the right rule)
# ---------------------------------------------------------------------------

RULES: list[tuple[list[str], str, str]] = [
    # ── headings ──────────────────────────────────────────────────────────────
    (["heading", "headings", "header", "headers", "title", "titles",
      "h1", "h2", "h3", "h4", "h5", "h6"],
     "h1,h2,h3,h4,h5,h6", "text"),

    # ── paragraphs ────────────────────────────────────────────────────────────
    (["paragraph", "paragraphs", "body", "text", "content", "article", "articles"],
     "p", "text"),

    # ── links / URLs ──────────────────────────────────────────────────────────
    (["link", "links", "anchor", "anchors", "href", "url", "urls", "hyperlink"],
     "a[href]", "href"),

    # ── images ────────────────────────────────────────────────────────────────
    (["image", "images", "img", "photo", "photos", "picture", "pictures",
      "thumbnail", "thumbnails", "src"],
     "img", "src"),

    # ── navigation ────────────────────────────────────────────────────────────
    (["nav", "navigation", "menu", "navbar", "topbar", "sidebar"],
     "nav a, header a, [role=navigation] a", "text"),

    # ── list items ────────────────────────────────────────────────────────────
    (["list", "lists", "item", "items", "bullet", "bullets", "li"],
     "ul li, ol li", "text"),

    # ── prices ────────────────────────────────────────────────────────────────
    (["price", "prices", "cost", "costs", "fee", "fees", "amount",
      "dollar", "euro", "pound"],
     "[class*=price],[class*=cost],[class*=amount],[class*=fee]", "text"),

    # ── products ──────────────────────────────────────────────────────────────
    (["product", "products", "item", "items", "goods", "merchandise"],
     "[class*=product] h1,[class*=product] h2,[class*=product-title],[class*=item-title]", "text"),

    # ── quotes / testimonials ─────────────────────────────────────────────────
    (["quote", "quotes", "blockquote", "testimonial", "testimonials", "saying"],
     "blockquote, q, [class*=quote], [class*=testimonial]", "text"),

    # ── authors ───────────────────────────────────────────────────────────────
    (["author", "authors", "writer", "writers", "byline", "posted", "by"],
     "[class*=author],[class*=byline],[rel=author],[class*=writer]", "text"),

    # ── dates / times ─────────────────────────────────────────────────────────
    (["date", "dates", "time", "times", "published", "posted", "when", "timestamp"],
     "time,[class*=date],[class*=time],[datetime],[class*=published],[class*=timestamp]", "text"),

    # ── tables ────────────────────────────────────────────────────────────────
    (["table", "tables", "row", "rows", "cell", "cells", "column", "columns",
      "td", "th", "grid"],
     "table td, table th", "text"),

    # ── forms / inputs ────────────────────────────────────────────────────────
    (["form", "forms", "input", "inputs", "field", "fields", "label", "labels",
      "placeholder", "textbox"],
     "label, input[placeholder], textarea[placeholder]", "text"),

    # ── emails ────────────────────────────────────────────────────────────────
    (["email", "emails", "e-mail", "mail", "contact", "mailto"],
     "a[href^=mailto]", "href"),

    # ── phone numbers ─────────────────────────────────────────────────────────
    (["phone", "phones", "telephone", "tel", "mobile", "number", "call"],
     "a[href^=tel],[class*=phone],[class*=tel],[class*=mobile]", "text"),

    # ── code ──────────────────────────────────────────────────────────────────
    (["code", "snippet", "snippets", "pre", "syntax", "script", "example"],
     "pre, code", "text"),

    # ── meta / description ────────────────────────────────────────────────────
    (["meta", "description", "summary", "seo", "og", "opengraph"],
     "meta[name=description],meta[property^=og]", "attr:content"),

    # ── buttons ───────────────────────────────────────────────────────────────
    (["button", "buttons", "cta", "action", "call"],
     "button, [role=button], input[type=submit], input[type=button]", "text"),

    # ── videos ────────────────────────────────────────────────────────────────
    (["video", "videos", "embed", "youtube", "iframe", "media"],
     "video, iframe[src*=youtube], iframe[src*=vimeo], [class*=video]", "src"),
]


def _tokenize(text: str) -> set[str]:
    """Lowercase, split on non-alpha chars, drop stopwords."""
    stopwords = {"find", "get", "all", "every", "the", "a", "an", "of",
                 "in", "on", "from", "and", "or", "show", "give", "list",
                 "extract", "fetch", "return", "me", "us", "please", "i",
                 "want", "need", "look", "for", "with", "that", "this"}
    tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
    return tokens - stopwords


def _intent_to_selector(intent: str) -> tuple[str, str]:
    tokens = _tokenize(intent)
    best_score = 0
    best_selector = "p"
    best_mode = "text"

    for keywords, selector, mode in RULES:
        score = len(tokens & set(keywords))
        if score > best_score:
            best_score = score
            best_selector = selector
            best_mode = mode

    # score == 0 means nothing matched at all — try a loose class/tag search
    if best_score == 0 and tokens:
        keyword = next(iter(tokens))
        best_selector = f"{keyword},[class*={keyword}],[id*={keyword}]"
        best_mode = "text"

    return best_selector, best_mode


def _extract(tag, mode: str) -> str | None:
    if mode == "text":
        t = tag.get_text(separator=" ", strip=True)
        return t if t else None
    if mode == "href":
        href = tag.get("href", "").strip()
        return href if href else None
    if mode == "src":
        return tag.get("src") or tag.get("data-src") or tag.get("data-lazy-src") or None
    if mode.startswith("attr:"):
        attr = mode.split(":", 1)[1]
        return tag.get(attr) or None
    return None


def run_query(html: str, intent: str) -> dict:
    selector, mode = _intent_to_selector(intent)
    soup = BeautifulSoup(html, "lxml")

    seen: set[str] = set()
    results: list[str] = []

    for tag in soup.select(selector):
        value = _extract(tag, mode)
        if value and value not in seen:
            seen.add(value)
            results.append(value)
        if len(results) >= 100:
            break

    return {
        "intent": intent,
        "selector": selector,
        "extract_mode": mode,
        "count": len(results),
        "results": results,
    }
