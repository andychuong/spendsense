#!/usr/bin/env python
"""
Basic standalone tests for RAG system (no backend dependencies).

This script tests core RAG functionality without requiring database or backend models.

Usage:
    python scripts/test_rag_basic.py
"""

import sys
import os

# Add service directory to path
service_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_vector_store():
    """Test VectorStore initialization and basic operations."""
    logger.info("Testing VectorStore...")
    
    try:
        from app.rag.vector_store import VectorStore
        from app.rag.config import RAGConfig
        
        # Initialize
        config = RAGConfig(
            vector_db_path="./data/chroma_test_basic",
            collection_name="test_basic",
        )
        vs = VectorStore(config=config)
        logger.info("✓ VectorStore initialized")
        
        # Add documents
        docs = [
            {
                "id": "test_1",
                "content": "High credit card utilization requires debt reduction strategies",
                "type": "test",
            },
            {
                "id": "test_2",
                "content": "Variable income requires emergency fund and cash flow planning",
                "type": "test",
            }
        ]
        
        count = vs.add_documents(docs)
        logger.info(f"✓ Added {count} documents")
        
        # Search
        results = vs.search("credit card debt strategies", top_k=2)
        logger.info(f"✓ Search returned {len(results['ids'][0])} results")
        
        if results['ids'][0]:
            logger.info(f"  Top result: {results['ids'][0][0]}")
            logger.info(f"  Similarity: {results['distances'][0][0]:.3f}")
        
        # Stats
        stats = vs.get_stats()
        logger.info(f"✓ Stats: {stats['total_documents']} total documents")
        
        # Cleanup
        vs.clear()
        logger.info("✓ Cleanup complete")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ VectorStore test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_engine():
    """Test QueryEngine without backend dependencies."""
    logger.info("\nTesting QueryEngine...")
    
    try:
        from app.rag.vector_store import VectorStore
        from app.rag.config import RAGConfig
        from app.rag.query_engine import QueryEngine
        
        # Initialize
        config = RAGConfig(
            vector_db_path="./data/chroma_test_query",
            collection_name="test_query",
        )
        vs = VectorStore(config=config)
        
        # Add some test documents
        docs = [
            {
                "id": "debt_strategy",
                "content": "Debt avalanche method focuses on highest interest rate first",
                "type": "strategy",
                "category": "debt",
            },
            {
                "id": "emergency_fund",
                "content": "Emergency fund should cover 3-6 months of expenses",
                "type": "strategy",
                "category": "savings",
            }
        ]
        vs.add_documents(docs)
        
        # Create query engine
        query_engine = QueryEngine(vs)
        logger.info("✓ QueryEngine initialized")
        
        # Generate query
        query = query_engine.generate_query_from_profile(
            personas=["HIGH_UTILIZATION"],
            signals_30d={"credit": {"avg_utilization": 0.68}}
        )
        logger.info(f"✓ Generated query: {query[:80]}...")
        
        # Retrieve context
        context = query_engine.retrieve_context(query, top_k=2)
        logger.info(f"✓ Retrieved {context['retrieved_count']} documents")
        
        if context['documents']:
            logger.info(f"  Top doc: {context['documents'][0]['id']}")
        
        # Cleanup
        vs.clear()
        logger.info("✓ Cleanup complete")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ QueryEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_builder():
    """Test KnowledgeBaseBuilder with catalog data."""
    logger.info("\nTesting KnowledgeBaseBuilder...")
    
    try:
        from app.rag.vector_store import VectorStore
        from app.rag.config import RAGConfig
        from app.rag.knowledge_builder import KnowledgeBaseBuilder
        
        # Initialize
        config = RAGConfig(
            vector_db_path="./data/chroma_test_kb",
            collection_name="test_kb",
        )
        vs = VectorStore(config=config)
        
        # Create builder (without database)
        builder = KnowledgeBaseBuilder(None, vs)
        logger.info("✓ KnowledgeBaseBuilder initialized")
        
        # Test catalog ingestion (synchronous)
        import asyncio
        
        async def run_test():
            # Education content
            edu_count = await builder.ingest_education_content()
            logger.info(f"✓ Ingested {edu_count} education items")
            
            # Partner offers
            offer_count = await builder.ingest_partner_offers()
            logger.info(f"✓ Ingested {offer_count} partner offers")
            
            # Financial strategies
            strategy_count = await builder.ingest_financial_strategies()
            logger.info(f"✓ Ingested {strategy_count} financial strategies")
            
            # Total
            total = vs.count()
            logger.info(f"✓ Total documents in knowledge base: {total}")
            
            return total > 0
        
        result = asyncio.run(run_test())
        
        # Cleanup
        vs.clear()
        logger.info("✓ Cleanup complete")
        
        return result
        
    except Exception as e:
        logger.error(f"✗ KnowledgeBaseBuilder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompts():
    """Test prompt templates."""
    logger.info("\nTesting Prompts...")
    
    try:
        from app.rag.prompts import (
            get_system_prompt,
            get_education_recommendation_prompt,
            get_partner_offer_prompt,
        )
        
        # System prompt
        system_prompt = get_system_prompt()
        assert len(system_prompt) > 100
        assert "SpendSense" in system_prompt
        logger.info("✓ System prompt loaded")
        
        # Education prompt
        edu_prompt = get_education_recommendation_prompt(
            retrieved_context="Test context",
            user_personas=["HIGH_UTILIZATION"],
            user_signals={"credit": {"avg_utilization": 0.68}},
            count=3,
        )
        assert len(edu_prompt) > 100
        assert "HIGH_UTILIZATION" in edu_prompt
        logger.info("✓ Education prompt generated")
        
        # Partner offer prompt
        offer_prompt = get_partner_offer_prompt(
            retrieved_context="Test context",
            user_personas=["SAVINGS_BUILDER"],
            user_signals={"savings": {"net_inflow_monthly": 250}},
            count=2,
        )
        assert len(offer_prompt) > 100
        assert "SAVINGS_BUILDER" in offer_prompt
        logger.info("✓ Partner offer prompt generated")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Prompts test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ab_testing():
    """Test A/B testing framework."""
    logger.info("\nTesting A/B Testing Framework...")
    
    try:
        from app.eval.ab_testing import ABTester, ABTestConfig
        
        # Create config
        config = ABTestConfig(
            rollout_percentage=0.10,
            enabled=True,
        )
        
        ab_tester = ABTester(config=config)
        logger.info("✓ ABTester initialized")
        
        # Assign users
        user1_variant = ab_tester.assign_variant("user_1")
        user2_variant = ab_tester.assign_variant("user_2")
        logger.info(f"✓ User 1 assigned to: {user1_variant}")
        logger.info(f"✓ User 2 assigned to: {user2_variant}")
        
        # Consistent assignment
        user1_again = ab_tester.assign_variant("user_1")
        assert user1_variant == user1_again
        logger.info("✓ Consistent assignment verified")
        
        # Track metrics
        ab_tester.track_generation(
            "user_1",
            user1_variant,
            {"success": True, "generation_time_ms": 3200, "total_recommendations": 8}
        )
        logger.info("✓ Tracked generation metrics")
        
        # Get metrics
        metrics = ab_tester.get_metrics()
        logger.info(f"✓ Retrieved metrics: {len(metrics)} variants")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ A/B testing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_collector():
    """Test metrics collection."""
    logger.info("\nTesting Metrics Collector...")
    
    try:
        from app.eval.metrics import RecommendationMetrics
        
        metrics = RecommendationMetrics()
        logger.info("✓ RecommendationMetrics initialized")
        
        # Track generation
        metrics.track_generation(
            "user_1",
            "rag",
            {
                "success": True,
                "generation_time_ms": 3200,
                "total_recommendations": 8,
                "education_recommendations": [
                    {"title": "Test", "rationale": "User has 68% utilization"}
                ],
                "partner_offers": [],
                "context_used": {"documents_retrieved": 12},
            }
        )
        logger.info("✓ Tracked generation")
        
        # Track interaction
        metrics.track_user_interaction("user_1", "rec_1", "view")
        metrics.track_user_interaction("user_1", "rec_1", "click")
        logger.info("✓ Tracked interactions")
        
        # Get metrics
        gen_metrics = metrics.get_generation_metrics(method="rag")
        logger.info(f"✓ Generation metrics: {gen_metrics['sample_size']} samples")
        
        interaction_metrics = metrics.get_interaction_metrics()
        logger.info(f"✓ Interaction metrics: {interaction_metrics['total_interactions']} interactions")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Metrics collector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all basic tests."""
    logger.info("=" * 80)
    logger.info("RAG System - Basic Tests")
    logger.info("=" * 80)
    
    tests = [
        ("VectorStore", test_vector_store),
        ("QueryEngine", test_query_engine),
        ("KnowledgeBaseBuilder", test_knowledge_builder),
        ("Prompts", test_prompts),
        ("A/B Testing", test_ab_testing),
        ("Metrics Collector", test_metrics_collector),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"Test {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status:8} | {name}")
    
    logger.info("-" * 80)
    logger.info(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    logger.info("=" * 80)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

