"""
API routes for chat functionality.
"""
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.chat.chat_service import chat_service
from app.core.exceptions import NotFoundError, LLMError
from app.api.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/chat", tags=["chat"])

# Request and response models
class ConversationCreate(BaseModel):
    """Request model for creating a conversation."""
    title: Optional[str] = None

class MessageCreate(BaseModel):
    """Request model for creating a message."""
    content: str = Field(..., min_length=1, max_length=4096)

class Message(BaseModel):
    """Response model for a message."""
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str
    metadata: Dict[str, Any] = {}

class Conversation(BaseModel):
    """Response model for a conversation."""
    id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    model: str
    metadata: Dict[str, Any] = {}

# API Routes
@router.post("/conversations", response_model=Conversation, status_code=201)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new conversation.
    """
    try:
        conversation = await chat_service.start_conversation(
            user_id=current_user["id"], 
            title=conversation_data.title
        )
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")

@router.get("/conversations", response_model=List[Conversation])
async def list_conversations(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List all conversations for the current user.
    """
    from app.db.supabase import supabase_client
    try:
        conversations = await supabase_client.get_conversations(current_user["id"])
        return conversations
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list conversations")

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a conversation by ID.
    """
    from app.db.supabase import supabase_client
    try:
        conversation = await supabase_client.get_conversation(conversation_id)
        
        if not conversation:
            raise NotFoundError(f"Conversation {conversation_id} not found")
        
        # Check ownership
        if conversation["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
        
        return conversation
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get conversation")

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def list_messages(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List all messages in a conversation.
    """
    try:
        # Check if conversation exists and belongs to the user
        from app.db.supabase import supabase_client
        conversation = await supabase_client.get_conversation(conversation_id)
        
        if not conversation:
            raise NotFoundError(f"Conversation {conversation_id} not found")
        
        # Check ownership
        if conversation["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
        
        messages = await chat_service.get_conversation_history(conversation_id)
        return messages
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list messages")

@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def create_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new message in a conversation and get a response.
    """
    try:
        # Check if conversation exists and belongs to the user
        from app.db.supabase import supabase_client
        conversation = await supabase_client.get_conversation(conversation_id)
        
        if not conversation:
            raise NotFoundError(f"Conversation {conversation_id} not found")
        
        # Check ownership
        if conversation["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
        
        # Send message and get response
        response = await chat_service.send_message(
            conversation_id=conversation_id,
            user_id=current_user["id"],
            content=message_data.content
        )
        
        return response
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LLMError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create message")

@router.post("/conversations/{conversation_id}/messages/stream", status_code=200)
async def stream_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new message in a conversation and stream the response.
    """
    try:
        # Check if conversation exists and belongs to the user
        from app.db.supabase import supabase_client
        conversation = await supabase_client.get_conversation(conversation_id)
        
        if not conversation:
            raise NotFoundError(f"Conversation {conversation_id} not found")
        
        # Check ownership
        if conversation["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
        
        # Create async generator for streaming response
        async def generate_stream():
            try:
                async for chunk in chat_service.stream_message(
                    conversation_id=conversation_id,
                    user_id=current_user["id"],
                    content=message_data.content
                ):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                logger.error(f"Error streaming message: {str(e)}")
                yield f"data: [ERROR] {str(e)}\n\n"
            
            # End the stream
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting up message stream: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to set up message stream")

@router.get("/conversations/{conversation_id}/summary", response_model=dict)
async def get_conversation_summary(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a summary of a conversation.
    """
    try:
        # Check if conversation exists and belongs to the user
        from app.db.supabase import supabase_client
        conversation = await supabase_client.get_conversation(conversation_id)
        
        if not conversation:
            raise NotFoundError(f"Conversation {conversation_id} not found")
        
        # Check ownership
        if conversation["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
        
        summary = await chat_service.summarize_conversation(conversation_id)
        return {"summary": summary}