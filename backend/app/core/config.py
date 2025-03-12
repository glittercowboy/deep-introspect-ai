"""
Application configuration module
"""
import os
import secrets
from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    """Application settings class"""
    
    PROJECT_NAME: str = "DeepIntrospect AI"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Secret key for JWT
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # JWT token expiration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Supabase configuration
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    
    # Neo4j configuration
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    
    # LLM API keys
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    
    # mem0 API key
    MEM0_API_KEY: str
    
    # Default LLM model to use
    DEFAULT_LLM_MODEL: str = "claude-3-opus-20240229"  # Anthropic Claude 3 Opus
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-large"  # OpenAI embedding model
    
    # Validators
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string if provided as comma-separated string"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        """Pydantic config"""
        env_file = ".env"
        case_sensitive = True

settings = Settings(
    # Default values for when .env file is missing
    SUPABASE_URL=os.getenv("SUPABASE_URL", ""),
    SUPABASE_SERVICE_KEY=os.getenv("SUPABASE_SERVICE_KEY", ""),
    NEO4J_URI=os.getenv("NEO4J_URI", ""),
    NEO4J_USERNAME=os.getenv("NEO4J_USERNAME", ""),
    NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD", ""),
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
    ANTHROPIC_API_KEY=os.getenv("ANTHROPIC_API_KEY", ""),
    MEM0_API_KEY=os.getenv("MEM0_API_KEY", ""),
)