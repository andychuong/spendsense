"""OAuth 2.0 service for handling OAuth authentication flows."""

import secrets
import json
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode
from datetime import datetime, timedelta

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
import httpx

from app.config import settings
from app.core.redis_client import get_redis_client


# Supported OAuth providers
OAUTH_PROVIDERS = ["google", "github", "facebook", "apple"]


def generate_oauth_state() -> str:
    """
    Generate a cryptographically secure random state for OAuth flow.
    
    This state is used to prevent CSRF attacks.
    
    Returns:
        Random state string (32 characters)
    """
    return secrets.token_urlsafe(32)


def store_oauth_state(state: str, provider: str, redirect_uri: Optional[str] = None) -> bool:
    """
    Store OAuth state in Redis with 10-minute TTL.
    
    Args:
        state: OAuth state string
        provider: OAuth provider name (google, github, facebook, apple)
        redirect_uri: Optional redirect URI to store with state
        
    Returns:
        True if stored successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        # Redis not available, but we can still proceed (development mode)
        return False
    
    try:
        key = f"oauth:state:{state}"
        value = {
            "provider": provider,
            "redirect_uri": redirect_uri,
            "created_at": datetime.utcnow().isoformat(),
        }
        # Store with 10-minute TTL
        redis_client.setex(key, 600, json.dumps(value))
        return True
    except Exception:
        return False


def verify_oauth_state(state: str) -> Optional[Dict[str, Any]]:
    """
    Verify and retrieve OAuth state from Redis.
    
    Args:
        state: OAuth state string to verify
        
    Returns:
        Dictionary with provider and redirect_uri if valid, None otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        # Redis not available, but we can still proceed (development mode)
        return None
    
    try:
        key = f"oauth:state:{state}"
        value = redis_client.get(key)
        if not value:
            return None
        
        # Delete state after use (one-time use)
        redis_client.delete(key)
        
        return json.loads(value)
    except Exception:
        return None


def get_oauth_config(provider: str) -> Optional[Dict[str, Any]]:
    """
    Get OAuth configuration for a provider.
    
    Args:
        provider: OAuth provider name (google, github, facebook, apple)
        
    Returns:
        Dictionary with client_id, client_secret, and endpoints, or None if not configured
    """
    provider_lower = provider.lower()
    
    if provider_lower == "google":
        if not settings.oauth_google_client_id or not settings.oauth_google_client_secret:
            return None
        return {
            "client_id": settings.oauth_google_client_id,
            "client_secret": settings.oauth_google_client_secret,
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
            "scopes": ["email", "profile", "openid"],
        }
    
    elif provider_lower == "github":
        if not settings.oauth_github_client_id or not settings.oauth_github_client_secret:
            return None
        return {
            "client_id": settings.oauth_github_client_id,
            "client_secret": settings.oauth_github_client_secret,
            "authorize_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
            "scopes": ["user:email"],
        }
    
    elif provider_lower == "facebook":
        if not settings.oauth_facebook_client_id or not settings.oauth_facebook_client_secret:
            return None
        return {
            "client_id": settings.oauth_facebook_client_id,
            "client_secret": settings.oauth_facebook_client_secret,
            "authorize_url": "https://www.facebook.com/v18.0/dialog/oauth",
            "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
            "userinfo_url": "https://graph.facebook.com/v18.0/me",
            "scopes": ["email", "public_profile"],
        }
    
    elif provider_lower == "apple":
        if not settings.oauth_apple_client_id or not settings.oauth_apple_key_id or not settings.oauth_apple_team_id or not settings.oauth_apple_private_key:
            return None
        return {
            "client_id": settings.oauth_apple_client_id,
            "key_id": settings.oauth_apple_key_id,
            "team_id": settings.oauth_apple_team_id,
            "private_key": settings.oauth_apple_private_key,
            "authorize_url": "https://appleid.apple.com/auth/authorize",
            "token_url": "https://appleid.apple.com/auth/token",
            "scopes": ["email", "name"],
        }
    
    return None


def get_oauth_authorize_url(provider: str, redirect_uri: str, state: Optional[str] = None) -> Optional[str]:
    """
    Generate OAuth authorization URL for a provider.
    
    Args:
        provider: OAuth provider name (google, github, facebook, apple)
        redirect_uri: Callback URL after OAuth flow
        state: Optional OAuth state (will be generated if not provided)
        
    Returns:
        Authorization URL or None if provider not configured
    """
    config = get_oauth_config(provider)
    if not config:
        return None
    
    if not state:
        state = generate_oauth_state()
    
    # Store state in Redis
    store_oauth_state(state, provider, redirect_uri)
    
    provider_lower = provider.lower()
    
    if provider_lower == "google":
        params = {
            "client_id": config["client_id"],
            "response_type": "code",
            "scope": " ".join(config["scopes"]),
            "redirect_uri": redirect_uri,
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{config['authorize_url']}?{urlencode(params)}"
    
    elif provider_lower == "github":
        params = {
            "client_id": config["client_id"],
            "scope": " ".join(config["scopes"]),
            "redirect_uri": redirect_uri,
            "state": state,
        }
        return f"{config['authorize_url']}?{urlencode(params)}"
    
    elif provider_lower == "facebook":
        params = {
            "client_id": config["client_id"],
            "scope": ",".join(config["scopes"]),
            "redirect_uri": redirect_uri,
            "state": state,
            "response_type": "code",
        }
        return f"{config['authorize_url']}?{urlencode(params)}"
    
    elif provider_lower == "apple":
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(config["scopes"]),
            "response_mode": "form_post",
            "state": state,
        }
        return f"{config['authorize_url']}?{urlencode(params)}"
    
    return None


async def exchange_oauth_code(
    provider: str, code: str, redirect_uri: str
) -> Optional[OAuth2Token]:
    """
    Exchange OAuth authorization code for access token.
    
    Args:
        provider: OAuth provider name (google, github, facebook, apple)
        code: Authorization code from OAuth callback
        redirect_uri: Callback URL used in authorization
        
    Returns:
        OAuth2Token object with access token, or None if exchange failed
    """
    config = get_oauth_config(provider)
    if not config:
        return None
    
    provider_lower = provider.lower()
    
    try:
        if provider_lower == "apple":
            # Apple Sign In requires special handling with JWT client secret
            # For now, we'll use a simpler approach with httpx
            # Note: Apple Sign In implementation is more complex and may need additional work
            async with httpx.AsyncClient() as client:
                data = {
                    "client_id": config["client_id"],
                    "client_secret": config["private_key"],  # This should be a JWT for Apple
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                }
                response = await client.post(config["token_url"], data=data)
                if response.status_code == 200:
                    token_data = response.json()
                    return OAuth2Token(token_data)
                return None
        
        # For other providers, use Authlib OAuth2Client
        async with AsyncOAuth2Client(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
        ) as client:
            token = await client.fetch_token(
                config["token_url"],
                code=code,
                redirect_uri=redirect_uri,
            )
            return OAuth2Token(token)
    except Exception:
        return None


async def get_oauth_user_info(provider: str, token: OAuth2Token) -> Optional[Dict[str, Any]]:
    """
    Retrieve user information from OAuth provider.
    
    Args:
        provider: OAuth provider name (google, github, facebook, apple)
        token: OAuth2Token with access token
        
    Returns:
        Dictionary with user information (email, name, provider_id), or None if failed
    """
    config = get_oauth_config(provider)
    if not config:
        return None
    
    provider_lower = provider.lower()
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token['access_token']}"}
            
            if provider_lower == "google":
                response = await client.get(config["userinfo_url"], headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "email": data.get("email"),
                        "name": data.get("name"),
                        "provider_id": data.get("id"),
                        "picture": data.get("picture"),
                    }
            
            elif provider_lower == "github":
                response = await client.get(config["userinfo_url"], headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Get email separately if not in user info
                    email = data.get("email")
                    if not email:
                        # Try to get primary email from emails endpoint
                        emails_response = await client.get(
                            "https://api.github.com/user/emails",
                            headers=headers,
                        )
                        if emails_response.status_code == 200:
                            emails = emails_response.json()
                            primary_email = next(
                                (e["email"] for e in emails if e.get("primary")), None
                            )
                            email = primary_email or (emails[0]["email"] if emails else None)
                    
                    return {
                        "email": email,
                        "name": data.get("name") or data.get("login"),
                        "provider_id": str(data.get("id")),
                        "picture": data.get("avatar_url"),
                    }
            
            elif provider_lower == "facebook":
                # Facebook requires fields parameter
                params = {"fields": "id,name,email,picture"}
                response = await client.get(
                    config["userinfo_url"],
                    headers=headers,
                    params=params,
                )
                if response.status_code == 200:
                    data = response.json()
                    picture_url = None
                    if data.get("picture") and data["picture"].get("data"):
                        picture_url = data["picture"]["data"].get("url")
                    
                    return {
                        "email": data.get("email"),
                        "name": data.get("name"),
                        "provider_id": data.get("id"),
                        "picture": picture_url,
                    }
            
            elif provider_lower == "apple":
                # Apple Sign In returns user info in ID token
                # For now, we'll decode the ID token if available
                # Note: Apple Sign In implementation may need additional work
                id_token = token.get("id_token")
                if id_token:
                    # Decode ID token (JWT) to get user info
                    # In production, you should verify the signature
                    import base64
                    try:
                        # JWT has 3 parts separated by dots
                        parts = id_token.split(".")
                        if len(parts) >= 2:
                            # Decode payload (second part)
                            payload = parts[1]
                            # Add padding if needed
                            payload += "=" * (4 - len(payload) % 4)
                            decoded = base64.urlsafe_b64decode(payload)
                            data = json.loads(decoded)
                            
                            return {
                                "email": data.get("email"),
                                "name": None,  # Apple doesn't return name in ID token
                                "provider_id": data.get("sub"),
                                "picture": None,
                            }
                    except Exception:
                        pass
                
                return None
            
            return None
    except Exception:
        return None

