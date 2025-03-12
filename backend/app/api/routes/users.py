"""
User API routes.
"""
import logging
from typing import Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies.auth import get_current_user, get_current_active_user
from app.api.models.user import (
    UserResponse,
    UserProfileResponse,
    UserUpdate,
    UserPreferences
)
from app.db.supabase import supabase_client
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.get("/me", response_model=UserResponse)
async def get_current_user_route(
    current_user: dict = Depends(get_current_active_user)
) -> Any:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return current_user


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: dict = Depends(get_current_active_user)
) -> Any:
    """
    Get detailed user profile with stats and preferences.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile with additional information
    """
    # Get conversation count
    conversations = await supabase_client.get_conversations(current_user["id"])
    conversation_count = len(conversations)
    
    # Get insight count
    insights = await supabase_client.get_insights(current_user["id"])
    insight_count = len(insights)
    
    # Get user preferences
    preferences = current_user.get("preferences", {})
    if not preferences:
        # Set default preferences
        preferences = {
            "theme": "dark",
            "default_model": "anthropic",
            "notification_enabled": True,
            "insights_enabled": True
        }
    
    # Last activity
    last_activity = current_user.get("last_activity")
    if not last_activity and conversations:
        # Use latest conversation update time
        conversations.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        last_activity = conversations[0].get("updated_at")
    
    return UserProfileResponse(
        **current_user,
        conversation_count=conversation_count,
        insight_count=insight_count,
        preferences=UserPreferences(**preferences),
        last_activity=last_activity
    )


@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_active_user)
) -> Any:
    """
    Update current user information.
    
    Args:
        user_update: User data to update
        current_user: Current authenticated user
        
    Returns:
        Updated user information
    """
    # Build update data
    update_data = {}
    
    if user_update.name is not None:
        update_data["name"] = user_update.name
    
    if user_update.email is not None:
        # Check if email already exists
        if user_update.email != current_user["email"]:
            existing_user = await supabase_client.get_user_by_email(user_update.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
        
        update_data["email"] = user_update.email
    
    if user_update.password is not None:
        update_data["password_hash"] = get_password_hash(user_update.password)
    
    if update_data:
        update_data["updated_at"] = datetime.now().isoformat()
        updated_user = await supabase_client.update_user(current_user["id"], update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user",
            )
        
        return updated_user
    
    return current_user


@router.put("/me/preferences", response_model=UserPreferences)
async def update_preferences(
    preferences: UserPreferences,
    current_user: dict = Depends(get_current_active_user)
) -> Any:
    """
    Update user preferences.
    
    Args:
        preferences: User preferences to update
        current_user: Current authenticated user
        
    Returns:
        Updated preferences
    """
    # Get current preferences
    current_preferences = current_user.get("preferences", {})
    if not current_preferences:
        current_preferences = {
            "theme": "dark",
            "default_model": "anthropic",
            "notification_enabled": True,
            "insights_enabled": True
        }
    
    # Update preferences
    updated_preferences = {**current_preferences}
    
    if preferences.theme is not None:
        updated_preferences["theme"] = preferences.theme
    
    if preferences.default_model is not None:
        updated_preferences["default_model"] = preferences.default_model
    
    if preferences.notification_enabled is not None:
        updated_preferences["notification_enabled"] = preferences.notification_enabled
    
    if preferences.insights_enabled is not None:
        updated_preferences["insights_enabled"] = preferences.insights_enabled
    
    # Update user
    update_data = {
        "preferences": updated_preferences,
        "updated_at": datetime.now().isoformat()
    }
    
    updated_user = await supabase_client.update_user(current_user["id"], update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences",
        )
    
    return UserPreferences(**updated_preferences)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    current_user: dict = Depends(get_current_active_user)
) -> Any:
    """
    Delete current user.
    
    Args:
        current_user: Current authenticated user
    """
    # Delete user
    success = await supabase_client.delete_user(current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )
    
    return None
