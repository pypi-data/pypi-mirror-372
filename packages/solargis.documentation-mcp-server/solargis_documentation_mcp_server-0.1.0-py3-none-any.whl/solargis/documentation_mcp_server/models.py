from pydantic import BaseModel


class SearchResult(BaseModel):
    """Search result from Solargis documentation search."""
    rank_order: int
    url: str
    title: str
    breadcrumb: str
