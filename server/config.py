"""
Server Configuration
Centralized configuration for FastAPI server
"""
import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class ServerSettings(BaseSettings):
    """Server configuration settings"""
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    RELOAD: bool = False
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Security
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/market_viz.db"
    DATABASE_ECHO: bool = False
    
    # API
    API_V1_PREFIX: str = "/api"
    API_TITLE: str = "Market Research Visualization API"
    API_DESCRIPTION: str = "Real-time market analytics and data API"
    API_VERSION: str = "1.0.0"
    
    # Paths
    OUTPUTS_DIR: str = "outputs"
    STATIC_DIR: str = "outputs/static"
    ANIMATED_DIR: str = "outputs/animated"
    DATA_DIR: str = "data"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 100
    
    # Background Tasks
    ENABLE_SCHEDULER: bool = True
    MARKET_UPDATE_INTERVAL_MINUTES: int = 15
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


def get_settings() -> ServerSettings:
    """Get server settings singleton"""
    return ServerSettings()


settings = get_settings()
