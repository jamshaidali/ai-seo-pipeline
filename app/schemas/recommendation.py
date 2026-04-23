from pydantic import BaseModel
from typing import List
from datetime import datetime

class RecommendationResponse(BaseModel):
    recommendation_uuid: str
    target_query_uuid: str
    content_type: str
    title: str
    rationale: str
    target_keywords: List[str]
    priority: str
    created_at: datetime

class RecommendationListResponse(BaseModel):
    recommendations: List[RecommendationResponse]
    total: int