from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    BACKEND_PORT: int = 8000
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/metrica_social"
    
    DEFAULT_MINING_MODE: str = "mock"
    SCRAPECREATORS_API_KEY: Optional[str] = None
    SCRAPECREATORS_BASE_URL: str = "https://api.scrapecreators.com"
    
    # Configurações Multi-LLM para Failover
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "deepseek-r1-distill-llama-70b"
    
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "deepseek/deepseek-r1:free"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
