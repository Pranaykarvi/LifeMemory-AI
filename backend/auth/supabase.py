"""
Supabase authentication and JWT verification middleware.

JWT verification uses OIDC discovery to dynamically fetch JWKS URI.
This is OIDC-compliant and works across all Supabase projects.
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from jwt import PyJWKClient, decode
from supabase import Client
from database.connection import get_supabase_client
from config.settings import get_settings
import logging
import httpx

security = HTTPBearer()
logger = logging.getLogger(__name__)

# Load OIDC configuration at module initialization
settings = get_settings()
OIDC_CONFIG_URL = f"{settings.SUPABASE_URL}/auth/v1/.well-known/openid-configuration"

# Fetch OIDC config once at startup
try:
    with httpx.Client(timeout=5.0) as client:
        resp = client.get(OIDC_CONFIG_URL)
        resp.raise_for_status()
        oidc_config = resp.json()
    
    ISSUER = oidc_config["issuer"]
    JWKS_URI = oidc_config["jwks_uri"]
    
    logger.info(f"Loaded OIDC config from /auth/v1/.well-known/openid-configuration")
    logger.info(f"Issuer: {ISSUER}")
    logger.info(f"JWKS URI: {JWKS_URI}")
    
    # Initialize JWKS client with discovered URI
    jwks_client = PyJWKClient(JWKS_URI)
    logger.info("Initialized JWKS client with discovered URI")
    
except Exception as e:
    logger.error(f"Failed to load OIDC configuration: {str(e)}")
    raise RuntimeError(f"OIDC discovery failed: {str(e)}") from e


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify Supabase JWT token using OIDC-discovered JWKS.
    
    This function:
    - Uses JWKS URI discovered via OIDC configuration
    - Verifies token signature using RS256
    - Validates audience and issuer (OIDC-compliant)
    - Extracts user information
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        dict: Token payload containing user_id and other claims
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        logger.info(f"Verifying token: {token[:20]}...")
        
        # Get signing key from JWKS (discovered via OIDC)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        
        # Decode and verify token with ES256 or RS256
        # Supabase projects may use either algorithm depending on configuration
        # Validate audience and issuer for security (OIDC-compliant)
        payload = decode(
            token,
            signing_key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=ISSUER,
        )
        
        # Extract user_id from token
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token missing user_id (sub claim)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id"
            )
        
        logger.info(f"Token verified successfully for user: {user_id}")
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "token": token
        }
        
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
        )


async def get_current_user(
    token_data: dict = Depends(verify_token)
) -> str:
    """
    Extract user_id from verified token.
    
    Args:
        token_data: Verified token payload from verify_token
        
    Returns:
        str: User ID (UUID)
    """
    return token_data["user_id"]


def get_supabase_rest_headers(token: str) -> dict:
    """
    Get headers for Supabase REST API calls with user authentication.
    
    RLS requires both:
    - Authorization: Bearer <USER_JWT> - establishes auth.uid()
    - apikey: <ANON_KEY> - required for REST API access
    
    Args:
        token: User's JWT token
        
    Returns:
        dict: Headers dict with Authorization and apikey
    """
    settings = get_settings()
    return {
        "Authorization": f"Bearer {token}",
        "apikey": settings.SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
