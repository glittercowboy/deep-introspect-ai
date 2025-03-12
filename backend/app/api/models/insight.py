"""
API models for insights.
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class InsightBase(BaseModel):
    """Base schema for an insight."""
    type: str = Field(..., description="The type of insight (belief, value, trait, etc.)")
    content: str = Field(..., description="The content of the insight")
    evidence: str = Field(..., description="Evidence for this insight from the conversation")


class InsightResponse(InsightBase):
    """Schema for returning an insight."""
    id: str = Field(..., description="The insight ID")
    user_id: str = Field(..., description="The user ID")
    conversation_id: Optional[str] = Field(None, description="The conversation ID if the insight is tied to a specific conversation")
    created_at: datetime = Field(..., description="The timestamp when the insight was created")
    confidence: float = Field(..., description="Confidence level of the insight (0-1)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class InsightList(BaseModel):
    """Schema for returning a list of insights."""
    insights: List[InsightResponse] = Field(..., description="List of insights")


class UserSummarySection(BaseModel):
    """Schema for a section in the user summary."""
    content: str = Field(..., description="The content of the section")
    evidence: List[str] = Field(default_factory=list, description="Evidence for this section")


class UserSummary(BaseModel):
    """Schema for a user summary based on insights."""
    summary: str = Field(..., description="Overall summary of the user")
    categories: Dict[str, UserSummarySection] = Field(..., description="Different categories of the summary")


class InsightGraphNode(BaseModel):
    """Schema for a node in the insight graph."""
    id: str = Field(..., description="The node ID")
    label: str = Field(..., description="The label of the node")
    type: str = Field(..., description="The type of node")
    size: int = Field(..., description="The size of the node for visualization")
    content: Optional[str] = Field(None, description="The full content of the node")
    evidence: Optional[str] = Field(None, description="Evidence for this node")


class InsightGraphLink(BaseModel):
    """Schema for a link in the insight graph."""
    source: str = Field(..., description="The source node ID")
    target: str = Field(..., description="The target node ID")
    label: str = Field(..., description="The label of the link")
    type: str = Field(..., description="The type of link")


class InsightGraph(BaseModel):
    """Schema for an insight graph."""
    nodes: List[InsightGraphNode] = Field(..., description="List of graph nodes")
    links: List[InsightGraphLink] = Field(..., description="List of graph links")


class UserInsights(BaseModel):
    """Schema for all user insights and visualizations."""
    insights: List[InsightResponse] = Field(..., description="Raw insights about the user")
    summary: UserSummary = Field(..., description="Summary of the user based on insights")
    graph: InsightGraph = Field(..., description="Graph visualization of insights")
