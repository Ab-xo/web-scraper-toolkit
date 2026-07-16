from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional


class ScrapeRequest(BaseModel):
    url: HttpUrl
    use_playwright: bool = False


class DomNode(BaseModel):
    tag: str
    attrs: dict[str, str] = {}
    text: Optional[str] = None
    children: list["DomNode"] = []


DomNode.model_rebuild()


class LinkItem(BaseModel):
    href: str
    text: str


class ScrapeResponse(BaseModel):
    url: str
    method_used: str
    html_length: int
    dom_tree: DomNode
    title: Optional[str] = None
    text: Optional[str] = None
    links: list[LinkItem] = []
    html: Optional[str] = None


class QueryRequest(BaseModel):
    html: str
    intent: str
    base_url: Optional[str] = None   # original page URL, used for pagination
    max_results: int = 100            # max items to return across all pages

    @field_validator("intent")
    @classmethod
    def intent_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("intent must not be empty")
        if len(v) > 300:
            raise ValueError("intent too long (max 300 chars)")
        return v

    @field_validator("html")
    @classmethod
    def html_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("html must not be empty")
        if len(v) > 5_000_000:  # 5MB cap
            raise ValueError("html too large (max 5 MB)")
        return v

    @field_validator("max_results")
    @classmethod
    def max_results_range(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_results must be at least 1")
        if v > 500:
            raise ValueError("max_results cannot exceed 500")
        return v


class QueryResponse(BaseModel):
    intent: str
    selector: str
    extract_mode: str
    count: int
    results: list[str]
    ai_powered: bool = False
    fallback: bool = False
    summary: Optional[str] = None
    pages_fetched: int = 1

