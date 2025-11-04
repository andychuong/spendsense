"""FastAPI dependencies for authentication and authorization."""

import logging
from typing import Optional, Union
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

# HTTP Bearer token scheme
security = HTTPBearer()

# Logger for authorization events
logger = logging.getLogger(__name__)


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
            logger.warning(
                f"Authorization denied: User {current_user.user_id} (role: {user_role.value}) "
                f"attempted to access endpoint requiring {required_role.value} role or higher"
            )
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


def check_resource_access(
    resource_user_id: Union[uuid.UUID, str],
    current_user: User,
    allow_operator: bool = True,
    allow_admin: bool = True,
    check_consent: bool = True,
    db: Optional[Session] = None,
) -> bool:
    """
    Check if current user can access a resource.
    
    Resource-level authorization:
    - Users can access their own resources
    - Operators can access all user resources (if allow_operator=True)
    - Admins can access all resources (if allow_admin=True)
    - Operators/admins must respect user consent (if check_consent=True)
    
    Args:
        resource_user_id: User ID of the resource owner
        current_user: Current authenticated user
        allow_operator: Whether operators can access this resource
        allow_admin: Whether admins can access this resource
        check_consent: Whether to check the resource owner's consent status
        db: Optional database session to check resource owner's consent
        
    Returns:
        True if user can access resource, False otherwise
    """
    # Convert resource_user_id to UUID if needed
    if isinstance(resource_user_id, str):
        try:
            resource_user_id = uuid.UUID(resource_user_id)
        except ValueError:
            return False
    
    # Users can always access their own resources (consent not checked for own data)
    if current_user.user_id == resource_user_id:
        return True
    
    # Check operator access
    if allow_operator:
        user_role = current_user.role
        if isinstance(user_role, str):
            try:
                user_role = UserRole(user_role)
            except ValueError:
                user_role = UserRole.USER
        
        if user_role in (UserRole.OPERATOR, UserRole.ADMIN):
            # Operators and admins can access resources, but must respect consent
            if check_consent and db is not None:
                # Check if the resource owner has granted consent
                from app.models.user import User as UserModel
                resource_owner = db.query(UserModel).filter(
                    UserModel.user_id == resource_user_id
                ).first()
                
                if resource_owner and not resource_owner.consent_status:
                    # Resource owner has revoked consent or never gave consent
                    logger.warning(
                        f"Access denied: Operator/Admin {current_user.user_id} attempted to access "
                        f"resource owned by {resource_user_id} who has revoked consent"
                    )
                    return False
            
            # Operators and admins can access resources (consent check passed or not required)
            return True
    
    return False


def require_resource_access_factory(
    allow_operator: bool = True,
    allow_admin: bool = True,
    check_consent: bool = True,
):
    """
    Factory function to create a dependency that requires resource access.
    
    Usage in endpoint:
        @router.get("/users/{user_id}/profile")
        async def get_profile(
            user_id: uuid.UUID,
            current_user: User = Depends(get_current_active_user),
            db: Session = Depends(get_db),
            _: User = Depends(require_resource_access_factory(check_consent=True)(user_id, db)),
        ):
            ...
    
    Args:
        allow_operator: Whether operators can access this resource
        allow_admin: Whether admins can access this resource
        check_consent: Whether to check the resource owner's consent status
        
    Returns:
        A function that takes resource_user_id and db and returns a dependency
    """
    def resource_access_checker(
        resource_user_id: Union[uuid.UUID, str],
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        """
        Dependency to require resource access.
        
        Checks if current user can access a resource (either owner or operator/admin).
        Operators and admins must respect user consent when accessing other users' data.
        Raises HTTPException if access is denied.
        
        Args:
            resource_user_id: User ID of the resource owner
            db: Database session to check resource owner's consent
            current_user: Current authenticated user
            
        Returns:
            Current user if access is granted
            
        Raises:
            HTTPException: 403 Forbidden if access is denied
        """
        if not check_resource_access(
            resource_user_id=resource_user_id,
            current_user=current_user,
            allow_operator=allow_operator,
            allow_admin=allow_admin,
            check_consent=check_consent,
            db=db,
        ):
            # Check if it's a consent issue
            from app.models.user import User as UserModel
            resource_owner = db.query(UserModel).filter(
                UserModel.user_id == resource_user_id
            ).first()
            
            if resource_owner and not resource_owner.consent_status:
                logger.warning(
                    f"Access denied (consent): User {current_user.user_id} (role: {current_user.role}) "
                    f"attempted to access resource owned by {resource_user_id} who has revoked consent"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot access this user's data. User has revoked consent or not granted consent."
                )
            
            logger.warning(
                f"Authorization denied: User {current_user.user_id} (role: {current_user.role}) "
                f"attempted to access resource owned by {resource_user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )
        
        return current_user
    
    return resource_access_checker


def require_owner_or_operator_factory():
    """
    Factory function to create a dependency that requires resource ownership or operator role.
    
    Users can access their own resources, operators can access any user resource.
    
    Usage in endpoint:
        @router.get("/users/{user_id}/profile")
        async def get_profile(
            user_id: uuid.UUID,
            current_user: User = Depends(require_owner_or_operator_factory()(user_id)),
        ):
            ...
    """
    return require_resource_access_factory(allow_operator=True, allow_admin=True)


def require_owner_or_admin_factory():
    """
    Factory function to create a dependency that requires resource ownership or admin role.
    
    Users can access their own resources, admins can access any resource.
    Operators cannot access these resources.
    
    Usage in endpoint:
        @router.get("/users/{user_id}/admin-data")
        async def get_admin_data(
            user_id: uuid.UUID,
            current_user: User = Depends(require_owner_or_admin_factory()(user_id)),
        ):
            ...
    """
    return require_resource_access_factory(allow_operator=False, allow_admin=True)


def require_owner_only_factory():
    """
    Factory function to create a dependency that requires resource ownership only.
    
    Only the resource owner can access this resource.
    Operators and admins cannot access these resources.
    
    Usage in endpoint:
        @router.get("/users/{user_id}/private-data")
        async def get_private_data(
            user_id: uuid.UUID,
            current_user: User = Depends(require_owner_only_factory()(user_id)),
        ):
            ...
    """
    return require_resource_access_factory(allow_operator=False, allow_admin=False)


# Convenience functions for common patterns
def check_user_access(
    user_id: Union[uuid.UUID, str],
    current_user: User,
    db: Optional[Session] = None,
    check_consent: bool = True,
) -> bool:
    """
    Convenience function to check if current user can access another user's data.
    
    Users can access their own data, operators and admins can access any user's data.
    Operators and admins must respect user consent when accessing other users' data.
    
    Args:
        user_id: User ID to check access for
        current_user: Current authenticated user
        db: Optional database session to check target user's consent
        check_consent: Whether to check the target user's consent status (default: True)
        
    Returns:
        True if user can access, False otherwise
    """
    return check_resource_access(
        resource_user_id=user_id,
        current_user=current_user,
        allow_operator=True,
        allow_admin=True,
        check_consent=check_consent,
        db=db,
    )


def require_consent(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require user consent for data processing.
    
    This dependency should be used in endpoints that process user data or generate recommendations.
    Raises HTTPException if user has not granted consent.
    
    Usage:
        @router.get("/recommendations")
        async def get_recommendations(
            current_user: User = Depends(require_consent)
        ):
            # Only users who have granted consent can access this endpoint
            ...
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if consent is granted
        
    Raises:
        HTTPException: 403 Forbidden if consent not granted
    """
    if not current_user.consent_status:
        logger.warning(
            f"Consent check failed: User {current_user.user_id} attempted to access "
            f"data processing without consent"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required for data processing. Please grant consent first."
        )
    
    return current_user

