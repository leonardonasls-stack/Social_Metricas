from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    BACKEND_PORT: int = 8000
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/metrica_social"
    
    DEFAULT_MINING_MODE: str = "mock"
    SCRAPECREATORS_API_KEY: Optional[str] = None
    SCRAPECREATORS_BASE_URL: str = "https://api.scrapecreators.com"
    
    SYNTHESIS_API_KEY: Optional[str] = None
    SYNTHESIS_MODEL: str = "gpt-4o-mini"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
