"""
Chat API models.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base message model."""
    content: str
    role: Literal["user", "assistant"] = "user"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MessageCreate(MessageBase):
    """Message creation model."""
    conversation_id: str


class MessageResponse(MessageBase):
    """Message response model."""
    id: str
    conversation_id: str
    created_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class ConversationBase(BaseModel):
    """Base conversation model."""
    title: Optional[str] = None
    model: Optional[str] = "anthropic"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ConversationCreate(ConversationBase):
    """Conversation creation model."""
    pass


class ConversationUpdate(BaseModel):
    """Conversation update model."""
    title: Optional[str] = None
    model: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(ConversationBase):
    """Conversation response model."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    """Conversation detail response with messages."""
    messages: List[MessageResponse] = Field(default_factory=list)


class SendMessageRequest(BaseModel):
    """Send message request model."""
    content: str
    conversation_id: str
    model: Optional[str] = None


class SendMessageResponse(BaseModel):
    """Send message response model."""
    message: MessageResponse
    conversation: ConversationResponse


class StreamMessageRequest(SendMessageRequest):
    """Stream message request model."""
    pass


class StartConversationRequest(BaseModel):
    """Start conversation request model."""
    title: Optional[str] = None
    model: Optional[str] = "anthropic"


class StartConversationResponse(BaseModel):
    """Start conversation response model."""
    conversation: ConversationResponse
    welcome_message: Optional[MessageResponse] = None
