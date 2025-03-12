"""
Factory for LLM services.
"""
import logging
from enum import Enum
from app.services.llm.base import LLMService
from app.services.llm.openai_service import openai_service
from app.services.llm.anthropic_service import anthropic_service
from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    """Enum for LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class LLMFactory:
    """
    Factory for creating and retrieving LLM services.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(LLMFactory, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the factory."""
        self.services = {
            LLMProvider.OPENAI: openai_service,
            LLMProvider.ANTHROPIC: anthropic_service
        }
        self.default_provider = LLMProvider.ANTHROPIC
        logger.info("LLM factory initialized with default provider: %s", self.default_provider)
    
    def get_service(self, provider: str = None) -> LLMService:
        """
        Get the LLM service for the specified provider.
        
        Args:
            provider: Provider name (openai or anthropic)
            
        Returns:
            LLM service instance
        """
        if not provider:
            provider = self.default_provider
        
        try:
            provider_enum = LLMProvider(provider.lower())
            return self.services[provider_enum]
        except (ValueError, KeyError):
            logger.warning(f"Invalid provider: {provider}, using default: {self.default_provider}")
            return self.services[self.default_provider]
    
    def set_default_provider(self, provider: str):
        """
        Set the default LLM provider.
        
        Args:
            provider: Provider name (openai or anthropic)
        """
        try:
            self.default_provider = LLMProvider(provider.lower())
            logger.info(f"Default LLM provider set to: {self.default_provider}")
        except ValueError:
            logger.error(f"Invalid provider: {provider}")
            raise ValidationError(f"Invalid LLM provider: {provider}. Valid options are: {', '.join([p.value for p in LLMProvider])}")

# Create a singleton instance
llm_factory = LLMFactory()