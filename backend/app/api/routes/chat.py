"""
Chat API routes.
"""
import logging
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from app.api.dependencies.auth import get_current_user
from app.api.models.chat import (
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse,
    SendMessageRequest,
    SendMessageResponse,
    StartConversationRequest,
    StartConversationResponse
)
from app.services.chat.chat_service import chat_service
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Get all conversations for the current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of conversations
    """
    conversations = await chat_service.get_user_conversations(current_user["id"])
    return conversations


@router.post("/conversations", response_model=StartConversationResponse)
async def start_conversation(
    request: StartConversationRequest,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Start a new conversation.
    
    Args:
        request: Start conversation request with title and model
        current_user: Current authenticated user
        
    Returns:
        New conversation with welcome message
    """
    conversation = await chat_service.start_conversation(
        user_id=current_user["id"],
        title=request.title,
    )
    
    # Get the welcome message (first message in the conversation)
    messages = await chat_service.get_conversation_history(conversation["id"])
    welcome_message = messages[0] if messages else None
    
    return StartConversationResponse(
        conversation=conversation,
        welcome_message=welcome_message
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Get conversation details with messages.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        
    Returns:
        Conversation details with messages
    """
    # Get conversation
    conversation = await chat_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    # Check if user owns the conversation
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )
    
    # Get messages
    messages = await chat_service.get_conversation_history(conversation_id)
    
    # Return conversation with messages
    return ConversationDetailResponse(
        **conversation,
        messages=messages
    )


@router.post("/messages", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Send a message and get a response.
    
    Args:
        request: Send message request with content and conversation ID
        current_user: Current authenticated user
        
    Returns:
        Response message and updated conversation
    """
    # Get conversation to verify ownership
    conversation = await chat_service.get_conversation(request.conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    # Check if user owns the conversation
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )
    
    # Set model if specified
    if request.model:
        # Update the model in the conversation
        conversation = await chat_service.update_conversation(
            request.conversation_id,
            {"model": request.model}
        )
    
    # Send message and get response
    response_message = await chat_service.send_message(
        conversation_id=request.conversation_id,
        user_id=current_user["id"],
        content=request.content
    )
    
    # Get updated conversation
    updated_conversation = await chat_service.get_conversation(request.conversation_id)
    
    return SendMessageResponse(
        message=response_message,
        conversation=updated_conversation
    )


@router.post("/messages/stream")
async def stream_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
) -> StreamingResponse:
    """
    Send a message and stream the response.
    
    Args:
        request: Send message request with content and conversation ID
        current_user: Current authenticated user
        
    Returns:
        Streaming response with message chunks
    """
    # Get conversation to verify ownership
    conversation = await chat_service.get_conversation(request.conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    # Check if user owns the conversation
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )
    
    # Set model if specified
    if request.model:
        # Update the model in the conversation
        conversation = await chat_service.update_conversation(
            request.conversation_id,
            {"model": request.model}
        )
    
    # Create streaming response
    async def response_generator():
        async for chunk in chat_service.stream_message(
            conversation_id=request.conversation_id,
            user_id=current_user["id"],
            content=request.content
        ):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream"
    )


@router.post("/conversations/{conversation_id}/summarize")
async def summarize_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Generate a summary of a conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        
    Returns:
        Conversation summary
    """
    # Get conversation to verify ownership
    conversation = await chat_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    # Check if user owns the conversation
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )
    
    # Generate summary
    summary = await chat_service.summarize_conversation(conversation_id)
    
    return {"summary": summary}


# WebSocket endpoint for real-time chat
@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str
):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: WebSocket connection
        conversation_id: Conversation ID
        token: JWT token for authentication
    """
    await websocket.accept()
    
    try:
        # Authenticate user with token
        from jose import jwt
        from app.core.config import settings
        from app.api.models.auth import TokenPayload
        
        # Decode token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        
        # Validate token payload
        token_data = TokenPayload(**payload)
        
        # Get user ID
        user_id = token_data.sub
        
        # Get conversation to verify ownership
        conversation = await chat_service.get_conversation(conversation_id)
        if not conversation or conversation["user_id"] != user_id:
            await websocket.close(code=1008, reason="Not authorized")
            return
        
        # Handle messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process message
            content = data.get("content")
            if not content:
                continue
            
            # Stream response
            async for chunk in chat_service.stream_message(
                conversation_id=conversation_id,
                user_id=user_id,
                content=content
            ):
                await websocket.send_json({"chunk": chunk})
            
            # Send end of message marker
            await websocket.send_json({"done": True})
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011, reason="Server error")
