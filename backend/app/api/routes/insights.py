"""
Insights API routes.
"""
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from app.services.chat.chat_service import chat_service
from app.services.insights.insights_service import insights_service
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/insights", tags=["insights"])


class InsightResponse(BaseModel):
    """Insight response model."""
    id: str = Field(..., description="Insight ID")
    user_id: str = Field(..., description="User ID")
    conversation_id: str = Field(..., description="Conversation ID")
    type: str = Field(..., description="Insight type (belief, value, pattern, etc.)")
    content: str = Field(..., description="Insight content")
    evidence: str = Field(..., description="Evidence from conversation")
    created_at: str = Field(..., description="Creation timestamp")
    confidence: float = Field(..., description="Confidence score (0-1)")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174002",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174001",
                "type": "belief",
                "content": "The user believes they are not qualified for senior roles.",
                "evidence": "I don't think I have what it takes to be a senior developer yet.",
                "created_at": "2025-01-01T00:00:00Z",
                "confidence": 0.8
            }
        }


class SummaryResponse(BaseModel):
    """User summary response model."""
    summary: str = Field(..., description="Overall summary")
    categories: Dict[str, Any] = Field(..., description="Categorized summaries")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "summary": "Jane is a reflective software developer focused on growth.",
                "categories": {
                    "key_traits": ["Analytical", "Growth-oriented"],
                    "values_beliefs": ["Values work-life balance", "Believes in continuous learning"],
                    "goals": ["Become a senior developer", "Improve communication skills"],
                    "challenges": ["Imposter syndrome", "Work-related anxiety"],
                    "patterns": ["Self-critical thinking", "Seeks validation from others"]
                }
            }
        }


class GraphResponse(BaseModel):
    """Graph visualization response model."""
    nodes: List[Dict[str, Any]] = Field(..., description="Graph nodes")
    links: List[Dict[str, Any]] = Field(..., description="Graph links")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "nodes": [
                    {"id": "user-123", "label": "User", "type": "user", "size": 20},
                    {"id": "insight-1", "label": "Values work-life balance", "type": "value", "size": 10}
                ],
                "links": [
                    {"source": "user-123", "target": "insight-1", "label": "has_value", "type": "value"}
                ]
            }
        }


class UserInsightsResponse(BaseModel):
    """User insights response model."""
    insights: List[InsightResponse] = Field(..., description="List of insights")
    summary: SummaryResponse = Field(..., description="User summary")
    graph: GraphResponse = Field(..., description="Graph visualization data")


@router.get("/user", response_model=UserInsightsResponse)
async def get_user_insights(
    user_id: str = "test-user"  # TODO: Get from auth
) -> Dict[str, Any]:
    """
    Get all insights for a user.
    """
    try:
        insights_data = await chat_service.get_user_insights(user_id)
        return insights_data
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting user insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user insights"
        )


@router.get("/user/summary", response_model=SummaryResponse)
async def get_user_summary(
    user_id: str = "test-user"  # TODO: Get from auth
) -> Dict[str, Any]:
    """
    Get a summary of a user.
    """
    try:
        summary = await insights_service.generate_user_summary(user_id)
        return summary
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting user summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user summary"
        )


@router.get("/user/graph", response_model=GraphResponse)
async def get_user_graph(
    user_id: str = "test-user"  # TODO: Get from auth
) -> Dict[str, Any]:
    """
    Get a graph visualization of a user's insights.
    """
    try:
        graph = await insights_service.generate_insight_graph(user_id)
        return graph
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting user graph: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user graph"
        )


@router.get("/conversations/{conversation_id}", response_model=List[InsightResponse])
async def get_conversation_insights(
    conversation_id: str,
    user_id: str = "test-user"  # TODO: Get from auth
) -> List[Dict[str, Any]]:
    """
    Get insights for a specific conversation.
    """
    try:
        from app.db.supabase import supabase_client
        insights = await supabase_client.get_insights_by_conversation(conversation_id)
        return insights
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting conversation insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation insights"
        )


@router.post("/conversations/{conversation_id}/generate", response_model=List[InsightResponse])
async def generate_conversation_insights(
    conversation_id: str,
    user_id: str = "test-user"  # TODO: Get from auth
) -> List[Dict[str, Any]]:
    """
    Generate insights for a conversation.
    """
    try:
        insights = await insights_service.generate_conversation_insights(user_id, conversation_id)
        return insights
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating conversation insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate conversation insights"
        )
