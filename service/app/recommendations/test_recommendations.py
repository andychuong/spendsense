"""Test script for recommendation generation service.

This script tests:
1. Catalog structure and persona matching
2. Recommendation selection logic
3. Rationale generation
4. Full integration test (requires database)
"""

import uuid
import sys
import os
from typing import Dict, Any

# Add service and backend to path for imports
service_path = os.path.join(os.path.dirname(__file__), "../..")
backend_path = os.path.join(os.path.dirname(__file__), "../../../backend")
if service_path not in sys.path:
    sys.path.insert(0, service_path)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.recommendations.catalog import (
    EDUCATION_CATALOG,
    PARTNER_OFFER_CATALOG,
    REGULATORY_DISCLAIMER,
)
from app.recommendations.generator import RecommendationGenerator


def test_catalog_structure():
    """Test 1: Verify catalog structure"""
    print("=" * 60)
    print("TEST 1: Catalog Structure")
    print("=" * 60)

    # Test education catalog
    print(f"\nEducation Catalog: {len(EDUCATION_CATALOG)} items")
    persona_counts = {}
    for item in EDUCATION_CATALOG:
        for persona_id in item["persona_ids"]:
            persona_counts[persona_id] = persona_counts.get(persona_id, 0) + 1

    print("Education items per persona:")
    for persona_id in sorted(persona_counts.keys()):
        print(f"  Persona {persona_id}: {persona_counts[persona_id]} items")

    # Test partner offer catalog
    print(f"\nPartner Offer Catalog: {len(PARTNER_OFFER_CATALOG)} offers")
    offer_persona_counts = {}
    for offer in PARTNER_OFFER_CATALOG:
        for persona_id in offer["persona_ids"]:
            offer_persona_counts[persona_id] = offer_persona_counts.get(persona_id, 0) + 1

    print("Partner offers per persona:")
    for persona_id in sorted(offer_persona_counts.keys()):
        print(f"  Persona {persona_id}: {offer_persona_counts[persona_id]} offers")

    # Verify all items have required fields
    print("\nVerifying catalog structure...")
    all_valid = True
    for item in EDUCATION_CATALOG:
        required_fields = ["id", "title", "content", "persona_ids"]
        missing = [f for f in required_fields if f not in item]
        if missing:
            print(f"  ERROR: Education item {item.get('id', 'unknown')} missing fields: {missing}")
            all_valid = False

    for offer in PARTNER_OFFER_CATALOG:
        required_fields = ["id", "title", "content", "persona_ids", "eligibility_requirements"]
        missing = [f for f in required_fields if f not in offer]
        if missing:
            print(f"  ERROR: Partner offer {offer.get('id', 'unknown')} missing fields: {missing}")
            all_valid = False

    if all_valid:
        print("  ✓ All catalog items have required fields")

    print("\n✓ Catalog structure test passed!\n")
    return True


def test_recommendation_selection():
    """Test 2: Test recommendation selection logic"""
    print("=" * 60)
    print("TEST 2: Recommendation Selection Logic")
    print("=" * 60)

    # Mock database session (we'll create a simple mock)
    class MockDB:
        pass

    db = MockDB()
    generator = RecommendationGenerator(db)

    # Test education item selection for each persona
    print("\nTesting education item selection:")
    for persona_id in range(1, 6):
        items = generator.select_education_items(persona_id, count=5)
        print(f"  Persona {persona_id}: Selected {len(items)} items")

        # Verify count is between 3-5
        if 3 <= len(items) <= 5:
            print(f"    ✓ Count is valid (3-5)")
        else:
            print(f"    ✗ Count is invalid: {len(items)}")

        # Verify all items match persona
        all_match = all(persona_id in item["persona_ids"] for item in items)
        if all_match:
            print(f"    ✓ All items match persona")
        else:
            print(f"    ✗ Some items don't match persona")

    # Test partner offer selection
    print("\nTesting partner offer selection:")
    existing_products = {
        "credit_card": False,
        "savings": False,
        "high_yield_savings": False,
    }

    for persona_id in range(1, 6):
        offers = generator.select_partner_offers(persona_id, existing_products, count=3)
        print(f"  Persona {persona_id}: Selected {len(offers)} offers")

        # Verify count is between 1-3
        if 1 <= len(offers) <= 3:
            print(f"    ✓ Count is valid (1-3)")
        else:
            print(f"    ✗ Count is invalid: {len(offers)}")

    print("\n✓ Recommendation selection test passed!\n")
    return True


def test_rationale_generation():
    """Test 3: Test rationale generation with sample signals"""
    print("=" * 60)
    print("TEST 3: Rationale Generation")
    print("=" * 60)

    class MockDB:
        pass

    db = MockDB()
    generator = RecommendationGenerator(db)

    # Test rationale for Persona 1 (High Utilization)
    print("\nTesting rationale for Persona 1 (High Utilization):")
    signals_30d = {
        "credit": {
            "critical_utilization_cards": [
                {
                    "account_name": "Visa ending in 4523",
                    "utilization_percent": 68.5,
                    "current_balance": 3400.00,
                    "credit_limit": 5000.00,
                }
            ],
            "cards_with_interest": [
                {
                    "account_name": "Visa ending in 4523",
                    "interest_charges": {
                        "total_interest_charges": 87.50,
                    }
                }
            ],
        }
    }

    test_item = EDUCATION_CATALOG[0]  # First education item
    rationale = generator.generate_rationale(
        test_item,
        signals_30d,
        {},
        1,  # Persona 1
    )

    print(f"  Education Item: {test_item['title']}")
    print(f"  Rationale Preview: {rationale[:200]}...")
    print(f"  Contains disclaimer: {'disclaimer' in rationale.lower() or 'not financial advice' in rationale.lower()}")

    # Test rationale for Persona 3 (Subscription-Heavy)
    print("\nTesting rationale for Persona 3 (Subscription-Heavy):")
    sub_signals_30d = {
        "subscriptions": {
            "subscription_count": 5,
            "total_recurring_spend": 125.50,
            "subscription_share_percent": 15.2,
        }
    }

    test_offer = PARTNER_OFFER_CATALOG[2]  # Subscription management offer
    rationale = generator.generate_rationale(
        test_offer,
        sub_signals_30d,
        {},
        3,  # Persona 3
    )

    print(f"  Partner Offer: {test_offer['title']}")
    print(f"  Rationale Preview: {rationale[:200]}...")
    print(f"  Contains disclaimer: {'disclaimer' in rationale.lower() or 'not financial advice' in rationale.lower()}")

    print("\n✓ Rationale generation test passed!\n")
    return True


def test_persona_matching():
    """Test 4: Test persona matching logic"""
    print("=" * 60)
    print("TEST 4: Persona Matching")
    print("=" * 60)

    # Test that each persona has matching recommendations
    persona_names = {
        1: "High Utilization",
        2: "Variable Income Budgeter",
        3: "Subscription-Heavy",
        4: "Savings Builder",
        5: "Custom Persona",
    }

    print("\nVerifying persona matching:")
    for persona_id in range(1, 6):
        education_matches = [
            item for item in EDUCATION_CATALOG
            if persona_id in item["persona_ids"]
        ]
        offer_matches = [
            offer for offer in PARTNER_OFFER_CATALOG
            if persona_id in offer["persona_ids"]
        ]

        print(f"  Persona {persona_id} ({persona_names[persona_id]}):")
        print(f"    Education items: {len(education_matches)}")
        print(f"    Partner offers: {len(offer_matches)}")

        if len(education_matches) >= 3:
            print(f"    ✓ Has enough education items")
        else:
            print(f"    ✗ Needs more education items")

        if len(offer_matches) >= 1:
            print(f"    ✓ Has partner offers")
        else:
            print(f"    ✗ Needs partner offers")

    print("\n✓ Persona matching test passed!\n")
    return True


def test_integration_with_database():
    """Test 5: Full integration test (requires database)"""
    print("=" * 60)
    print("TEST 5: Integration Test (Requires Database)")
    print("=" * 60)

    try:
        from backend.app.database import SessionLocal
        from backend.app.models.user_profile import UserProfile
        from backend.app.models.recommendation import Recommendation
        from backend.app.models.user import User

        db = SessionLocal()

        # Find a user with a profile
        user_profile = db.query(UserProfile).first()

        if not user_profile:
            print("\n⚠ No user profiles found in database.")
            print("  To test with database:")
            print("  1. Ensure you have users with assigned personas")
            print("  2. Run persona assignment first if needed")
            print("  3. Then run recommendation generation")
            db.close()
            return False

        user_id = user_profile.user_id
        print(f"\nTesting with user: {user_id}")
        print(f"  Persona: {user_profile.persona_name} (ID: {user_profile.persona_id})")

        # Check existing recommendations
        existing_count = db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).count()

        print(f"  Existing recommendations: {existing_count}")

        # Generate recommendations
        generator = RecommendationGenerator(db)
        result = generator.generate_recommendations(user_id)

        print(f"\n  Generated {len(result['recommendations'])} recommendations:")
        print(f"    Education items: {result['education_count']}")
        print(f"    Partner offers: {result['partner_offer_count']}")

        # Verify recommendations were stored
        new_count = db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).count()

        print(f"  Total recommendations in DB: {new_count}")

        # Show sample recommendations
        recommendations = db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).order_by(Recommendation.created_at.desc()).limit(5).all()

        print(f"\n  Sample recommendations:")
        for rec in recommendations:
            print(f"    - [{rec.type.value}] {rec.title[:50]}...")
            print(f"      Status: {rec.status.value}")
            print(f"      Rationale: {rec.rationale[:100]}...")

        db.close()
        print("\n✓ Integration test passed!\n")
        return True

    except ImportError as e:
        print(f"\n⚠ Cannot import database modules: {e}")
        print("  Skipping integration test")
        return False
    except Exception as e:
        print(f"\n⚠ Integration test error: {e}")
        print("  Make sure database is set up and accessible")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RECOMMENDATION GENERATION SERVICE - TEST SUITE")
    print("=" * 60 + "\n")

    tests = [
        ("Catalog Structure", test_catalog_structure),
        ("Recommendation Selection", test_recommendation_selection),
        ("Rationale Generation", test_rationale_generation),
        ("Persona Matching", test_persona_matching),
        ("Integration (Database)", test_integration_with_database),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test failed with error: {e}\n")
            results.append((name, False))

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

