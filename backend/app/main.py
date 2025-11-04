"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import api_router

# OpenAPI documentation metadata
description = """
SpendSense API provides a comprehensive platform for financial data analysis,
persona-based recommendations, and user profile management.

## Features

* **Authentication**: Multiple authentication methods including email/password,
  phone/SMS, and OAuth (Google, GitHub, Facebook, Apple)
* **User Management**: Profile management, account linking, and data deletion
* **Consent Management**: GDPR-compliant consent tracking and revocation
* **Data Upload**: Secure file upload for transaction data (JSON/CSV formats)
* **Recommendations**: Personalized financial recommendations based on behavioral signals
* **Operator Dashboard**: Review queue and analytics for operators

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the
Authorization header:

```
Authorization: Bearer <your_access_token>
```

Access tokens expire after 1 hour. Use the refresh token endpoint to obtain new
access tokens.

## Rate Limiting

* General API: 1000 requests/hour per user
* Authentication endpoints: 5 attempts/hour per IP
* SMS verification: 5 SMS/hour, 10 SMS/day per phone number

## Response Caching

Some endpoints cache responses for performance:
* User profiles: 5 minutes
* Recommendations: 1 hour
* Behavioral signals: 24 hours
"""

tags_metadata = [
    {
        "name": "authentication",
        "description": "User authentication and session management. Includes email/password, phone/SMS, and OAuth authentication methods.",
    },
    {
        "name": "users",
        "description": "User profile management and data access. Users can view and update their own profiles, and operators can access user profiles with proper authorization.",
    },
    {
        "name": "consent",
        "description": "Consent management for GDPR compliance. Users can grant, revoke, and check their consent status for data processing.",
    },
    {
        "name": "data",
        "description": "Transaction data upload and management. Users can upload financial data files in JSON or CSV format.",
    },
    {
        "name": "operator",
        "description": "Operator dashboard endpoints. Requires operator or admin role. Includes review queue, analytics, and user management.",
    },
    {
        "name": "health",
        "description": "Health check and system status endpoints.",
    },
]

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=description,
    debug=settings.debug,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "SpendSense API", "version": settings.app_version}


@app.get("/health", tags=["health"])
async def health():
    """
    Health check endpoint.

    Returns the health status of the API service.
    """
    return {"status": "healthy"}

