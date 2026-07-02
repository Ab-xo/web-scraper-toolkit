from pydantic import BaseModel, HttpUrl
from typing import Optional


class ScrapeRequest(BaseModel):
    url: HttpUrl
class DomNode(BaseModel):
    tag:str
    attrs: dict[str,str] ={}
    text : Optional[str] = None
    children: list["DomNode"] = []
DomNode.model_rebuild()
class ScrapeResponse(BaseModel):
    url: str
    method_used: str
    html_length: int
    dom_tree: DomNode

