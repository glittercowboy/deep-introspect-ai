"""
Insights API routes.
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.api.models.user import User
from app.api.models.insights import InsightListResponse, InsightResponse
from app.services.insights.insights_service import insights_service
from app.services.knowledge.knowledge_service import knowledge_service
from app.api.dependencies.auth import get_current_user
from app.db.supabase import supabase_client

router = APIRouter(prefix="/v1/insights", tags=["Insights"])

@router.get("", response_model=InsightListResponse)
async def list_insights(
    current_user: User = Depends(get_current_user),
    type: Optional[str] = Query(None, description="Filter by insight type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List insights for the current user.
    """
    # Get insights from database
    insights = await insights_service.get_user_insights(current_user.id)
    
    # Apply type filter if provided
    if type:
        insights = [insight for insight in insights if insight.get("type", "").lower() == type.lower()]
    
    # Calculate total
    total = len(insights)
    
    # Apply pagination
    paginated_insights = insights[offset:offset+limit]
    
    return {
        "insights": paginated_insights,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/{insight_id}", response_model=InsightResponse)
async def get_insight(
    insight_id: str = Path(..., title="The ID of the insight to get"),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific insight.
    """
    # Find the insight in the user's insights
    insights = await insights_service.get_user_insights(current_user.id)
    insight = next((i for i in insights if i["id"] == insight_id), None)
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    return insight

@router.get("/conversation/{conversation_id}")
async def get_insights_for_conversation(
    conversation_id: str = Path(..., title="The ID of the conversation to get insights for"),
    current_user: User = Depends(get_current_user)
):
    """
    Get insights for a specific conversation.
    """
    # Verify that the conversation exists and belongs to the user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Get insights for the conversation
    insights = await insights_service.get_user_insights(current_user.id)
    conversation_insights = [
        insight for insight in insights 
        if insight.get("conversation_id") == conversation_id
    ]
    
    return {
        "insights": conversation_insights,
        "conversation_id": conversation_id
    }

@router.post("/conversation/{conversation_id}/generate")
async def generate_insights_for_conversation(
    conversation_id: str = Path(..., title="The ID of the conversation to generate insights for"),
    current_user: User = Depends(get_current_user)
):
    """
    Generate insights for a specific conversation.
    """
    # Verify that the conversation exists and belongs to the user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Generate insights
    insights = await insights_service.generate_conversation_insights(
        user_id=current_user.id,
        conversation_id=conversation_id
    )
    
    return {
        "insights": insights,
        "count": len(insights),
        "conversation_id": conversation_id
    }

@router.get("/search")
async def search_insights(
    query: str = Query(..., min_length=2, description="Search query"),
    current_user: User = Depends(get_current_user)
):
    """
    Search for insights by content.
    """
    # Get all user insights
    insights = await insights_service.get_user_insights(current_user.id)
    
    # Simple search implementation
    query = query.lower()
    matching_insights = [
        insight for insight in insights
        if query in insight.get("content", "").lower() or query in insight.get("evidence", "").lower()
    ]
    
    return {
        "insights": matching_insights,
        "count": len(matching_insights),
        "query": query
    }

@router.get("/knowledge/search")
async def search_knowledge(
    query: str = Query(..., min_length=2, description="Search query"),
    current_user: User = Depends(get_current_user)
):
    """
    Search the knowledge graph.
    """
    results = await knowledge_service.search_knowledge(
        user_id=current_user.id,
        query=query
    )
    
    return {
        "results": results,
        "count": len(results),
        "query": query
    }