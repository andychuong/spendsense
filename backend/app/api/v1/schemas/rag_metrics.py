"""Schemas for RAG metrics and A/B test results."""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class VectorStoreStats(BaseModel):
    """Vector store statistics."""
    total_documents: int = Field(..., description="Total documents in vector store")
    embedding_model: str = Field(..., description="Embedding model name")
    embedding_dimensions: int = Field(..., description="Embedding dimensions")
    document_types: Dict[str, int] = Field(default_factory=dict, description="Document counts by type")


class GenerationMetrics(BaseModel):
    """Generation performance metrics."""
    sample_size: int = Field(..., description="Number of generations")
    successful_generations: int = Field(..., description="Number of successful generations")
    success_rate: float = Field(..., description="Success rate (0.0-1.0)")
    avg_generation_time_ms: float = Field(..., description="Average generation time in milliseconds")
    avg_recommendation_count: float = Field(..., description="Average number of recommendations")
    avg_citation_rate: Optional[float] = Field(None, description="Average citation rate (RAG only)")


class ABTestMetrics(BaseModel):
    """A/B test metrics."""
    variant: str = Field(..., description="Variant name (control or variant_a)")
    method: str = Field(..., description="Generation method (catalog or rag)")
    sample_size: int = Field(..., description="Number of users in variant")
    success_rate: float = Field(..., description="Success rate")
    avg_generation_time_ms: float = Field(..., description="Average generation time")
    avg_rating: Optional[float] = Field(None, description="Average user rating")
    helpful_rate: Optional[float] = Field(None, description="Rate of helpful votes")


class ABTestComparison(BaseModel):
    """A/B test comparison results."""
    variant_faster: bool = Field(..., description="Whether variant is faster than control")
    speed_improvement: float = Field(..., description="Speed improvement percentage")
    rating_improvement: float = Field(..., description="Rating improvement (points)")
    helpful_rate_improvement: float = Field(..., description="Helpful rate improvement")
    statistically_significant: bool = Field(..., description="Whether results are statistically significant")


class ABTestStatus(BaseModel):
    """A/B test status and results."""
    enabled: bool = Field(..., description="Whether A/B test is enabled")
    rollout_percentage: float = Field(..., description="Percentage of users in test")
    control: ABTestMetrics = Field(..., description="Control variant metrics")
    variant_a: ABTestMetrics = Field(..., description="Variant A metrics")
    comparison: ABTestComparison = Field(..., description="Comparison results")
    recommendation: str = Field(..., description="Rollout recommendation")


class RAGHealthCheck(BaseModel):
    """RAG system health check."""
    vector_store_healthy: bool = Field(..., description="Whether vector store is healthy")
    vector_store_stats: Optional[VectorStoreStats] = Field(None, description="Vector store statistics")
    rag_enabled: bool = Field(..., description="Whether RAG is enabled")
    rag_rollout_percentage: float = Field(..., description="RAG rollout percentage")
    openai_configured: bool = Field(..., description="Whether OpenAI API key is configured")
    last_check: datetime = Field(..., description="Last health check timestamp")


class RAGDashboard(BaseModel):
    """Complete RAG dashboard data."""
    health: RAGHealthCheck = Field(..., description="Health check results")
    rag_metrics: Optional[GenerationMetrics] = Field(None, description="RAG generation metrics")
    catalog_metrics: Optional[GenerationMetrics] = Field(None, description="Catalog generation metrics")
    ab_test_status: Optional[ABTestStatus] = Field(None, description="A/B test status")

