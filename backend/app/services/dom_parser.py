from bs4 import BeautifulSoup, Tag, NavigableString
from app.models.schemas import DomNode, LinkItem

# Tags that add no structural or visual value to a DOM viewer
SKIP_TAGS = {"script", "style", "noscript", "meta", "link"}

MAX_DEPTH = 40  # safety net against pathological nesting


def parse_html_to_tree(html: str) -> DomNode:
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("html") or soup
    return _build_node(root, depth=0)


def extract_title(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    tag = soup.find("title")
    return tag.get_text(strip=True) if tag else None


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def extract_links(html: str, base_url: str = "") -> list[LinkItem]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#"):
            continue
        if href.startswith("/") and base_url:
            from urllib.parse import urljoin
            href = urljoin(base_url, href)
        if href not in seen:
            seen.add(href)
            links.append(LinkItem(href=href, text=a.get_text(strip=True) or href))
    return links


def _build_node(element: Tag, depth: int) -> DomNode:
    children: list[DomNode] = []
    direct_text: list[str] = []

    if depth < MAX_DEPTH:
        for child in element.children:
            if isinstance(child, NavigableString):
                stripped = child.strip()
                if stripped:
                    direct_text.append(stripped)
            elif isinstance(child, Tag):
                if child.name in SKIP_TAGS:
                    continue
                children.append(_build_node(child, depth + 1))

    return DomNode(
        tag=element.name or "unknown",
        attrs={k: str(v) for k, v in element.attrs.items()},
        text=" ".join(direct_text) if direct_text else None,
        children=children,
    )