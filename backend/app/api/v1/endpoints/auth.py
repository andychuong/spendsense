"""Authentication endpoints."""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse
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
from app.core.sms_service import (
    send_verification_code,
    verify_verification_code,
    validate_phone_number,
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
    PhoneVerificationRequest,
    PhoneVerificationRequestResponse,
    PhoneVerificationVerifyRequest,
    PhoneVerificationVerifyResponse,
    OAuthAuthorizeResponse,
    OAuthCallbackResponse,
)
from app.core.oauth_service import (
    get_oauth_authorize_url,
    exchange_oauth_code,
    get_oauth_user_info,
    verify_oauth_state,
    OAUTH_PROVIDERS,
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


@router.post("/phone/request", response_model=PhoneVerificationRequestResponse)
async def request_phone_verification(
    request: PhoneVerificationRequest,
):
    """
    Request SMS verification code for phone number.
    
    This endpoint:
    1. Validates phone number format
    2. Checks SMS rate limits
    3. Generates and stores verification code
    4. Sends SMS via AWS SNS
    
    Args:
        request: Phone verification request with phone number
        
    Returns:
        Success response with normalized phone number
        
    Raises:
        HTTPException: If phone number is invalid, rate limited, or SMS sending fails
    """
    try:
        # Validate and normalize phone number
        normalized_phone = validate_phone_number(request.phone)
        
        # Send verification code
        success, error_message = send_verification_code(normalized_phone)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message or "Failed to send verification code"
            )
        
        return PhoneVerificationRequestResponse(
            message="Verification code sent successfully",
            phone=normalized_phone,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/phone/verify", response_model=PhoneVerificationVerifyResponse)
async def verify_phone_code(
    request: PhoneVerificationVerifyRequest,
    db: Session = Depends(get_db),
):
    """
    Verify SMS code and register/login user.
    
    This endpoint:
    1. Validates phone number format
    2. Verifies the code against stored code in Redis
    3. Creates user if doesn't exist, or logs in existing user
    4. Generates JWT tokens
    5. Returns tokens and user info
    
    Args:
        request: Phone verification verify request with phone and code
        db: Database session
        
    Returns:
        User authentication response with tokens
        
    Raises:
        HTTPException: If code is invalid, expired, or max attempts exceeded
    """
    try:
        # Validate and normalize phone number
        normalized_phone = validate_phone_number(request.phone)
        
        # Verify code
        try:
            is_valid = verify_verification_code(normalized_phone, request.code)
        except ValueError as e:
            # Max attempts exceeded
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired verification code"
            )
        
        # Check if user exists with this phone number
        user = db.query(User).filter(User.phone_number == normalized_phone).first()
        is_new_user = False
        
        if not user:
            # Create new user
            is_new_user = True
            user = User(
                phone_number=normalized_phone,
                role=UserRole.USER.value,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # User exists, log them in
            is_new_user = False
        
        # Create session for refresh token
        temp_token = str(uuid.uuid4())
        session = SessionModel(
            user_id=user.user_id,
            refresh_token=temp_token,
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
        
        return PhoneVerificationVerifyResponse(
            user_id=str(user.user_id),
            phone=normalized_phone,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            is_new_user=is_new_user,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/oauth/{provider}/authorize", response_model=OAuthAuthorizeResponse)
async def oauth_authorize(
    provider: str,
    redirect_uri: str = Query(..., description="Callback URL after OAuth flow"),
    db: Session = Depends(get_db),
):
    """
    Initiate OAuth flow for a provider.
    
    This endpoint:
    1. Validates the provider
    2. Generates OAuth state for CSRF protection
    3. Creates authorization URL
    4. Returns authorization URL and state
    
    Args:
        provider: OAuth provider name (google, github, facebook, apple)
        redirect_uri: Callback URL after OAuth flow
        db: Database session
        
    Returns:
        OAuth authorization response with authorize URL and state
        
    Raises:
        HTTPException: If provider is invalid or not configured
    """
    provider_lower = provider.lower()
    
    # Validate provider
    if provider_lower not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}. Supported providers: {', '.join(OAUTH_PROVIDERS)}"
        )
    
    # Generate authorization URL (this also generates and stores state)
    from app.core.oauth_service import generate_oauth_state
    state = generate_oauth_state()
    authorize_url = get_oauth_authorize_url(provider_lower, redirect_uri, state)
    
    if not authorize_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth provider {provider} is not configured. Please check OAuth credentials."
        )
    
    # Extract state from URL to return it
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(authorize_url)
    params = parse_qs(parsed.query)
    state_from_url = params.get("state", [state])[0]
    
    return OAuthAuthorizeResponse(
        authorize_url=authorize_url,
        state=state_from_url,
    )


@router.get("/oauth/{provider}/callback")
@router.post("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    code: Optional[str] = Query(None, description="Authorization code from OAuth provider (GET)"),
    state: Optional[str] = Query(None, description="OAuth state parameter for CSRF protection (GET)"),
    redirect_uri: Optional[str] = Query(None, description="Callback URL used in authorization"),
    db: Session = Depends(get_db),
):
    """
    Handle OAuth callback from provider.
    
    This endpoint supports both GET and POST methods:
    - GET: Used by most OAuth providers (Google, GitHub, Facebook)
    - POST: Used by Apple Sign In (response_mode: form_post)
    
    This endpoint:
    1. Validates OAuth state (CSRF protection)
    2. Exchanges authorization code for access token
    3. Retrieves user information from provider
    4. Creates or updates user in database
    5. Links OAuth provider to user account
    6. Generates JWT tokens
    7. Returns tokens to client (via redirect or JSON)
    
    Args:
        provider: OAuth provider name (google, github, facebook, apple)
        request: FastAPI request object (for POST method)
        code: Authorization code from OAuth provider (GET) or from form data (POST)
        state: OAuth state parameter for CSRF protection (GET) or from form data (POST)
        redirect_uri: Optional callback URL (if not provided, will use stored one)
        db: Database session
        
    Returns:
        Redirect to frontend with tokens, or JSON response with tokens
        
    Raises:
        HTTPException: If OAuth flow fails or user creation fails
    """
    provider_lower = provider.lower()
    
    # Handle POST method (Apple Sign In uses form_post)
    if request.method == "POST":
        form_data = await request.form()
        code = form_data.get("code") or code
        state = form_data.get("state") or state
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code is required"
            )
        if not state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth state is required"
            )
    
    # Validate provider
    if provider_lower not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    # Validate code and state
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required"
        )
    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state is required"
        )
    
    # Verify state (CSRF protection)
    state_info = verify_oauth_state(state)
    if not state_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state"
        )
    
    # Get redirect_uri from state if not provided
    if not redirect_uri:
        redirect_uri = state_info.get("redirect_uri")
        if not redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="redirect_uri is required"
            )
    
    # Exchange code for access token
    token = await exchange_oauth_code(provider_lower, code, redirect_uri)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange authorization code for access token"
        )
    
    # Get user info from provider
    user_info = await get_oauth_user_info(provider_lower, token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve user information from OAuth provider"
        )
    
    email = user_info.get("email")
    provider_id = user_info.get("provider_id")
    
    if not provider_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth provider did not return user identifier"
        )
    
    # Check if user exists with this OAuth provider
    user = None
    is_new_user = False
    
    # Check if user exists with this email (if email provided)
    if email:
        user = db.query(User).filter(User.email == email).first()
    
    # If no user found by email, check by OAuth provider
    if not user:
        # Query users with this OAuth provider linked
        users = db.query(User).all()
        for u in users:
            oauth_providers = u.oauth_providers or {}
            if oauth_providers.get(provider_lower) == str(provider_id):
                user = u
                break
    
    if not user:
        # Create new user
        is_new_user = True
        user = User(
            email=email,
            role=UserRole.USER.value,
            oauth_providers={provider_lower: str(provider_id)},
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update existing user - link OAuth provider
        oauth_providers = user.oauth_providers or {}
        oauth_providers[provider_lower] = str(provider_id)
        # Update email if not set and OAuth provides one
        if not user.email and email:
            user.email = email
        user.oauth_providers = oauth_providers
        db.commit()
        db.refresh(user)
    
    # Create session for refresh token
    temp_token = str(uuid.uuid4())
    session = SessionModel(
        user_id=user.user_id,
        refresh_token=temp_token,
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
    
    # Return response
    # If redirect_uri is a frontend URL, redirect with tokens
    # Otherwise, return JSON response
    if redirect_uri.startswith("http://") or redirect_uri.startswith("https://"):
        # Frontend URL - redirect with tokens as query params or hash
        # For security, we'll use hash fragment (not query params)
        # Frontend will extract tokens from hash
        from urllib.parse import urlencode
        token_params = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": str(user.user_id),
            "email": user.email or "",
            "is_new_user": "true" if is_new_user else "false",
        }
        # Use hash fragment for security (not query params)
        redirect_url = f"{redirect_uri}#{urlencode(token_params)}"
        return RedirectResponse(url=redirect_url)
    else:
        # Return JSON response
        return OAuthCallbackResponse(
            user_id=str(user.user_id),
            email=user.email,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            is_new_user=is_new_user,
            provider=provider_lower,
        )

