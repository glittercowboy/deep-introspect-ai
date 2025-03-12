"""
Insights API models.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field


class InsightBase(BaseModel):
    """Base insight model."""
    type: str  # belief, value, trait, pattern, etc.
    content: str
    evidence: Optional[str] = None
    confidence: Optional[float] = 0.8
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class InsightCreate(InsightBase):
    """Insight creation model."""
    user_id: str
    conversation_id: Optional[str] = None


class InsightResponse(InsightBase):
    """Insight response model."""
    id: str
    user_id: str
    conversation_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class UserSummaryBase(BaseModel):
    """User summary base model."""
    summary: str
    categories: Dict[str, List[str]]


class UserSummaryResponse(UserSummaryBase):
    """User summary response model."""
    user_id: str
    generated_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class GraphNode(BaseModel):
    """Knowledge graph node model."""
    id: str
    label: str
    type: str
    size: Optional[int] = 10
    content: Optional[str] = None
    evidence: Optional[str] = None


class GraphLink(BaseModel):
    """Knowledge graph link model."""
    source: str
    target: str
    label: str
    type: Optional[str] = None


class KnowledgeGraphResponse(BaseModel):
    """Knowledge graph response model."""
    nodes: List[GraphNode]
    links: List[GraphLink]


class UserInsightsResponse(BaseModel):
    """User insights response model with graph and summary."""
    insights: List[InsightResponse]
    summary: UserSummaryResponse
    graph: KnowledgeGraphResponse


class InsightCategoryResponse(BaseModel):
    """Insight category with grouped insights."""
    category: str
    count: int
    insights: List[InsightResponse]


class InsightAnalysisResponse(BaseModel):
    """Insight analysis with trends and patterns."""
    total_count: int
    categories: Dict[str, int]
    recent_insights: List[InsightResponse]
    top_patterns: List[InsightResponse]
    trend_analysis: Dict[str, Any]


class ConversationInsightsRequest(BaseModel):
    """Request to generate insights from a conversation."""
    conversation_id: str


class ConversationInsightsResponse(BaseModel):
    """Response with generated insights from a conversation."""
    insights: List[InsightResponse]
    conversation_id: str
    analysis: Dict[str, Any]
