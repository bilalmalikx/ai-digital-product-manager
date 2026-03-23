from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings."""

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    LANGSMITH_PROJECT_NAME: str = os.getenv("LANGSMITH_PROJECT_NAME", "default_project")

    class config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()