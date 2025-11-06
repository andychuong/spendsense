"""Quick test to validate catalog changes are syntactically correct.

This test can be run without database dependencies to verify:
1. Catalog structure is valid
2. New items are properly formatted
3. No syntax errors introduced
"""

import sys
import os

# Add service to path
service_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if service_path not in sys.path:
    sys.path.insert(0, service_path)

def test_catalog_imports():
    """Test that catalog imports without errors"""
    print("Testing catalog imports...")
    try:
        from app.recommendations.catalog import (
            EDUCATION_CATALOG,
            PARTNER_OFFER_CATALOG,
            REGULATORY_DISCLAIMER,
        )
        print("✓ Catalog imports successfully")
        return True
    except Exception as e:
        print(f"✗ Catalog import failed: {e}")
        return False


def test_new_education_item():
    """Test that new education item (edu_015) exists and is valid"""
    print("\nTesting new education item (edu_015)...")
    try:
        from app.recommendations.catalog import EDUCATION_CATALOG
        
        edu_015 = None
        for item in EDUCATION_CATALOG:
            if item.get("id") == "edu_015":
                edu_015 = item
                break
        
        if not edu_015:
            print("✗ edu_015 not found in catalog")
            return False
        
        # Verify required fields
        required_fields = ["id", "title", "content", "persona_ids", "tags"]
        missing = [f for f in required_fields if f not in edu_015]
        if missing:
            print(f"✗ edu_015 missing fields: {missing}")
            return False
        
        # Verify it's assigned to Persona 5
        if 5 not in edu_015["persona_ids"]:
            print("✗ edu_015 not assigned to Persona 5")
            return False
        
        print(f"✓ edu_015 found and valid")
        print(f"  Title: {edu_015['title']}")
        print(f"  Persona IDs: {edu_015['persona_ids']}")
        print(f"  Content length: {len(edu_015['content'])} chars")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_new_partner_offer():
    """Test that new partner offer (offer_001b) exists and is valid"""
    print("\nTesting new partner offer (offer_001b)...")
    try:
        from app.recommendations.catalog import PARTNER_OFFER_CATALOG
        
        offer_001b = None
        for offer in PARTNER_OFFER_CATALOG:
            if offer.get("id") == "offer_001b":
                offer_001b = offer
                break
        
        if not offer_001b:
            print("✗ offer_001b not found in catalog")
            return False
        
        # Verify required fields
        required_fields = ["id", "title", "content", "persona_ids", "eligibility_requirements"]
        missing = [f for f in required_fields if f not in offer_001b]
        if missing:
            print(f"✗ offer_001b missing fields: {missing}")
            return False
        
        # Verify it's assigned to Persona 1
        if 1 not in offer_001b["persona_ids"]:
            print("✗ offer_001b not assigned to Persona 1")
            return False
        
        # Verify eligibility requirements structure
        eligibility = offer_001b["eligibility_requirements"]
        if not isinstance(eligibility, dict):
            print("✗ eligibility_requirements is not a dictionary")
            return False
        
        print(f"✓ offer_001b found and valid")
        print(f"  Title: {offer_001b['title']}")
        print(f"  Persona IDs: {offer_001b['persona_ids']}")
        print(f"  Eligibility: min_credit_score={eligibility.get('min_credit_score')}, min_income={eligibility.get('min_income')}")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_persona_counts():
    """Test that each persona has adequate recommendations"""
    print("\nTesting persona recommendation counts...")
    try:
        from app.recommendations.catalog import EDUCATION_CATALOG, PARTNER_OFFER_CATALOG
        
        persona_edu_counts = {}
        persona_offer_counts = {}
        
        for item in EDUCATION_CATALOG:
            for persona_id in item["persona_ids"]:
                persona_edu_counts[persona_id] = persona_edu_counts.get(persona_id, 0) + 1
        
        for offer in PARTNER_OFFER_CATALOG:
            for persona_id in offer["persona_ids"]:
                persona_offer_counts[persona_id] = persona_offer_counts.get(persona_id, 0) + 1
        
        all_valid = True
        for persona_id in range(1, 6):
            edu_count = persona_edu_counts.get(persona_id, 0)
            offer_count = persona_offer_counts.get(persona_id, 0)
            
            print(f"  Persona {persona_id}: {edu_count} education items, {offer_count} partner offers")
            
            if edu_count < 3:
                print(f"    ⚠ Persona {persona_id} needs more education items (has {edu_count}, need ≥3)")
                all_valid = False
            else:
                print(f"    ✓ Has enough education items")
            
            if offer_count < 1:
                print(f"    ⚠ Persona {persona_id} needs partner offers (has {offer_count}, need ≥1)")
                all_valid = False
            else:
                print(f"    ✓ Has partner offers")
        
        return all_valid
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_rationale_syntax():
    """Test that rationale.py syntax is valid"""
    print("\nTesting rationale.py syntax...")
    try:
        # Try to compile the file
        rationale_path = os.path.join(os.path.dirname(__file__), "rationale.py")
        if not os.path.exists(rationale_path):
            print(f"  ⚠ File not found: rationale.py")
            return True  # Skip if file not found in test environment
        
        with open(rationale_path, 'r') as f:
            code = f.read()
        
        compile(code, rationale_path, 'exec')
        print("✓ rationale.py syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"✗ Syntax error in rationale.py: {e}")
        if hasattr(e, 'lineno') and hasattr(e, 'text'):
            print(f"  Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_guardrails_syntax():
    """Test that guardrails files have valid syntax"""
    print("\nTesting guardrails syntax...")
    try:
        # Try to find guardrails directory (could be in different locations)
        current_dir = os.path.dirname(__file__)
        possible_paths = [
            os.path.join(current_dir, "../../common"),
            os.path.join(current_dir, "../common"),
            os.path.join(os.path.dirname(current_dir), "app/common"),
        ]
        
        guardrails_dir = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                guardrails_dir = abs_path
                break
        
        if not guardrails_dir:
            print("  ⚠ Guardrails directory not found, skipping syntax check")
            return True  # Skip if not found in test environment
        
        files_to_check = [
            "tone_validation_guardrails.py",
            "eligibility_guardrails.py",
        ]
        
        all_valid = True
        for filename in files_to_check:
            filepath = os.path.join(guardrails_dir, filename)
            if not os.path.exists(filepath):
                print(f"  ⚠ File not found: {filename}")
                continue
            
            with open(filepath, 'r') as f:
                code = f.read()
            
            try:
                compile(code, filepath, 'exec')
                print(f"  ✓ {filename} syntax is valid")
            except SyntaxError as e:
                print(f"  ✗ Syntax error in {filename}: {e}")
                if hasattr(e, 'lineno') and hasattr(e, 'text'):
                    print(f"    Line {e.lineno}: {e.text}")
                all_valid = False
        
        return all_valid
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("CATALOG CHANGES VALIDATION TEST")
    print("=" * 60)
    
    tests = [
        ("Catalog Imports", test_catalog_imports),
        ("New Education Item", test_new_education_item),
        ("New Partner Offer", test_new_partner_offer),
        ("Persona Counts", test_persona_counts),
        ("Rationale Syntax", test_rationale_syntax),
        ("Guardrails Syntax", test_guardrails_syntax),
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
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

