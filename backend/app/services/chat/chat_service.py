"""
Chat service for handling conversations and interactions.
"""
import logging
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from app.services.llm.factory import llm_factory
from app.services.memory.memory_service import memory_service
from app.services.knowledge.knowledge_service import knowledge_service
from app.services.insights.insights_service import insights_service

logger = logging.getLogger(__name__)

class ChatService:
    """
    Service for managing chat conversations.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of the service exists."""
        if cls._instance is None:
            cls._instance = super(ChatService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the chat service."""
        self.system_message = """You are DeepIntrospect AI, a groundbreaking self-reflection AI chatbot designed to help users understand themselves better through conversation. 
        Your purpose is to facilitate personal growth through AI-assisted introspection.
        
        As you chat with users:
        - Be empathetic, thoughtful, and insightful
        - Ask probing but respectful questions that help users reflect on their thoughts, beliefs, patterns, and behaviors
        - Maintain continuity across the conversation
        - Avoid generic platitudes or shallow responses
        - When appropriate, offer observations or potential patterns you notice, but be humble and open to correction
        - Tailor your responses to the individual user based on what you learn about them
        - Help users gain valuable insights about themselves through conversation
        
        You are here to help users understand themselves better - not to give generic advice or act as a medical professional."""
        
        logger.info("Chat service initialized")
    
    async def start_conversation(self, user_id: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new conversation.
        
        Args:
            user_id: User ID
            title: Optional conversation title
            
        Returns:
            Conversation data
        """
        # Create conversation in memory service
        conversation = await memory_service.create_conversation(user_id, title)
        
        # Add welcome message from assistant
        welcome_message = """Hello! I'm DeepIntrospect AI, designed to help you better understand yourself through thoughtful conversation. As we talk, I'll learn about your thoughts, patterns, and perspectives.

How are you feeling today, and what would you like to explore or reflect on?"""
        
        await memory_service.add_message(
            conversation["id"],
            "assistant",
            welcome_message
        )
        
        return conversation
    
    async def send_message(
        self, 
        conversation_id: str,
        user_id: str, 
        content: str
    ) -> Dict[str, Any]:
        """
        Send a user message and get a response.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            content: Message content
            
        Returns:
            Response data
        """
        # Add user message to memory
        user_message = await memory_service.add_message(
            conversation_id,
            "user",
            content
        )
        
        # Get conversation context
        context_messages = await memory_service.get_conversation_context(
            conversation_id,
            query=content,
            limit=20
        )
        
        # Add system message
        messages = [{"role": "system", "content": self.system_message}] + context_messages
        
        # Get LLM service
        llm_service = llm_factory.get_service()
        
        # Generate response
        response_content = await llm_service.generate_chat(
            messages,
            temperature=0.7
        )
        
        # Add assistant message to memory
        assistant_message = await memory_service.add_message(
            conversation_id,
            "assistant",
            response_content
        )
        
        # Process conversation for knowledge and insights (run in background)
        asyncio.create_task(self._process_conversation_insights(user_id, conversation_id))
        
        return assistant_message
    
    async def stream_message(
        self,
        conversation_id: str,
        user_id: str,
        content: str
    ) -> AsyncGenerator[str, None]:
        """
        Send a user message and stream the response.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            content: Message content
            
        Yields:
            Response chunks
        """
        # Add user message to memory
        user_message = await memory_service.add_message(
            conversation_id,
            "user",
            content
        )
        
        # Get conversation context
        context_messages = await memory_service.get_conversation_context(
            conversation_id,
            query=content,
            limit=20
        )
        
        # Add system message
        messages = [{"role": "system", "content": self.system_message}] + context_messages
        
        # Get LLM service
        llm_service = llm_factory.get_service()
        
        # Generate streaming response
        full_response = ""
        async for chunk in llm_service.generate_stream(
            messages,
            temperature=0.7
        ):
            full_response += chunk
            yield chunk
        
        # Add assistant message to memory
        assistant_message = await memory_service.add_message(
            conversation_id,
            "assistant",
            full_response
        )
        
        # Process conversation for knowledge and insights (run in background)
        asyncio.create_task(self._process_conversation_insights(user_id, conversation_id))
    
    async def _process_conversation_insights(self, user_id: str, conversation_id: str) -> None:
        """
        Process conversation for insights in the background.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
        """
        try:
            # Get conversation messages
            messages = await memory_service.get_conversation_history(conversation_id)
            
            if len(messages) < 6:  # Wait until there's enough conversation
                return
            
            # Process with knowledge service
            await knowledge_service.process_conversation(user_id, conversation_id, messages)
            
            # Generate insights if conversation is substantial
            if len(messages) >= 10:
                await insights_service.generate_conversation_insights(user_id, conversation_id)
        except Exception as e:
            logger.error(f"Error processing conversation insights: {str(e)}")
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages
        """
        return await memory_service.get_conversation_history(conversation_id)
    
    async def summarize_conversation(self, conversation_id: str) -> str:
        """
        Generate a summary of a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation summary
        """
        return await memory_service.summarize_conversation(conversation_id)
    
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get insights for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            User insights data
        """
        # Get raw insights
        raw_insights = await insights_service.get_user_insights(user_id)
        
        # Get user summary
        summary = await insights_service.generate_user_summary(user_id)
        
        # Get insight graph
        graph = await insights_service.generate_insight_graph(user_id)
        
        return {
            "insights": raw_insights,
            "summary": summary,
            "graph": graph
        }

# Create a singleton instance
chat_service = ChatService()