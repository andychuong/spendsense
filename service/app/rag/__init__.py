"""RAG (Retrieval-Augmented Generation) system for SpendSense.

This module provides intelligent recommendation generation using vector-based
retrieval of relevant knowledge from a growing knowledge base.

Components:
- VectorStore: ChromaDB-based vector database for document storage and retrieval
- KnowledgeBaseBuilder: Ingests data from various sources into the knowledge base
- RAGRecommendationGenerator: Generates recommendations using retrieved context
- QueryEngine: Intelligent query generation and retrieval strategies
"""

from app.rag.vector_store import VectorStore
from app.rag.config import RAGConfig
from app.rag.query_engine import QueryEngine
from app.rag.rag_generator import RAGRecommendationGenerator
from app.rag.knowledge_builder import KnowledgeBaseBuilder

__all__ = [
    "VectorStore",
    "RAGConfig",
    "QueryEngine",
    "RAGRecommendationGenerator",
    "KnowledgeBaseBuilder",
]

