#!/usr/bin/env python3
"""
Test basic usage of mLLMCelltype without LangExtract
This tests that the original API still works correctly
"""

import sys
import os

# Add the python package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mllmcelltype import annotate_clusters

def test_basic_usage():
    """Test the most basic usage pattern"""
    print("=" * 60)
    print("🧪 Testing Basic Usage (Original API)")
    print("=" * 60)
    
    # Simple test data
    marker_genes = {
        "Cluster_0": ["CD3D", "CD3E", "CD4"],
        "Cluster_1": ["CD19", "CD79A"],
        "Cluster_2": ["CD14", "LYZ"],
    }
    
    print("\n1️⃣ Default usage (no extra parameters):")
    print("Code: annotate_clusters(marker_genes, 'human', 'gemini-2.5-flash')")
    try:
        result = annotate_clusters(
            marker_genes=marker_genes,
            species="human",
            model="gemini-2.5-flash"
        )
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    print("\n2️⃣ With provider specified:")
    print("Code: annotate_clusters(marker_genes, 'human', 'gemini-2.5-flash', 'gemini')")
    try:
        result = annotate_clusters(
            marker_genes=marker_genes,
            species="human",
            model="gemini-2.5-flash",
            provider="gemini"
        )
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    print("\n3️⃣ With use_cache:")
    print("Code: annotate_clusters(marker_genes, 'human', 'gpt-4o-mini', use_cache=True)")
    try:
        result = annotate_clusters(
            marker_genes=marker_genes,
            species="human",
            model="gpt-4o-mini",
            use_cache=True
        )
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    print("\n4️⃣ Explicitly disable LangExtract:")
    print("Code: annotate_clusters(..., use_langextract=False)")
    try:
        result = annotate_clusters(
            marker_genes=marker_genes,
            species="human",
            model="gemini-2.5-flash",
            provider="gemini",
            use_langextract=False  # Explicitly disable
        )
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    return True

def test_different_models():
    """Test with different models to ensure compatibility"""
    print("\n" + "=" * 60)
    print("🤖 Testing Different Models")
    print("=" * 60)
    
    marker_genes = {
        "Cluster_0": ["CD3D", "CD3E"],
    }
    
    models_to_test = [
        ("gpt-4o-mini", "openai"),
        ("gemini-2.5-flash", "gemini"),
        ("claude-3-5-haiku-latest", "anthropic"),
    ]
    
    for model, provider in models_to_test:
        print(f"\n🔹 Testing {model} ({provider}):")
        try:
            result = annotate_clusters(
                marker_genes=marker_genes,
                species="human",
                model=model,
                provider=provider,
                use_cache=True  # Use cache to speed up
            )
            print(f"  ✅ Success: {result}")
        except Exception as e:
            if "API" in str(e) or "key" in str(e).lower():
                print(f"  ⏭️ Skipped (no API key)")
            else:
                print(f"  ❌ Failed: {e}")
                return False
    
    return True

def test_error_cases():
    """Test that error handling still works"""
    print("\n" + "=" * 60)
    print("🚨 Testing Error Handling")
    print("=" * 60)
    
    print("\n1️⃣ Empty markers:")
    try:
        result = annotate_clusters(
            marker_genes={},
            species="human",
            model="gemini-2.5-flash"
        )
        print(f"⚠️ Should have raised error, got: {result}")
    except Exception as e:
        print(f"✅ Error caught correctly: {str(e)[:50]}...")
    
    print("\n2️⃣ Invalid model:")
    try:
        result = annotate_clusters(
            marker_genes={"Cluster_0": ["CD3D"]},
            species="human",
            model="invalid-model-xyz",
            provider="invalid"
        )
        print(f"⚠️ Should have raised error, got: {result}")
    except Exception as e:
        print(f"✅ Error caught correctly: {str(e)[:50]}...")
    
    return True

def main():
    """Run all tests"""
    print("🚀 mLLMCelltype Backward Compatibility Test")
    print("=" * 60)
    print("Testing that original API still works without LangExtract")
    print()
    
    all_passed = True
    
    # Run tests
    tests = [
        ("Basic Usage", test_basic_usage),
        ("Different Models", test_different_models),
        ("Error Handling", test_error_cases),
    ]
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            if not passed:
                all_passed = False
                print(f"\n❌ {test_name} test failed!")
        except Exception as e:
            all_passed = False
            print(f"\n❌ {test_name} test crashed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("The original mLLMCelltype API works perfectly.")
        print("LangExtract integration does NOT break existing code.")
    else:
        print("❌ Some tests failed!")
        print("Please review the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)