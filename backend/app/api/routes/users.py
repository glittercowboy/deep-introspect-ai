"""
User API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.db.supabase import supabase_client
from app.api.routes.auth import get_current_user
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/users", tags=["users"])

# Models for request and response
class UserProfile(BaseModel):
    """User profile model."""
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    preferences: Dict[str, Any] = {}

class UserProfileUpdate(BaseModel):
    """User profile update model."""
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserStats(BaseModel):
    """User statistics model."""
    conversation_count: int
    message_count: int
    insight_count: int
    last_activity: Optional[datetime] = None
    total_tokens_used: int = 0

@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get the current user's profile.
    
    Args:
        current_user: Current user data
        
    Returns:
        User profile
    """
    # We already have most of the user data from the dependency
    # Just format it to match the response model
    profile = {
        "id": current_user["id"],
        "email": current_user["email"],
        "full_name": current_user.get("full_name"),
        "created_at": datetime.fromisoformat(current_user["created_at"]),
        "preferences": current_user.get("preferences", {})
    }
    
    return profile

@router.patch("/me", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update the current user's profile.
    
    Args:
        profile_update: Profile data to update
        current_user: Current user data
        
    Returns:
        Updated user profile
    """
    # Build update data
    update_data = {}
    
    if profile_update.full_name is not None:
        update_data["full_name"] = profile_update.full_name
        
    if profile_update.preferences is not None:
        # Merge with existing preferences
        existing_prefs = current_user.get("preferences", {})
        update_data["preferences"] = {**existing_prefs, **profile_update.preferences}
    
    if not update_data:
        # No changes requested
        return await get_profile(current_user)
    
    # Update the user in the database
    updated_user = await supabase_client.update_user(current_user["id"], update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    # Return the updated profile
    return {
        "id": updated_user["id"],
        "email": updated_user["email"],
        "full_name": updated_user.get("full_name"),
        "created_at": datetime.fromisoformat(updated_user["created_at"]),
        "preferences": updated_user.get("preferences", {})
    }

@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get the current user's statistics.
    
    Args:
        current_user: Current user data
        
    Returns:
        User statistics
    """
    user_id = current_user["id"]
    
    # Get conversations
    conversations = await supabase_client.get_conversations(user_id)
    conversation_count = len(conversations)
    
    # Get message count (across all conversations)
    message_count = 0
    for conversation in conversations:
        messages = await supabase_client.get_messages(conversation["id"])
        message_count += len(messages)
    
    # Get insights
    insights = await supabase_client.get_insights(user_id)
    insight_count = len(insights)
    
    # Determine last activity
    last_activity = None
    if conversations:
        # Sort conversations by updated_at
        sorted_conversations = sorted(
            conversations,
            key=lambda c: c.get("updated_at", c.get("created_at")),
            reverse=True
        )
        last_activity_str = sorted_conversations[0].get("updated_at", sorted_conversations[0].get("created_at"))
        if last_activity_str:
            last_activity = datetime.fromisoformat(last_activity_str)
    
    # Return stats
    return {
        "conversation_count": conversation_count,
        "message_count": message_count,
        "insight_count": insight_count,
        "last_activity": last_activity,
        "total_tokens_used": current_user.get("total_tokens_used", 0)
    }