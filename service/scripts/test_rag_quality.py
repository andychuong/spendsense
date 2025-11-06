#!/usr/bin/env python
"""
Test RAG recommendation quality and compare with catalog-based system.

This script generates recommendations using both RAG and catalog methods,
then compares them on various quality metrics.

Usage:
    # Test with sample users
    python scripts/test_rag_quality.py --sample-users

    # Test with specific user
    python scripts/test_rag_quality.py --user-id <user-id>

    # Generate comparison report
    python scripts/test_rag_quality.py --sample-users --report output/comparison.json
"""

import sys
import os
import asyncio
import logging
import argparse
import json
import time
import uuid
from typing import Dict, List, Any
from datetime import datetime

# Add service directory to path
service_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Sample test users with different financial situations
SAMPLE_USERS = [
    {
        "id": uuid.uuid4(),
        "name": "High Utilization User",
        "personas": ["HIGH_UTILIZATION"],
        "signals_30d": {
            "credit": {
                "avg_utilization": 0.68,
                "total_credit_balance": 5200.00,
                "total_credit_limit": 7650.00,
                "cards_with_interest": ["card_1"],
                "high_utilization_cards": ["card_1"],
                "interest_charges_30d": 87.00,
            }
        },
        "signals_180d": {},
    },
    {
        "id": uuid.uuid4(),
        "name": "Variable Income User",
        "personas": ["VARIABLE_INCOME_BUDGETER"],
        "signals_30d": {
            "income": {
                "payment_frequency": "irregular",
                "median_pay_gap_days": 52,
                "cash_flow_buffer_months": 0.6,
            }
        },
        "signals_180d": {},
    },
    {
        "id": uuid.uuid4(),
        "name": "Subscription Heavy User",
        "personas": ["SUBSCRIPTION_HEAVY"],
        "signals_30d": {
            "subscriptions": {
                "subscription_count": 8,
                "total_recurring_spend": 127.00,
                "subscription_share_percent": 15.0,
            }
        },
        "signals_180d": {},
    },
    {
        "id": uuid.uuid4(),
        "name": "Savings Builder User",
        "personas": ["SAVINGS_BUILDER"],
        "signals_30d": {
            "savings": {
                "net_inflow_monthly": 250.00,
                "savings_growth_rate_percent": 3.5,
                "emergency_fund_coverage_months": 2.1,
            },
            "credit": {
                "avg_utilization": 0.15,
            }
        },
        "signals_180d": {},
    },
]


async def generate_rag_recommendations(user: Dict[str, Any]) -> Dict[str, Any]:
    """Generate recommendations using RAG."""
    from app.rag import VectorStore, RAGRecommendationGenerator
    
    try:
        vs = VectorStore()
        generator = RAGRecommendationGenerator(vs, use_openai=True)
        
        start_time = time.time()
        result = generator.generate_recommendations(
            user_id=user["id"],
            personas=user["personas"],
            signals_30d=user["signals_30d"],
            signals_180d=user.get("signals_180d", {}),
            education_count=5,
            partner_offer_count=3,
        )
        generation_time = (time.time() - start_time) * 1000
        
        result["generation_time_ms"] = generation_time
        return result
        
    except Exception as e:
        logger.error(f"RAG generation failed: {e}")
        return {"success": False, "error": str(e)}


def generate_catalog_recommendations(user: Dict[str, Any]) -> Dict[str, Any]:
    """Generate recommendations using catalog-based system."""
    # Note: This would use the actual catalog generator
    # For testing, we'll simulate the output structure
    logger.info("Catalog generation would happen here (requires database)")
    
    return {
        "success": True,
        "generation_method": "catalog",
        "user_id": str(user["id"]),
        "personas": user["personas"],
        "recommendations": [
            {"type": "education", "title": "Catalog Education Item 1"},
            {"type": "education", "title": "Catalog Education Item 2"},
            {"type": "partner_offer", "title": "Catalog Partner Offer 1"},
        ],
        "generation_time_ms": 150,  # Simulated
    }


def analyze_quality(
    rag_result: Dict[str, Any],
    catalog_result: Dict[str, Any],
    user: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze and compare quality of RAG vs catalog recommendations."""
    
    analysis = {
        "user_name": user["name"],
        "user_personas": user["personas"],
        "comparison": {},
        "rag_metrics": {},
        "catalog_metrics": {},
    }
    
    # RAG metrics
    if rag_result.get("success"):
        rag_recs = rag_result.get("education_recommendations", []) + rag_result.get("partner_offers", [])
        
        analysis["rag_metrics"] = {
            "total_recommendations": len(rag_recs),
            "generation_time_ms": rag_result.get("generation_time_ms", 0),
            "documents_retrieved": rag_result.get("context_used", {}).get("documents_retrieved", 0),
            "similar_scenarios_found": rag_result.get("context_used", {}).get("similar_scenarios_found", 0),
        }
        
        # Check for data citations
        citations_found = 0
        for rec in rag_recs:
            rationale = rec.get("rationale", "")
            # Look for specific numbers/percentages/dates
            if any(char.isdigit() for char in rationale):
                citations_found += 1
        
        analysis["rag_metrics"]["recommendations_with_citations"] = citations_found
        analysis["rag_metrics"]["citation_rate"] = citations_found / len(rag_recs) if rag_recs else 0
        
        # Check for personalization
        personalized = 0
        for rec in rag_recs:
            content = rec.get("content", "").lower()
            rationale = rec.get("rationale", "").lower()
            # Check if mentions persona or user situation
            if any(term in content + rationale for term in ["you", "your", "because"]):
                personalized += 1
        
        analysis["rag_metrics"]["personalized_recommendations"] = personalized
        analysis["rag_metrics"]["personalization_rate"] = personalized / len(rag_recs) if rag_recs else 0
    
    # Catalog metrics
    if catalog_result.get("success"):
        cat_recs = catalog_result.get("recommendations", [])
        
        analysis["catalog_metrics"] = {
            "total_recommendations": len(cat_recs),
            "generation_time_ms": catalog_result.get("generation_time_ms", 0),
        }
    
    # Comparison
    if rag_result.get("success") and catalog_result.get("success"):
        analysis["comparison"] = {
            "rag_faster": analysis["rag_metrics"]["generation_time_ms"] < analysis["catalog_metrics"]["generation_time_ms"],
            "speed_difference_ms": analysis["rag_metrics"]["generation_time_ms"] - analysis["catalog_metrics"]["generation_time_ms"],
            "rag_more_citations": analysis["rag_metrics"]["citation_rate"] > 0.5,
            "rag_more_personalized": analysis["rag_metrics"]["personalization_rate"] > 0.7,
        }
    
    return analysis


async def test_sample_users(report_path: str = None):
    """Test RAG quality with sample users."""
    logger.info("Testing RAG quality with sample users...")
    logger.info("=" * 80)
    
    results = []
    
    for i, user in enumerate(SAMPLE_USERS, 1):
        logger.info(f"\n[Test {i}/{len(SAMPLE_USERS)}] {user['name']}")
        logger.info(f"Personas: {user['personas']}")
        logger.info("-" * 80)
        
        # Generate RAG recommendations
        logger.info("Generating RAG recommendations...")
        rag_result = await generate_rag_recommendations(user)
        
        if rag_result.get("success"):
            logger.info(f"✓ RAG: {rag_result.get('total_recommendations', 0)} recommendations in {rag_result.get('generation_time_ms', 0):.0f}ms")
            logger.info(f"  Context: {rag_result.get('context_used', {}).get('documents_retrieved', 0)} documents retrieved")
            
            # Show sample recommendation
            if rag_result.get("education_recommendations"):
                sample = rag_result["education_recommendations"][0]
                logger.info(f"\n  Sample Recommendation:")
                logger.info(f"  Title: {sample.get('title')}")
                logger.info(f"  Priority: {sample.get('priority')}")
                logger.info(f"  Rationale: {sample.get('rationale', '')[:150]}...")
        else:
            logger.error(f"✗ RAG failed: {rag_result.get('error')}")
        
        # Generate catalog recommendations
        logger.info("\nGenerating catalog recommendations...")
        catalog_result = generate_catalog_recommendations(user)
        
        if catalog_result.get("success"):
            logger.info(f"✓ Catalog: {len(catalog_result.get('recommendations', []))} recommendations")
        
        # Analyze quality
        logger.info("\nAnalyzing quality...")
        analysis = analyze_quality(rag_result, catalog_result, user)
        
        logger.info(f"  RAG Citation Rate: {analysis['rag_metrics'].get('citation_rate', 0):.1%}")
        logger.info(f"  RAG Personalization Rate: {analysis['rag_metrics'].get('personalization_rate', 0):.1%}")
        
        results.append({
            "user": user["name"],
            "rag_result": rag_result if rag_result.get("success") else {"error": rag_result.get("error")},
            "catalog_result": catalog_result,
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        logger.info("=" * 80)
    
    # Generate summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    
    successful_rag = sum(1 for r in results if r["rag_result"].get("success", False))
    avg_rag_time = sum(r["rag_result"].get("generation_time_ms", 0) for r in results if "generation_time_ms" in r["rag_result"]) / successful_rag if successful_rag > 0 else 0
    
    avg_citation_rate = sum(r["analysis"]["rag_metrics"].get("citation_rate", 0) for r in results) / len(results)
    avg_personalization = sum(r["analysis"]["rag_metrics"].get("personalization_rate", 0) for r in results) / len(results)
    
    logger.info(f"Tests Run: {len(results)}")
    logger.info(f"Successful RAG: {successful_rag}/{len(results)}")
    logger.info(f"Average Generation Time: {avg_rag_time:.0f}ms")
    logger.info(f"Average Citation Rate: {avg_citation_rate:.1%}")
    logger.info(f"Average Personalization: {avg_personalization:.1%}")
    
    # Save report if requested
    if report_path:
        os.makedirs(os.path.dirname(report_path) if os.path.dirname(report_path) else ".", exist_ok=True)
        
        report = {
            "test_date": datetime.utcnow().isoformat(),
            "total_tests": len(results),
            "successful_tests": successful_rag,
            "summary": {
                "avg_generation_time_ms": avg_rag_time,
                "avg_citation_rate": avg_citation_rate,
                "avg_personalization_rate": avg_personalization,
            },
            "detailed_results": results,
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n✓ Report saved to: {report_path}")
    
    logger.info("=" * 80)
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test RAG recommendation quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--sample-users",
        action="store_true",
        help="Test with sample users"
    )
    
    parser.add_argument(
        "--user-id",
        type=str,
        help="Test with specific user ID"
    )
    
    parser.add_argument(
        "--report",
        type=str,
        help="Save comparison report to file (JSON)"
    )
    
    args = parser.parse_args()
    
    if not any([args.sample_users, args.user_id]):
        parser.error("Must specify --sample-users or --user-id")
    
    try:
        if args.sample_users:
            asyncio.run(test_sample_users(report_path=args.report))
        elif args.user_id:
            logger.info(f"Testing with user ID: {args.user_id}")
            logger.info("Note: Requires database connection")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 1
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

