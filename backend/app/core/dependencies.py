"""FastAPI dependencies for authentication and authorization."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        # Check token type
        if payload.get("type") != "access":
            raise credentials_exception
        
        user_id: Optional[str] = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not active
    """
    # Add any additional checks here (e.g., user.is_active, user.is_verified)
    # For now, just return the user
    return current_user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get the current authenticated user.
    Returns None if no token is provided or token is invalid.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header (optional)
        db: Database session
        
    Returns:
        User object or None
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        if payload.get("type") != "access":
            return None
        
        user_id: Optional[str] = payload.get("user_id")
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.user_id == user_id).first()
        return user
    except (JWTError, Exception):
        return None


def require_role(required_role: UserRole):
    """
    Dependency factory to require a specific role.
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function that checks role
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        # Check if user has required role or higher
        # Convert string role to UserRole enum if needed
        user_role = current_user.role
        if isinstance(user_role, str):
            try:
                user_role = UserRole(user_role)
            except ValueError:
                user_role = UserRole.USER  # Default to USER if invalid
        
        role_hierarchy = {
            UserRole.USER: 1,
            UserRole.OPERATOR: 2,
            UserRole.ADMIN: 3
        }
        
        user_role_level = role_hierarchy.get(user_role, 0)
        required_role_level = role_hierarchy.get(required_role, 0)
        
        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role or higher"
            )
        
        return current_user
    
    return role_checker


def require_operator(current_user: User = Depends(require_role(UserRole.OPERATOR))) -> User:
    """
    Dependency to require operator role or higher.
    
    Args:
        current_user: Current authenticated user with operator role
        
    Returns:
        User object
    """
    return current_user


def require_admin(current_user: User = Depends(require_role(UserRole.ADMIN))) -> User:
    """
    Dependency to require admin role.
    
    Args:
        current_user: Current authenticated user with admin role
        
    Returns:
        User object
    """
    return current_user

