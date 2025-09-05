from pydantic import BaseModel
from typing import Optional
from datetime import date

class BusinessInfo(BaseModel):
    business_name: str
    business_type: str
    target_audience: str
    location: str
    unique_selling_points: Optional[str] = None

class StrategyRequest(BaseModel):
    business_info: BusinessInfo

class MarketingPlanRequest(BaseModel):
    strategy: str
    duration: Optional[str] = "1 month"

class ContentSuggestionRequest(BaseModel):
    topic: str
    content_type: Optional[str] = "all"
    target_platform: Optional[str] = "Instagram"

class PostCreationRequest(BaseModel):
    idea: str
    platform: Optional[str] = "Instagram"
    tone: Optional[str] = "engaging"

class PostScheduleRequest(BaseModel):
    post_content: str
    scheduled_date: date

class PostModerationRequest(BaseModel):
    post_content: str

class APIResponse(BaseModel):
    success: bool
    data: Optional[str] = None
    message: Optional[str] = None
