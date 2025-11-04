"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, user, operator, consent, data_upload, recommendations

api_router = APIRouter(prefix="/api/v1")

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(consent.router)
api_router.include_router(operator.router)
api_router.include_router(data_upload.router)
api_router.include_router(recommendations.router)

