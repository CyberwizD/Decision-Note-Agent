"""
Configuration management for DecisionNote Agent
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # API Keys
    gemini_api_key: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Voting Configuration
    voting_approval_threshold: int = 2
    voting_timeout_minutes: int = 60
    allow_self_approve: bool = False
    
    # Daily Summary Configuration
    summary_time: str = "17:00"
    summary_timezone: str = "Africa/Lagos"
    
    # Database
    database_path: str = "data/decisionnote.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()
