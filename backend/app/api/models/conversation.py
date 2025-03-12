"""
API models for conversations.
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class ConversationBase(BaseModel):
    """Base schema for a conversation."""
    title: Optional[str] = Field(None, description="The title of the conversation")


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""
    pass


class ConversationResponse(ConversationBase):
    """Schema for returning a conversation."""
    id: str = Field(..., description="The conversation ID")
    user_id: str = Field(..., description="The user ID")
    created_at: datetime = Field(..., description="The timestamp when the conversation was created")
    updated_at: datetime = Field(..., description="The timestamp when the conversation was last updated")
    model: str = Field(..., description="The LLM model used for this conversation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    

class ConversationList(BaseModel):
    """Schema for returning a list of conversations."""
    conversations: List[ConversationResponse] = Field(..., description="List of conversations")


class ConversationSummary(BaseModel):
    """Schema for a conversation summary."""
    id: str = Field(..., description="The conversation ID")
    title: str = Field(..., description="The title of the conversation")
    summary: str = Field(..., description="The summary of the conversation")
    message_count: int = Field(..., description="The number of messages in the conversation")
    created_at: datetime = Field(..., description="The timestamp when the conversation was created")
    updated_at: datetime = Field(..., description="The timestamp when the conversation was last updated")
