"""Configuration settings for the application."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "SpendSense API"
    app_version: str = "1.1.0"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 600

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_ssl: bool = False
    redis_ssl_cert_reqs: Optional[str] = None

    # AWS
    aws_region: str = "us-west-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket_data: str = "spendsense-data"
    s3_bucket_analytics: str = "spendsense-analytics"

    # JWT
    jwt_secret_key: Optional[str] = None  # For HS256 (legacy support)
    jwt_private_key: Optional[str] = None  # RSA private key for RS256
    jwt_public_key: Optional[str] = None  # RSA public key for RS256
    jwt_algorithm: str = "RS256"  # Default to RS256 as per PRD
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30

    # OAuth
    oauth_google_client_id: Optional[str] = None
    oauth_google_client_secret: Optional[str] = None
    oauth_github_client_id: Optional[str] = None
    oauth_github_client_secret: Optional[str] = None
    oauth_facebook_client_id: Optional[str] = None
    oauth_facebook_client_secret: Optional[str] = None
    oauth_apple_client_id: Optional[str] = None
    oauth_apple_key_id: Optional[str] = None
    oauth_apple_team_id: Optional[str] = None
    oauth_apple_private_key: Optional[str] = None

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    openai_fallback_model: str = "gpt-3.5-turbo"
    
    # RAG System Configuration
    rag_enabled: bool = False  # Feature flag for RAG system
    rag_rollout_percentage: float = 0.10  # Percentage of users in A/B test (0.0-1.0)
    rag_openai_model: str = "gpt-4-turbo-preview"  # Model for RAG generation
    rag_vector_db_path: str = "./data/chroma_prod"  # Path to ChromaDB
    rag_embedding_model: str = "all-MiniLM-L6-v2"  # Sentence transformer model
    rag_top_k: int = 10  # Number of documents to retrieve
    rag_force_catalog_fallback: bool = False  # Force fallback to catalog if RAG fails

    # SMS (AWS SNS)
    sns_region: str = "us-west-1"
    sms_mock_mode: bool = False  # Set to True to use mock SMS (logs codes to console instead of sending)

    # N8N Integration
    n8n_api_key: Optional[str] = None
    n8n_webhook_secret: Optional[str] = None
    n8n_webhook_url: Optional[str] = None

    # Security
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173", "http://127.0.0.1:3001"]

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()

