"""Security utilities for authentication and authorization."""

import uuid
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from app.config import settings
from app.models.user import UserRole

# Password hashing context with bcrypt (cost factor 12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def generate_rsa_key_pair() -> tuple[str, str]:
    """
    Generate RSA key pair for JWT signing.
    
    Returns:
        Tuple of (private_key_pem, public_key_pem) as strings
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_key_pem, public_key_pem


# In-memory cache for generated keys (development only)
_generated_keys: Optional[tuple[str, str]] = None

# Path to store generated keys in development (for persistence across restarts)
DEV_KEYS_DIR = Path(__file__).parent.parent.parent / ".dev_keys"
DEV_PRIVATE_KEY_PATH = DEV_KEYS_DIR / "jwt_private_key.pem"
DEV_PUBLIC_KEY_PATH = DEV_KEYS_DIR / "jwt_public_key.pem"


def _load_or_generate_dev_keys() -> tuple[str, str]:
    """
    Load existing dev keys from disk or generate new ones.
    
    This ensures keys persist across server restarts in development.
    
    Returns:
        Tuple of (private_key, public_key)
    """
    global _generated_keys
    
    if _generated_keys is not None:
        return _generated_keys
    
    # Try to load existing keys from disk
    if DEV_PRIVATE_KEY_PATH.exists() and DEV_PUBLIC_KEY_PATH.exists():
        try:
            private_key = DEV_PRIVATE_KEY_PATH.read_text()
            public_key = DEV_PUBLIC_KEY_PATH.read_text()
            _generated_keys = (private_key, public_key)
            print("INFO: Loaded existing RSA keys from .dev_keys/ for development.")
            return _generated_keys
        except Exception as e:
            print(f"WARNING: Failed to load existing dev keys: {e}. Generating new keys.")
    
    # Generate new keys
    private_key, public_key = generate_rsa_key_pair()
    _generated_keys = (private_key, public_key)
    
    # Save keys to disk for persistence
    try:
        DEV_KEYS_DIR.mkdir(exist_ok=True)
        DEV_PRIVATE_KEY_PATH.write_text(private_key)
        DEV_PUBLIC_KEY_PATH.write_text(public_key)
        # Set restrictive permissions (read/write for owner only)
        os.chmod(DEV_PRIVATE_KEY_PATH, 0o600)
        os.chmod(DEV_PUBLIC_KEY_PATH, 0o644)
        print("INFO: Generated and saved RSA keys to .dev_keys/ for development.")
        print("WARNING: These keys are for development only. In production, keys must be in AWS Secrets Manager.")
    except Exception as e:
        print(f"WARNING: Failed to save dev keys to disk: {e}. Keys will only persist for this session.")
    
    return _generated_keys


def get_jwt_private_key() -> str:
    """
    Get JWT private key for signing tokens.
    
    In production, this should load from AWS Secrets Manager.
    For development, it can be loaded from environment variable, disk, or generated.
    """
    if hasattr(settings, 'jwt_private_key') and settings.jwt_private_key:
        return settings.jwt_private_key
    
    # For development only: load from disk or generate keys if not provided
    # In production, this should never happen - keys should be in Secrets Manager
    if settings.environment == "development":
        private_key, _ = _load_or_generate_dev_keys()
        return private_key
    else:
        raise ValueError(
            "JWT private key not configured. Set JWT_PRIVATE_KEY environment variable "
            "or configure it in AWS Secrets Manager."
        )


def get_jwt_public_key() -> str:
    """
    Get JWT public key for verifying tokens.
    
    In production, this should load from AWS Secrets Manager.
    For development, it can be loaded from environment variable, disk, or derived from private key.
    """
    if hasattr(settings, 'jwt_public_key') and settings.jwt_public_key:
        return settings.jwt_public_key
    
    # For development, try to load from disk or derive from private key
    if settings.environment == "development":
        _, public_key = _load_or_generate_dev_keys()
        return public_key
    
    # For production, try to derive from private key
    try:
        private_key_pem = get_jwt_private_key()
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
    except Exception as e:
        raise ValueError(
            f"JWT public key not configured. Set JWT_PUBLIC_KEY environment variable "
            f"or configure it in AWS Secrets Manager. Error: {str(e)}"
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt with cost factor 12.
    
    Args:
        password: Plain text password
        
    Returns:
        Bcrypt hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing token claims (user_id, email, role)
        expires_delta: Optional expiration time delta. Defaults to 1 hour.
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    # Use RS256 algorithm
    encoded_jwt = jwt.encode(
        to_encode,
        get_jwt_private_key(),
        algorithm="RS256"
    )
    
    return encoded_jwt


def create_refresh_token(user_id: uuid.UUID, token_id: uuid.UUID) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        user_id: User UUID
        token_id: Session/token UUID
        
    Returns:
        Encoded JWT refresh token string
    """
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    
    to_encode = {
        "user_id": str(user_id),
        "token_id": str(token_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    # Use RS256 algorithm
    encoded_jwt = jwt.encode(
        to_encode,
        get_jwt_private_key(),
        algorithm="RS256"
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary containing token claims
        
    Raises:
        JWTError: If token is invalid, expired, or cannot be decoded
    """
    try:
        payload = jwt.decode(
            token,
            get_jwt_public_key(),
            algorithms=["RS256"]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def create_tokens_for_user(user_id: uuid.UUID, email: str, role: UserRole, session_id: uuid.UUID) -> tuple[str, str]:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        user_id: User UUID
        email: User email
        role: User role
        session_id: Session UUID for refresh token
        
    Returns:
        Tuple of (access_token, refresh_token)
    """
    access_token_data = {
        "user_id": str(user_id),
        "email": email,
        "role": role.value,
    }
    
    access_token = create_access_token(access_token_data)
    refresh_token = create_refresh_token(user_id, session_id)
    
    return access_token, refresh_token


def decode_refresh_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a refresh token.
    
    Args:
        token: JWT refresh token string
        
    Returns:
        Dictionary containing token claims (user_id, token_id)
        
    Raises:
        JWTError: If token is invalid, expired, or cannot be decoded
    """
    try:
        payload = decode_token(token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise JWTError("Token is not a refresh token")
        
        # Validate required claims
        if "user_id" not in payload or "token_id" not in payload:
            raise JWTError("Invalid refresh token claims")
        
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid refresh token: {str(e)}")


def is_token_blacklisted(token_id: str, redis_client: Optional[Any] = None) -> bool:
    """
    Check if a token is blacklisted in Redis.
    
    Args:
        token_id: Token/session ID to check
        redis_client: Optional Redis client. If None, returns False (no blacklist check).
        
    Returns:
        True if token is blacklisted, False otherwise
    """
    if redis_client is None:
        # Redis not available, skip blacklist check
        return False
    
    try:
        key = f"blacklist:token:{token_id}"
        exists = redis_client.exists(key)
        return bool(exists)
    except Exception:
        # If Redis is unavailable, log but don't block
        # In production, this should be handled more carefully
        return False


def blacklist_token(token_id: str, expires_at: datetime, redis_client: Optional[Any] = None) -> None:
    """
    Blacklist a token in Redis.
    
    Args:
        token_id: Token/session ID to blacklist
        expires_at: Token expiration time (sets Redis TTL)
        redis_client: Optional Redis client. If None, does nothing.
    """
    if redis_client is None:
        # Redis not available, skip blacklisting
        return
    
    try:
        key = f"blacklist:token:{token_id}"
        # Calculate TTL in seconds
        ttl = int((expires_at - datetime.utcnow()).total_seconds())
        if ttl > 0:
            redis_client.setex(key, ttl, "1")
    except Exception:
        # If Redis is unavailable, log but don't fail
        # In production, this should be handled more carefully
        pass

