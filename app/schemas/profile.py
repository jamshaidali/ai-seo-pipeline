from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class ProfileCreateRequest(BaseModel):
    name: str = Field(..., description="Business name")
    domain: str = Field(..., description="Target domain name")
    industry: str = Field(..., description="Industry category")
    description: str = Field(..., description="Business description")
    competitors: List[str] = Field(..., description="List of competitor domains")

class ProfileResponse(BaseModel):
    profile_uuid: str
    name: str
    domain: str
    industry: str
    description: str
    competitors: List[str]
    status: str
    created_at: datetime
    updated_at: datetime
