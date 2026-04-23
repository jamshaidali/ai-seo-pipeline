from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QueryResponse(BaseModel):
    query_uuid: str
    query_text: str
    estimated_search_volume: Optional[int]
    competitive_difficulty: Optional[int]
    opportunity_score: Optional[float]
    domain_visible: Optional[bool]
    visibility_position: Optional[int]
    discovered_at: datetime

class QueryListResponse(BaseModel):
    queries: list[QueryResponse]
    total: int

class QueryFilterParams(BaseModel):
    min_score: Optional[float] = None
    status: Optional[str] = None  # 'scored', 'failed', etc.
    limit: Optional[int] = 50
    offset: Optional[int] = 0