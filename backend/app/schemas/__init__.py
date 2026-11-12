from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime


# Niche Schemas
class NicheBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None


class NicheCreate(NicheBase):
    slug: Optional[str] = None


class NicheResponse(NicheBase):
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime
    total_analyses: int = 0

    model_config = ConfigDict(from_attributes=True)


# Analysis Item Schemas
class PainPointSchema(BaseModel):
    category: str
    title: str
    description: Optional[str] = None
    frequency_percentage: float
    severity: str
    sample_comments: Optional[List[str]] = []
    financial_impact: Optional[str] = None
    competitors_affected: Optional[List[str]] = []

    model_config = ConfigDict(from_attributes=True)


class RecommendedFeatureSchema(BaseModel):
    title: str
    rationale: str
    reach: int
    impact: int
    confidence: int
    effort: int
    rice_score: float
    user_story: Optional[str] = None
    acceptance_criteria: Optional[List[str]] = []
    effort_breakdown: Optional[str] = None
    technical_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HookCopySchema(BaseModel):
    placement: str
    hook_text: str
    intent: str
    variations: Optional[List[str]] = []
    page_position: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FaqItemSchema(BaseModel):
    question: str
    answer_suggestion: str
    friction_level: int
    placement_tip: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Analysis Request / Response Schemas
class AnalysisCreateRequest(BaseModel):
    niche_id: UUID
    keyword: str = Field(..., min_length=2, max_length=255)
    sources: List[str] = Field(default_factory=lambda: ["reddit", "tiktok", "instagram", "youtube"])
    force_refresh: bool = False
    mode: Optional[str] = "mock"  # "mock" ou "live"


class AnalysisResponse(BaseModel):
    id: UUID
    niche_id: UUID
    keyword: str
    mode: str
    sources_selected: List[str]
    sample_size: int
    created_at: datetime
    is_cached: bool = False
    
    pain_points: List[PainPointSchema] = []
    recommended_features: List[RecommendedFeatureSchema] = []
    hook_copies: List[HookCopySchema] = []
    faq_items: List[FaqItemSchema] = []

    model_config = ConfigDict(from_attributes=True)


class DossierResponse(BaseModel):
    analysis_id: UUID
    keyword: str
    markdown_content: str
    metadata_info: Dict[str, Any]
    created_at: datetime
