"""
Base classes for LLM services.
"""
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from abc import ABC, abstractmethod

class LLMService(ABC):
    """
    Abstract base class for LLM services.
    """
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: User message/prompt
            system_message: Optional system message
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate chat completion.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated response
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming chat completion.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            
        Yields:
            Generated text chunks
        """
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        pass