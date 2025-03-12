"""
Chat routes for the API.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from app.services.chat.chat_service import chat_service
from app.core.exceptions import NotFoundError, AuthorizationError
from app.api.routes.users import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

# Models
class ConversationCreate(BaseModel):
    """Conversation creation model."""
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    """Conversation response model."""
    id: str
    title: str
    user_id: str
    created_at: str
    updated_at: str
    model: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MessageCreate(BaseModel):
    """Message creation model."""
    content: str

class MessageResponse(BaseModel):
    """Message response model."""
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConversationSummary(BaseModel):
    """Conversation summary model."""
    summary: str

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Create a new conversation.
    """
    # Start conversation
    result = await chat_service.start_conversation(
        user_id=current_user["id"],
        title=conversation.title
    )
    
    return result

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    List all conversations for the current user.
    """
    from app.db.supabase import supabase_client
    
    conversations = await supabase_client.get_conversations(current_user["id"])
    return conversations

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Get a specific conversation by ID.
    """
    from app.db.supabase import supabase_client
    
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Verify ownership
    if conversation["user_id"] != current_user["id"]:
        raise AuthorizationError("Not authorized to access this conversation")
    
    return conversation

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Send a message in a conversation and get a response.
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and user has access
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise AuthorizationError("Not authorized to access this conversation")
    
    # Send message and get response
    response = await chat_service.send_message(
        conversation_id=conversation_id,
        user_id=current_user["id"],
        content=message.content
    )
    
    return response

@router.post("/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> StreamingResponse:
    """
    Send a message in a conversation and get a streaming response.
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and user has access
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise AuthorizationError("Not authorized to access this conversation")
    
    # Create streaming response
    async def event_generator():
        async for chunk in chat_service.stream_message(
            conversation_id=conversation_id,
            user_id=current_user["id"],
            content=message.content
        ):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Get all messages in a conversation.
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and user has access
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise AuthorizationError("Not authorized to access this conversation")
    
    # Get messages
    messages = await chat_service.get_conversation_history(conversation_id)
    return messages

@router.get("/{conversation_id}/summary", response_model=ConversationSummary)
async def get_conversation_summary(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Get a summary of a conversation.
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and user has access
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise AuthorizationError("Not authorized to access this conversation")
    
    # Get summary
    summary = await chat_service.summarize_conversation(conversation_id)
    return {"summary": summary}