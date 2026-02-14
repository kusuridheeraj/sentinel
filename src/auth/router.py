from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from src.core.config import get_settings

router = APIRouter()
settings = get_settings()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/oauth2/v2.0/authorize",
    tokenUrl=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/oauth2/v2.0/token",
)

@router.get("/login")
def login():
    """
    Redirects user to Azure AD for authentication.
    """
    return {
        "msg": "Redirect user to this URL",
        "url": f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/oauth2/v2.0/authorize?client_id={settings.AZURE_CLIENT_ID}&response_type=code&scope=openid profile"
    }

@router.get("/callback")
def callback(code: str):
    """
    Exchanges authorization code for JWT.
    In a real app, backend calls Azure AD /token endpoint here.
    """
    # Mock implementation
    return {"msg": "Auth successful", "code": code, "mock_token": "ey..."}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validates JWT and returns user context.
    This is the Gatekeeper.
    """
    # TODO: Implement actual JWT validation with JWKS
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"sub": "user_123", "roles": ["admin"]}
