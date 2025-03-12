"""
Insights API routes.
"""
import logging
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies.auth import get_current_user
from app.api.models.insights import (
    InsightResponse,
    UserInsightsResponse,
    InsightCategoryResponse,
    InsightAnalysisResponse,
    ConversationInsightsRequest,
    ConversationInsightsResponse,
    KnowledgeGraphResponse,
    UserSummaryResponse
)
from app.services.insights.insights_service import insights_service
from app.services.knowledge.knowledge_service import knowledge_service
from app.services.chat.chat_service import chat_service

router = APIRouter(prefix="/insights", tags=["Insights"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[InsightResponse])
async def get_user_insights(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
    category: str = None
) -> Any:
    """
    Get insights for the current user.
    
    Args:
        current_user: Current authenticated user
        limit: Maximum number of insights to return
        offset: Offset for pagination
        category: Filter by insight category
        
    Returns:
        List of insights
    """
    # Get insights
    insights = await insights_service.get_user_insights(current_user["id"])
    
    # Filter by category if specified
    if category:
        insights = [i for i in insights if i.get("type", "").lower() == category.lower()]
    
    # Apply pagination
    paginated_insights = insights[offset:offset + limit]
    
    return paginated_insights


@router.get("/summary", response_model=UserSummaryResponse)
async def get_user_summary(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Get a summary of the user based on their insights.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User summary
    """
    summary = await insights_service.generate_user_summary(current_user["id"])
    return summary


@router.get("/graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    current_user: dict = Depends(get_current_user),
    depth: int = 2
) -> Any:
    """
    Get the knowledge graph for the user.
    
    Args:
        current_user: Current authenticated user
        depth: Graph traversal depth
        
    Returns:
        Knowledge graph with nodes and links
    """
    graph = await insights_service.generate_insight_graph(current_user["id"])
    return graph


@router.get("/categories", response_model=List[InsightCategoryResponse])
async def get_insight_categories(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Get insights grouped by category.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Insights grouped by category
    """
    # Get all insights
    insights = await insights_service.get_user_insights(current_user["id"])
    
    # Group by category
    categories = {}
    for insight in insights:
        category = insight.get("type", "unknown").lower()
        if category not in categories:
            categories[category] = {
                "category": category,
                "count": 0,
                "insights": []
            }
        
        categories[category]["count"] += 1
        categories[category]["insights"].append(insight)
    
    # Convert to list
    category_list = list(categories.values())
    
    # Sort by count (most common first)
    category_list.sort(key=lambda x: x["count"], reverse=True)
    
    return category_list


@router.get("/analysis", response_model=InsightAnalysisResponse)
async def get_insight_analysis(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Get analysis of user insights with trends and patterns.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Insight analysis with trends and patterns
    """
    # Get all insights
    insights = await insights_service.get_user_insights(current_user["id"])
    
    # Count by category
    categories = {}
    for insight in insights:
        category = insight.get("type", "unknown").lower()
        if category not in categories:
            categories[category] = 0
        
        categories[category] += 1
    
    # Get recent insights (top 10)
    recent_insights = sorted(
        insights, 
        key=lambda x: x.get("created_at", ""), 
        reverse=True
    )[:10]
    
    # Get top patterns (if any)
    patterns = [i for i in insights if i.get("type", "").lower() == "pattern"]
    patterns.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    top_patterns = patterns[:5]
    
    # Generate trend analysis
    # In a real implementation, this would be more sophisticated
    trend_analysis = {
        "most_common_category": max(categories.items(), key=lambda x: x[1])[0] if categories else None,
        "insight_count_over_time": {
            "last_week": len([i for i in insights if is_within_last_days(i.get("created_at", ""), 7)]),
            "last_month": len([i for i in insights if is_within_last_days(i.get("created_at", ""), 30)]),
            "total": len(insights)
        },
        "category_distribution": categories
    }
    
    return InsightAnalysisResponse(
        total_count=len(insights),
        categories=categories,
        recent_insights=recent_insights,
        top_patterns=top_patterns,
        trend_analysis=trend_analysis
    )


@router.post("/conversations", response_model=ConversationInsightsResponse)
async def generate_conversation_insights(
    request: ConversationInsightsRequest,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Generate insights from a conversation.
    
    Args:
        request: Request with conversation ID
        current_user: Current authenticated user
        
    Returns:
        Generated insights
    """
    # Get conversation to verify ownership
    conversation = await chat_service.get_conversation(request.conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    # Check if user owns the conversation
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )
    
    # Generate insights
    insights = await insights_service.generate_conversation_insights(
        current_user["id"],
        request.conversation_id
    )
    
    # Simple analysis
    analysis = {
        "total_count": len(insights),
        "categories": {}
    }
    
    # Count by category
    for insight in insights:
        category = insight.get("type", "unknown").lower()
        if category not in analysis["categories"]:
            analysis["categories"][category] = 0
        
        analysis["categories"][category] += 1
    
    return ConversationInsightsResponse(
        insights=insights,
        conversation_id=request.conversation_id,
        analysis=analysis
    )


@router.get("/search", response_model=List[InsightResponse])
async def search_insights(
    query: str,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Search for insights.
    
    Args:
        query: Search query
        current_user: Current authenticated user
        
    Returns:
        List of matching insights
    """
    # In a real implementation, you would use a proper search index
    # For this example, we'll do a simple string search
    insights = await insights_service.get_user_insights(current_user["id"])
    
    # Filter insights that match the query
    matching_insights = []
    for insight in insights:
        content = insight.get("content", "").lower()
        evidence = insight.get("evidence", "").lower()
        category = insight.get("type", "").lower()
        
        if (query.lower() in content or 
            query.lower() in evidence or 
            query.lower() in category):
            matching_insights.append(insight)
    
    return matching_insights


def is_within_last_days(date_str: str, days: int) -> bool:
    """
    Check if a date string is within the last N days.
    
    Args:
        date_str: ISO format date string
        days: Number of days
        
    Returns:
        True if the date is within the last N days
    """
    from datetime import datetime, timedelta
    try:
        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.now()
        return (now - date) <= timedelta(days=days)
    except Exception:
        return False
