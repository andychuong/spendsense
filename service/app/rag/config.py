"""Configuration for RAG system."""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class RAGConfig:
    """Configuration for RAG system."""
    
    # Vector database settings
    vector_db_path: str = "./data/chroma"
    collection_name: str = "financial_knowledge"
    
    # Embedding model settings
    embedding_model: str = "all-MiniLM-L6-v2"  # Fast, good quality, 384 dimensions
    # Alternative models:
    # - "all-mpnet-base-v2": Better quality, slower, 768 dimensions
    # - "paraphrase-multilingual-MiniLM-L12-v2": Multilingual support
    
    # Retrieval settings
    default_top_k: int = 5  # Number of documents to retrieve
    similarity_threshold: float = 0.5  # Minimum similarity score (0-1)
    
    # OpenAI settings (for RAG generation)
    openai_model: str = "gpt-4-turbo-preview"
    openai_fallback_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    
    # Feature flags
    enable_rag: bool = False  # Global RAG enable/disable
    enable_caching: bool = True  # Cache generated content
    enable_logging: bool = True  # Log retrieval and generation
    
    # Performance settings
    batch_size: int = 32  # For batch embedding
    max_context_length: int = 8000  # Max tokens in context (for GPT-4)
    
    @classmethod
    def from_env(cls) -> "RAGConfig":
        """Create config from environment variables."""
        return cls(
            vector_db_path=os.getenv("RAG_VECTOR_DB_PATH", "./data/chroma"),
            collection_name=os.getenv("RAG_COLLECTION_NAME", "financial_knowledge"),
            embedding_model=os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            default_top_k=int(os.getenv("RAG_DEFAULT_TOP_K", "5")),
            similarity_threshold=float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.5")),
            openai_model=os.getenv("RAG_OPENAI_MODEL", "gpt-4-turbo-preview"),
            openai_fallback_model=os.getenv("RAG_OPENAI_FALLBACK_MODEL", "gpt-3.5-turbo"),
            openai_temperature=float(os.getenv("RAG_OPENAI_TEMPERATURE", "0.7")),
            openai_max_tokens=int(os.getenv("RAG_OPENAI_MAX_TOKENS", "2000")),
            enable_rag=os.getenv("RAG_ENABLE", "false").lower() == "true",
            enable_caching=os.getenv("RAG_ENABLE_CACHING", "true").lower() == "true",
            enable_logging=os.getenv("RAG_ENABLE_LOGGING", "true").lower() == "true",
            batch_size=int(os.getenv("RAG_BATCH_SIZE", "32")),
            max_context_length=int(os.getenv("RAG_MAX_CONTEXT_LENGTH", "8000")),
        )


# Default configuration
DEFAULT_CONFIG = RAGConfig()

