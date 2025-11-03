"""FastAPI application entry point."""

from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "SpendSense API", "version": settings.app_version}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

