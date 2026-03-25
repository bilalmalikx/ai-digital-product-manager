from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import ConfigDict
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:admin@localhost:5432/product_agent"
    
    # LLM
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    
    # LangSmith
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT_NAME: str = "product_agent_system"
    LANGSMITH_TRACING_V2: str = "true"
    
    # MCP Config
    MCP_SERVER_URL: str = "http://localhost:8001"
    
    # API Keys
    TAVILY_API_KEY: Optional[str] = None
    SERPAPI_API_KEY: Optional[str] = None
    
    # Model Selection
    DEFAULT_MODEL: str = "gpt-4o"
    MODEL_PROVIDER: str = "openai"
    
    # Pydantic v2 configuration
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # This allows extra env vars like LANGSMITH_TRACING_V2
    )

settings = Settings()