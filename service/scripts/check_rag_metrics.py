#!/usr/bin/env python
"""Check RAG system metrics and health."""

import sys
import os

# Add service directory to path
service_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

import logging
import argparse
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_vector_store_health():
    """Check vector store health."""
    try:
        from app.rag import VectorStore
        
        vs = VectorStore()
        stats = vs.get_stats()
        
        logger.info("=" * 60)
        logger.info("VECTOR STORE HEALTH")
        logger.info("=" * 60)
        logger.info(f"Status: ✓ Healthy")
        logger.info(f"Total Documents: {stats['total_documents']}")
        logger.info(f"Embedding Model: {stats['embedding_model']}")
        logger.info(f"Embedding Dimensions: {stats['embedding_dimensions']}")
        
        if stats['total_documents'] < 10:
            logger.warning("⚠ Low document count - knowledge base may need rebuilding")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Vector store unhealthy: {e}")
        return False


def check_generation_metrics():
    """Check generation metrics."""
    try:
        from app.eval import get_metrics_collector
        
        metrics = get_metrics_collector()
        
        rag_metrics = metrics.get_generation_metrics(method="rag")
        catalog_metrics = metrics.get_generation_metrics(method="catalog")
        
        logger.info("\n" + "=" * 60)
        logger.info("GENERATION METRICS")
        logger.info("=" * 60)
        
        if rag_metrics["sample_size"] > 0:
            logger.info(f"\nRAG:")
            logger.info(f"  Sample Size: {rag_metrics['sample_size']}")
            logger.info(f"  Success Rate: {rag_metrics['success_rate']:.1%}")
            logger.info(f"  Avg Generation Time: {rag_metrics['avg_generation_time_ms']:.0f}ms")
            logger.info(f"  Avg Recommendations: {rag_metrics['avg_recommendation_count']:.1f}")
            
            if "avg_citation_rate" in rag_metrics:
                logger.info(f"  Citation Rate: {rag_metrics['avg_citation_rate']:.1%}")
            
            # Check alerts
            if rag_metrics['success_rate'] < 0.90:
                logger.warning(f"  ⚠ ALERT: Success rate below 90%")
            if rag_metrics['avg_generation_time_ms'] > 7000:
                logger.warning(f"  ⚠ ALERT: Generation time above 7s")
        else:
            logger.info("\nRAG: No data yet")
        
        if catalog_metrics["sample_size"] > 0:
            logger.info(f"\nCATALOG:")
            logger.info(f"  Sample Size: {catalog_metrics['sample_size']}")
            logger.info(f"  Success Rate: {catalog_metrics['success_rate']:.1%}")
            logger.info(f"  Avg Generation Time: {catalog_metrics['avg_generation_time_ms']:.0f}ms")
        else:
            logger.info("\nCATALOG: No data yet")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to check generation metrics: {e}")
        return False


def check_ab_test_status():
    """Check A/B test status."""
    try:
        from app.eval import create_ab_tester
        
        ab_tester = create_ab_tester(rollout_percentage=0.10, enabled=True)
        
        logger.info("\n" + "=" * 60)
        logger.info("A/B TEST STATUS")
        logger.info("=" * 60)
        
        if not ab_tester.is_enabled():
            logger.info("Status: Disabled")
            return True
        
        metrics = ab_tester.get_metrics()
        
        logger.info(f"Status: ✓ Enabled")
        logger.info(f"Rollout: {ab_tester.config.rollout_percentage:.0%}")
        
        for variant, stats in metrics.items():
            if variant == "comparison":
                continue
            
            method = ab_tester.config.variants.get(variant, variant)
            logger.info(f"\n{variant.upper()} ({method}):")
            logger.info(f"  Sample Size: {stats['sample_size']}")
            logger.info(f"  Success Rate: {stats['success_rate']:.1%}")
            logger.info(f"  Avg Time: {stats['avg_generation_time_ms']:.0f}ms")
            
            if stats.get('avg_rating'):
                logger.info(f"  Avg Rating: {stats['avg_rating']:.2f}/5.0")
        
        if "comparison" in metrics:
            comp = metrics["comparison"]
            logger.info(f"\nCOMPARISON:")
            logger.info(f"  Statistically Significant: {comp['statistically_significant']}")
            
            if not comp['statistically_significant']:
                logger.info(f"  ⚠ Need more data for statistical significance")
        
        # Recommendation
        recommendation = ab_tester.get_recommendation()
        logger.info(f"\nRECOMMENDATION: {recommendation}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to check A/B test: {e}")
        return False


def check_openai_quota():
    """Check OpenAI API quota/status."""
    import os
    
    logger.info("\n" + "=" * 60)
    logger.info("OPENAI API STATUS")
    logger.info("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("⚠ OPENAI_API_KEY not set")
        return False
    
    logger.info("✓ API key configured")
    logger.info("  Note: Check https://platform.openai.com/usage for quota")
    
    return True


def main():
    """Run all health checks."""
    parser = argparse.ArgumentParser(description="Check RAG system health")
    parser.add_argument("--vector-store", action="store_true", help="Check vector store only")
    parser.add_argument("--metrics", action="store_true", help="Check metrics only")
    parser.add_argument("--ab-test", action="store_true", help="Check A/B test only")
    parser.add_argument("--all", action="store_true", default=True, help="Check all (default)")
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info(f"RAG SYSTEM HEALTH CHECK - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("=" * 60)
    
    checks = []
    
    if args.vector_store or args.all:
        checks.append(("Vector Store", check_vector_store_health))
    
    if args.metrics or args.all:
        checks.append(("Generation Metrics", check_generation_metrics))
    
    if args.ab_test or args.all:
        checks.append(("A/B Test", check_ab_test_status))
    
    if args.all:
        checks.append(("OpenAI API", check_openai_quota))
    
    # Run checks
    results = []
    for name, check_func in checks:
        try:
            success = check_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"✗ {name} check failed: {e}")
            results.append((name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status:8} | {name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    logger.info("-" * 60)
    logger.info(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("✓ RAG system healthy")
        return 0
    else:
        logger.warning("⚠ Some checks failed - review above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

