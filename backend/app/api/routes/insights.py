"""
Insights routes for the API.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from app.services.insights.insights_service import insights_service
from app.services.knowledge.knowledge_service import knowledge_service
from app.services.chat.chat_service import chat_service
from app.core.exceptions import NotFoundError, AuthorizationError
from app.api.routes.users import get_current_user

router = APIRouter(prefix="/insights", tags=["Insights"])

# Models
class InsightResponse(BaseModel):
    """Insight response model."""
    id: str
    user_id: str
    conversation_id: Optional[str] = None
    type: str
    content: str
    evidence: str
    created_at: str
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UserSummaryResponse(BaseModel):
    """User summary response model."""
    summary: str
    categories: Dict[str, Any] = Field(default_factory=dict)

class GraphData(BaseModel):
    """Graph data model."""
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    links: List[Dict[str, Any]] = Field(default_factory=list)

class UserInsightsResponse(BaseModel):
    """User insights response model."""
    insights: List[InsightResponse] = Field(default_factory=list)
    summary: UserSummaryResponse
    graph: GraphData

@router.get("", response_model=List[InsightResponse])
async def list_insights(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    List all insights for the current user.
    """
    from app.db.supabase import supabase_client
    
    insights = await supabase_client.get_insights(current_user["id"])
    return insights

@router.get("/summary", response_model=UserSummaryResponse)
async def get_user_summary(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Get a summary of user insights.
    """
    # Generate user summary
    summary = await insights_service.generate_user_summary(current_user["id"])
    return summary

@router.get("/graph", response_model=GraphData)
async def get_insights_graph(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Get a graph visualization of user insights.
    """
    # Generate graph data
    graph = await insights_service.generate_insight_graph(current_user["id"])
    return graph

@router.get("/knowledge", response_model=Dict[str, Any])
async def get_knowledge_graph(
    current_user: Dict[str, Any] = Depends(get_current_user),
    depth: int = 2
) -> Any:
    """
    Get the user's knowledge graph.
    """
    # Get knowledge graph data
    graph = await knowledge_service.get_user_knowledge_graph(
        user_id=current_user["id"],
        depth=depth
    )
    return graph

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_knowledge(
    query: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Search the knowledge graph.
    """
    # Search knowledge graph
    results = await knowledge_service.search_knowledge(
        user_id=current_user["id"],
        query=query
    )
    return results

@router.get("/conversation/{conversation_id}", response_model=List[InsightResponse])
async def get_conversation_insights(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Get insights for a specific conversation.
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and user has access
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise AuthorizationError("Not authorized to access this conversation")
    
    # Get insights for the conversation
    insights = await supabase_client.get_insights_by_conversation(conversation_id)
    return insights

@router.post("/conversation/{conversation_id}", response_model=List[InsightResponse])
async def generate_conversation_insights(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Generate new insights for a conversation.
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and user has access
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise AuthorizationError("Not authorized to access this conversation")
    
    # Generate insights
    insights = await insights_service.generate_conversation_insights(
        user_id=current_user["id"],
        conversation_id=conversation_id
    )
    
    return insights

@router.get("/all", response_model=UserInsightsResponse)
async def get_all_user_insights(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Get all insights, summary, and graph for the user.
    """
    # Get complete user insights
    user_insights = await chat_service.get_user_insights(current_user["id"])
    return user_insights