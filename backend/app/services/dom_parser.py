from bs4 import BeautifulSoup, Tag, NavigableString
from app.models.schemas import DomNode

# Tags that add no structural or visual value to a DOM viewer
SKIP_TAGS = {"script", "style", "noscript", "meta", "link"}

MAX_DEPTH = 40  # safety net against pathological nesting


def parse_html_to_tree(html: str) -> DomNode:
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("html") or soup
    return _build_node(root, depth=0)


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