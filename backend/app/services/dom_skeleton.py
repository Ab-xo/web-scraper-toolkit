"""
DOM skeleton builder.
Sends the LLM a rich context: structure, visible text, and ALL links with their text.
This lets the AI find the correct navigation URL from actual page data.
"""
from __future__ import annotations
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag, Comment, NavigableString

STRIP_TAGS = {"script", "style", "noscript", "svg", "path"}
MAX_CHARS = 14000


def build_skeleton(html: str, base_url: str = "", max_chars: int = MAX_CHARS) -> str:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup.find_all(STRIP_TAGS):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # 1. DOM structure (tags + class/id only)
    lines: list[str] = []
    _walk(soup.find("body") or soup, lines, depth=0)
    structure = "\n".join(lines)

    # 2. Visible text (first 2000 chars)
    body = soup.find("body")
    visible = ""
    if body:
        raw = body.get_text(separator=" ", strip=True)
        visible = re.sub(r"\s+", " ", raw)[:2000]

    # 3. All links with text + href — critical for category navigation
    links_section = _extract_links(soup, base_url)

    combined = (
        f"=== DOM STRUCTURE ===\n{structure}\n\n"
        f"=== VISIBLE TEXT ===\n{visible}\n\n"
        f"=== ALL LINKS (text → href) ===\n{links_section}"
    )

    if len(combined) > max_chars:
        combined = combined[:max_chars].rsplit("\n", 1)[0] + "\n..."

    return combined


def _extract_links(soup, base_url: str) -> str:
    seen: set[str] = set()
    parts: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("javascript"):
            continue
        if base_url and not href.startswith("http"):
            href = urljoin(base_url, href)
        text = a.get_text(strip=True)
        if href not in seen and text:
            seen.add(href)
            parts.append(f"  {text!r} → {href}")
        if len(parts) >= 200:
            break
    return "\n".join(parts) if parts else "  (no links found)"


def _walk(element, lines: list[str], depth: int) -> None:
    if depth > 25 or not isinstance(element, Tag):
        return
    indent = "  " * depth
    attrs = _safe_attrs(element)
    attr_str = f" {attrs}".rstrip() if attrs else ""
    lines.append(f"{indent}<{element.name}{attr_str}>")
    for child in element.children:
        if isinstance(child, Tag):
            _walk(child, lines, depth + 1)
        elif isinstance(child, NavigableString):
            text = child.strip()
            if text and len(text) < 120:
                lines.append(f"{indent}  \"{text}\"")


def _safe_attrs(tag: Tag) -> str:
    parts: list[str] = []
    raw = dict(tag.attrs)
    if "id" in raw:
        val = raw["id"]
        parts.append(f'id="{" ".join(val) if isinstance(val, list) else val}"')
    if "class" in raw:
        val = raw["class"]
        parts.append(f'class="{" ".join(val) if isinstance(val, list) else val}"')
    return " ".join(parts)
