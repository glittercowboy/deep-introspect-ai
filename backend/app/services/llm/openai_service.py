"""
OpenAI service for LLM operations.
"""
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
import openai
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.llm.base import LLMService
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)

class OpenAIService(LLMService):
    """
    Service for interacting with OpenAI models.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of the service exists."""
        if cls._instance is None:
            cls._instance = super(OpenAIService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.default_model = "gpt-4-turbo"
        self.embedding_model = settings.DEFAULT_EMBEDDING_MODEL
        logger.info("OpenAI service initialized")
    
    async def generate_text(
        self, 
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text completion using OpenAI chat models.
        
        Args:
            prompt: User message/prompt
            system_message: Optional system message
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            raise LLMError(f"Error generating text: {str(e)}")
    
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate chat completion using OpenAI.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated response
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating chat with OpenAI: {str(e)}")
            raise LLMError(f"Error generating chat: {str(e)}")
    
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming chat completion using OpenAI.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            
        Yields:
            Generated text chunks
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error generating stream with OpenAI: {str(e)}")
            raise LLMError(f"Error generating stream: {str(e)}")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Error generating embeddings with OpenAI: {str(e)}")
            raise LLMError(f"Error generating embeddings: {str(e)}")
    
    async def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        try:
            from tiktoken import encoding_for_model
            
            # Use cl100k_base for newer models like gpt-4 and gpt-3.5-turbo
            encoder = encoding_for_model(self.default_model)
            return len(encoder.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
            # Fallback to rough estimation
            return len(text) // 4

# Create a singleton instance
openai_service = OpenAIService()