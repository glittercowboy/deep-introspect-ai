"""
Insights API routes.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.insights.insights_service import insights_service
from app.services.knowledge.knowledge_service import knowledge_service
from app.services.chat.chat_service import chat_service
from app.api.routes.auth import get_current_user
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/insights", tags=["Insights"])

# Models
class InsightResponse(BaseModel):
    """Insight response model"""
    id: str
    user_id: str
    conversation_id: str
    type: str
    content: str
    evidence: str
    created_at: str
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InsightListResponse(BaseModel):
    """Insight list response model"""
    insights: List[InsightResponse]
    total: int

class UserSummaryResponse(BaseModel):
    """User summary response model"""
    summary: str
    categories: Dict[str, Any]

class InsightGraphResponse(BaseModel):
    """Insight graph response model"""
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]

class UserInsightsResponse(BaseModel):
    """User insights response model"""
    insights: List[InsightResponse]
    summary: UserSummaryResponse
    graph: InsightGraphResponse

@router.get("/me", response_model=UserInsightsResponse)
async def get_my_insights(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user's insights.
    
    Args:
        current_user: Current user (from token)
        
    Returns:
        User insights, summary, and graph
    """
    insights_data = await chat_service.get_user_insights(current_user["id"])
    return insights_data

@router.get("/me/list", response_model=InsightListResponse)
async def list_my_insights(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List current user's insights.
    
    Args:
        current_user: Current user (from token)
        
    Returns:
        List of insights
    """
    insights = await insights_service.get_user_insights(current_user["id"])
    
    return {
        "insights": insights,
        "total": len(insights)
    }

@router.get("/me/summary", response_model=UserSummaryResponse)
async def get_my_summary(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user's summary.
    
    Args:
        current_user: Current user (from token)
        
    Returns:
        User summary
    """
    summary = await insights_service.generate_user_summary(current_user["id"])
    return summary

@router.get("/me/graph", response_model=InsightGraphResponse)
async def get_my_graph(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user's insight graph.
    
    Args:
        current_user: Current user (from token)
        
    Returns:
        Insight graph
    """
    graph = await insights_service.generate_insight_graph(current_user["id"])
    return graph

@router.get("/me/knowledge", response_model=Dict[str, Any])
async def get_my_knowledge_graph(
    current_user: Dict[str, Any] = Depends(get_current_user),
    depth: int = 2
) -> Dict[str, Any]:
    """
    Get current user's knowledge graph.
    
    Args:
        current_user: Current user (from token)
        depth: Depth of relationships to traverse
        
    Returns:
        Knowledge graph
    """
    graph = await knowledge_service.get_user_knowledge_graph(current_user["id"], depth)
    return graph

@router.get("/conversations/{conversation_id}", response_model=InsightListResponse)
async def get_conversation_insights(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get insights for a specific conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current user (from token)
        
    Returns:
        List of insights
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and belongs to user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this conversation"
        )
    
    # Get insights for conversation
    insights = await supabase_client.get_insights_by_conversation(conversation_id)
    
    return {
        "insights": insights,
        "total": len(insights)
    }

@router.post("/conversations/{conversation_id}/generate", response_model=InsightListResponse)
async def generate_conversation_insights(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate insights for a specific conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current user (from token)
        
    Returns:
        List of generated insights
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and belongs to user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this conversation"
        )
    
    # Generate insights
    insights = await insights_service.generate_conversation_insights(
        user_id=current_user["id"],
        conversation_id=conversation_id
    )
    
    return {
        "insights": insights,
        "total": len(insights)
    }

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_knowledge(
    query: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Search the knowledge graph.
    
    Args:
        query: Search query
        current_user: Current user (from token)
        
    Returns:
        List of matching nodes
    """
    results = await knowledge_service.search_knowledge(current_user["id"], query)
    return results