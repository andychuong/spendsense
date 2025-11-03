"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, user

api_router = APIRouter(prefix="/api/v1")

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(user.router)

