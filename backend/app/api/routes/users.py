"""
User API routes.
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from app.api.models.user import User, UserUpdate, UserResponse
from app.services.insights.insights_service import insights_service
from app.api.dependencies.auth import get_current_user
from app.db.supabase import supabase_client

router = APIRouter(prefix="/v1/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current user information.
    """
    # Get user from database
    user_data = await supabase_client.get_user(current_user.id)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_data

@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update the current user information.
    """
    # Update user in database
    updated_user = await supabase_client.update_user(
        user_id=current_user.id,
        user_data=user_update.dict(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user

@router.get("/me/insights")
async def get_user_insights(
    current_user: User = Depends(get_current_user)
):
    """
    Get insights for the current user.
    """
    insights = await insights_service.get_user_insights(current_user.id)
    
    return {
        "insights": insights
    }

@router.get("/me/summary")
async def get_user_summary(
    current_user: User = Depends(get_current_user)
):
    """
    Get a summary of the current user based on insights.
    """
    summary = await insights_service.generate_user_summary(current_user.id)
    
    return summary

@router.get("/me/insights/graph")
async def get_user_insights_graph(
    current_user: User = Depends(get_current_user)
):
    """
    Get a visual graph of the current user's insights.
    """
    graph = await insights_service.generate_insight_graph(current_user.id)
    
    return graph

@router.get("/me/knowledge")
async def get_user_knowledge(
    current_user: User = Depends(get_current_user),
    depth: int = Query(2, ge=1, le=5)
):
    """
    Get the knowledge graph for the current user.
    """
    from app.services.knowledge.knowledge_service import knowledge_service
    
    graph = await knowledge_service.get_user_knowledge_graph(
        user_id=current_user.id,
        depth=depth
    )
    
    return graph

@router.get("/me/preferences")
async def get_user_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get user preferences.
    """
    # Get user from database
    user_data = await supabase_client.get_user(current_user.id)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return preferences if they exist
    preferences = user_data.get("preferences", {})
    
    return preferences

@router.patch("/me/preferences")
async def update_user_preferences(
    preferences: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Update user preferences.
    """
    # Get current user data
    user_data = await supabase_client.get_user(current_user.id)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update preferences
    current_preferences = user_data.get("preferences", {})
    updated_preferences = {**current_preferences, **preferences}
    
    # Update user in database
    updated_user = await supabase_client.update_user(
        user_id=current_user.id,
        user_data={"preferences": updated_preferences}
    )
    
    if not updated_user:
        raise HTTPException(status_code=500, detail="Failed to update preferences")
    
    return updated_preferences