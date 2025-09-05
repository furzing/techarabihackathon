from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class DesignChange(BaseModel):
    category: str  # layout, color, typography, spacing, content, etc.
    description_en: str  # English description
    description_ar: str  # Arabic description
    severity: str  # minor, moderate, major
    location: Optional[str] = None  # where in the design
    action_required: Optional[str] = None  # what designer needs to do

class AnalysisData(BaseModel):
    similarity_score: float  # 0-100 percentage
    summary_en: str  # English summary
    summary_ar: str  # Arabic summary
    changes_detected: List[DesignChange]
    designer_notes_en: List[str]  # Direct instructions in English
    designer_notes_ar: List[str]  # Direct instructions in Arabic
    next_steps_en: List[str]  # Next actions in English
    next_steps_ar: List[str]  # Next actions in Arabic
    analysis_id: Optional[str] = None  # Database ID if saved

class AnalysisResponse(BaseModel):
    success: bool
    timestamp: datetime
    data: AnalysisData
    error: Optional[str] = None

class VersionComparisonRequest(BaseModel):
    version1_url: Optional[str] = None  # URL to first image
    version2_url: Optional[str] = None  # URL to second image
    context: Optional[str] = None  # Additional context about the design

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