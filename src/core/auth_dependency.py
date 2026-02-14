from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from src.core.config import get_settings

settings = get_settings()

# Define the API Key Header
api_key_header = APIKeyHeader(name="X-Sentinel-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """
    Validates the API Key from the header.
    In a real app, you would check this against a DB of valid keys.
    For MVP, we check against a single Env Var (SECRET_KEY or specific API_KEY).
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing API Key"
        )
    
    # Simple check: Does it match our master secret?
    # In prod, query: SELECT * FROM api_keys WHERE key = :api_key_header
    if api_key_header != settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return api_key_header
