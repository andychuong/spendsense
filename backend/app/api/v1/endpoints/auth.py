"""Authentication endpoints."""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_tokens_for_user,
    decode_refresh_token,
    create_access_token,
    create_refresh_token,
)
from app.core.dependencies import get_current_active_user
from app.models.user import User, UserRole
from app.models.session import Session as SessionModel
from app.api.v1.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    UserLoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user with email and password.
    
    Args:
        request: Registration request with email and password
        db: Database session
        
    Returns:
        User registration response with tokens
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Check if user with email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        role=UserRole.USER.value,  # Explicitly use the enum value
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create session for refresh token
    # Use a temporary unique token to avoid unique constraint violation
    temp_token = str(uuid.uuid4())
    session = SessionModel(
        user_id=user.user_id,
        refresh_token=temp_token,  # Temporary unique token
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Create tokens
    access_token, refresh_token = create_tokens_for_user(
        user_id=user.user_id,
        email=user.email or "",
        role=user.role,
        session_id=session.session_id,
    )
    
    # Update session with actual refresh token
    session.refresh_token = refresh_token
    db.commit()
    
    return UserRegisterResponse(
        user_id=str(user.user_id),
        email=user.email or "",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/login", response_model=UserLoginResponse)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Login user with email and password.
    
    Args:
        request: Login request with email and password
        db: Database session
        
    Returns:
        User login response with tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not for security
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user has password (might have registered via OAuth)
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create session for refresh token
    # Use a temporary unique token to avoid unique constraint violation
    temp_token = str(uuid.uuid4())
    session = SessionModel(
        user_id=user.user_id,
        refresh_token=temp_token,  # Temporary unique token
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Create tokens
    access_token, refresh_token = create_tokens_for_user(
        user_id=user.user_id,
        email=user.email or "",
        role=user.role,
        session_id=session.session_id,
    )
    
    # Update session with actual refresh token
    session.refresh_token = refresh_token
    db.commit()
    
    return UserLoginResponse(
        user_id=str(user.user_id),
        email=user.email or "",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Token refresh request with refresh token
        db: Database session
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    try:
        # Decode refresh token
        payload = decode_refresh_token(request.refresh_token)
        user_id = uuid.UUID(payload["user_id"])
        token_id = uuid.UUID(payload["token_id"])
        
        # Find session
        session = db.query(SessionModel).filter(
            SessionModel.session_id == token_id,
            SessionModel.user_id == user_id,
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if session is expired
        if session.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify refresh token matches
        if session.refresh_token != request.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        access_token, refresh_token = create_tokens_for_user(
            user_id=user.user_id,
            email=user.email or "",
            role=user.role,
            session_id=session.session_id,
        )
        
        # Update session with new refresh token
        session.refresh_token = refresh_token
        session.last_used_at = datetime.utcnow()
        db.commit()
        
        return TokenRefreshResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Logout user by revoking refresh tokens.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    """
    # Delete all sessions for the user
    db.query(SessionModel).filter(SessionModel.user_id == current_user.user_id).delete()
    db.commit()
    
    return None

