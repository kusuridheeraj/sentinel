from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentinel Access Gateway"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "change_me_in_production_please"  # Used for session signing
    ALGORITHM: str = "HS256"
    
    # Azure AD (OIDC)
    AZURE_CLIENT_ID: str = ""
    AZURE_TENANT_ID: str = ""
    AZURE_CLIENT_SECRET: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sentinel.db"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
