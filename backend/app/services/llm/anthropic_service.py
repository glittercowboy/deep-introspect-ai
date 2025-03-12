"""
Anthropic service for LLM operations.
"""
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
import anthropic
from anthropic import AsyncAnthropic
from app.core.config import settings
from app.services.llm.base import LLMService
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)

class AnthropicService(LLMService):
    """
    Service for interacting with Anthropic Claude models.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of the service exists."""
        if cls._instance is None:
            cls._instance = super(AnthropicService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the Anthropic client."""
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.default_model = settings.DEFAULT_LLM_MODEL
        logger.info("Anthropic service initialized with model: %s", self.default_model)
    
    async def generate_text(
        self, 
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text completion using Anthropic Claude.
        
        Args:
            prompt: User message/prompt
            system_message: Optional system message
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated text
        """
        try:
            message = await self.client.messages.create(
                model=self.default_model,
                max_tokens=max_tokens or 1024,
                temperature=temperature,
                system=system_message,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error generating text with Anthropic: {str(e)}")
            raise LLMError(f"Error generating text: {str(e)}")
    
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate chat completion using Anthropic Claude.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated response
        """
        try:
            # Extract system message if present
            system_message = None
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                elif msg["role"] in ["user", "assistant"]:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            message = await self.client.messages.create(
                model=self.default_model,
                max_tokens=max_tokens or 1024,
                temperature=temperature,
                system=system_message,
                messages=claude_messages
            )
            
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error generating chat with Anthropic: {str(e)}")
            raise LLMError(f"Error generating chat: {str(e)}")
    
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming chat completion using Anthropic Claude.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            
        Yields:
            Generated text chunks
        """
        try:
            # Extract system message if present
            system_message = None
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                elif msg["role"] in ["user", "assistant"]:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            stream = await self.client.messages.create(
                model=self.default_model,
                max_tokens=max_tokens or 1024,
                temperature=temperature,
                system=system_message,
                messages=claude_messages,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.type == "content_block_delta" and chunk.delta.text:
                    yield chunk.delta.text
        except Exception as e:
            logger.error(f"Error generating stream with Anthropic: {str(e)}")
            raise LLMError(f"Error generating stream: {str(e)}")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        Note: Anthropic doesn't provide embedding models, so we fallback to OpenAI.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        # Fallback to OpenAI embeddings
        from app.services.llm.openai_service import openai_service
        return await openai_service.generate_embeddings(texts)
    
    async def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text using Anthropic's tokenizer.
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        try:
            from anthropic.tokenizer import count_tokens
            return count_tokens(text)
        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
            # Fallback to rough estimation
            return len(text) // 4

# Create a singleton instance
anthropic_service = AnthropicService()