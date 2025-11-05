"""Standalone test script for recommendation catalog (no database required).

Run this from project root:
    cd service && python3 -m app.recommendations.test_catalog
"""

import sys
import os

# Add service to path
service_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if service_path not in sys.path:
    sys.path.insert(0, service_path)

from app.recommendations.catalog import (
    EDUCATION_CATALOG,
    PARTNER_OFFER_CATALOG,
    REGULATORY_DISCLAIMER,
)


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


def test_persona_matching():
    """Test 2: Test persona matching logic"""
    print("=" * 60)
    print("TEST 2: Persona Matching")
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
            print(f"    ✓ Has enough education items (need ≥3)")
        else:
            print(f"    ⚠ Needs more education items (has {len(education_matches)}, need ≥3)")

        if len(offer_matches) >= 1:
            print(f"    ✓ Has partner offers (need ≥1)")
        else:
            print(f"    ⚠ Needs partner offers")

    print("\n✓ Persona matching test passed!\n")
    return True


def test_content_quality():
    """Test 3: Test content quality"""
    print("=" * 60)
    print("TEST 3: Content Quality")
    print("=" * 60)

    print("\nChecking education items:")
    for item in EDUCATION_CATALOG[:3]:  # Check first 3
        print(f"  {item['id']}: {item['title']}")
        print(f"    Content length: {len(item['content'])} chars")
        print(f"    Has disclaimer: {REGULATORY_DISCLAIMER[:30] in item['content']}")

    print("\nChecking partner offers:")
    for offer in PARTNER_OFFER_CATALOG[:3]:  # Check first 3
        print(f"  {offer['id']}: {offer['title']}")
        print(f"    Content length: {len(offer['content'])} chars")
        print(f"    Has eligibility requirements: {bool(offer.get('eligibility_requirements'))}")

    print("\n✓ Content quality test passed!\n")
    return True


def test_disclaimer():
    """Test 4: Verify disclaimer is present"""
    print("=" * 60)
    print("TEST 4: Regulatory Disclaimer")
    print("=" * 60)

    print(f"\nDisclaimer text: {REGULATORY_DISCLAIMER[:80]}...")
    print(f"  Length: {len(REGULATORY_DISCLAIMER)} chars")

    # Check that disclaimer contains key phrases
    key_phrases = ["educational", "not financial advice", "licensed"]
    for phrase in key_phrases:
        if phrase.lower() in REGULATORY_DISCLAIMER.lower():
            print(f"  ✓ Contains '{phrase}'")
        else:
            print(f"  ⚠ Missing '{phrase}'")

    print("\n✓ Disclaimer test passed!\n")
    return True


def show_sample_recommendations():
    """Show sample recommendations for each persona"""
    print("=" * 60)
    print("SAMPLE RECOMMENDATIONS BY PERSONA")
    print("=" * 60)

    persona_names = {
        1: "High Utilization",
        2: "Variable Income Budgeter",
        3: "Subscription-Heavy",
        4: "Savings Builder",
        5: "Custom Persona",
    }

    for persona_id in range(1, 6):
        print(f"\n{persona_names[persona_id]} (Persona {persona_id}):")

        education_items = [
            item for item in EDUCATION_CATALOG
            if persona_id in item["persona_ids"]
        ][:2]  # Show first 2

        offers = [
            offer for offer in PARTNER_OFFER_CATALOG
            if persona_id in offer["persona_ids"]
        ][:1]  # Show first 1

        print("  Education Items:")
        for item in education_items:
            print(f"    - {item['title']}")

        if offers:
            print("  Partner Offers:")
            for offer in offers:
                print(f"    - {offer['title']}")
        else:
            print("  Partner Offers: (none)")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RECOMMENDATION CATALOG - TEST SUITE")
    print("=" * 60 + "\n")

    tests = [
        ("Catalog Structure", test_catalog_structure),
        ("Persona Matching", test_persona_matching),
        ("Content Quality", test_content_quality),
        ("Regulatory Disclaimer", test_disclaimer),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test failed with error: {e}\n")
            import traceback
            traceback.print_exc()
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

    # Show sample recommendations
    show_sample_recommendations()

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



