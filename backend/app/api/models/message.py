"""
API models for messages.
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base schema for a message."""
    content: str = Field(..., description="The content of the message")


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    pass


class MessageResponse(MessageBase):
    """Schema for returning a message."""
    id: str = Field(..., description="The message ID")
    conversation_id: str = Field(..., description="The conversation ID")
    role: str = Field(..., description="The role of the message sender (user or assistant)")
    created_at: datetime = Field(..., description="The timestamp when the message was created")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MessageList(BaseModel):
    """Schema for returning a list of messages."""
    messages: List[MessageResponse] = Field(..., description="List of messages")
