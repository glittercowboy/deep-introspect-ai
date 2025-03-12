"""
Chat API routes.
"""
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.services.chat.chat_service import chat_service
from app.core.exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/chat", tags=["chat"])


class MessageRequest(BaseModel):
    """Message request model."""
    content: str = Field(..., description="Message content")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "content": "Hello, I'm feeling anxious about my upcoming job interview."
            }
        }


class MessageResponse(BaseModel):
    """Message response model."""
    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    created_at: str = Field(..., description="Creation timestamp")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174001",
                "role": "assistant",
                "content": "I understand feeling anxious about interviews. Let's talk about what specifically concerns you.",
                "created_at": "2025-01-01T00:00:00Z"
            }
        }


class ConversationResponse(BaseModel):
    """Conversation response model."""
    id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Conversation title")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "user_id": "123e4567-e89b-12d3-a456-426614174002",
                "title": "Conversation about interview anxiety",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T01:00:00Z"
            }
        }


class ConversationRequest(BaseModel):
    """Conversation request model."""
    title: Optional[str] = Field(None, description="Conversation title")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "title": "Conversation about interview anxiety"
            }
        }


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationRequest,
    user_id: str = "test-user"  # TODO: Get from auth
) -> Dict[str, Any]:
    """
    Create a new conversation.
    """
    try:
        conversation = await chat_service.start_conversation(user_id, request.title)
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: str = "test-user"  # TODO: Get from auth
) -> List[Dict[str, Any]]:
    """
    List all conversations for a user.
    """
    try:
        from app.db.supabase import supabase_client
        conversations = await supabase_client.get_conversations(user_id)
        return conversations
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations"
        )


@router.get("/conversations/{conversation_id}", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    user_id: str = "test-user"  # TODO: Get from auth
) -> List[Dict[str, Any]]:
    """
    Get all messages for a conversation.
    """
    try:
        messages = await chat_service.get_conversation_history(conversation_id)
        return messages
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting conversation messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation messages"
        )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    request: MessageRequest,
    user_id: str = "test-user"  # TODO: Get from auth
) -> Dict[str, Any]:
    """
    Send a message to a conversation.
    """
    try:
        response = await chat_service.send_message(
            conversation_id,
            user_id,
            request.content
        )
        return response
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.post("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: str,
    request: MessageRequest,
    user_id: str = "test-user"  # TODO: Get from auth
) -> StreamingResponse:
    """
    Send a message to a conversation and stream the response.
    """
    try:
        async def generate():
            async for chunk in chat_service.stream_message(
                conversation_id,
                user_id,
                request.content
            ):
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error streaming message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stream message"
        )


@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: str,
    user_id: str = "test-user"  # TODO: Get from auth
) -> Dict[str, Any]:
    """
    Get a summary of a conversation.
    """
    try:
        summary = await chat_service.summarize_conversation(conversation_id)
        return {"summary": summary}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting conversation summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation summary"
        )
