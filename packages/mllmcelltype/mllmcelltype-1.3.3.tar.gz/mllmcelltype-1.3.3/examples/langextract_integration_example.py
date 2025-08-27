#!/usr/bin/env python3
"""
LangExtract Integration Example for mLLMCelltype

This script demonstrates how to use the enhanced format_results() function
with langextract integration for improved cell type annotation parsing.
"""

import os
import sys
from typing import Dict, List

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python"))

def demonstrate_basic_usage():
    """Demonstrate basic usage of enhanced format_results()."""
    print("📋 Basic Usage Examples")
    print("=" * 50)
    
    from mllmcelltype.utils import format_results
    
    # Example 1: Standard format (backward compatible)
    print("\n1️⃣ Standard 'Cluster X: Type' format:")
    results = [
        "Cluster 0: CD8+ T cells",
        "Cluster 1: Memory B cells", 
        "Cluster 2: Natural Killer cells"
    ]
    clusters = ["0", "1", "2"]
    
    annotations = format_results(results, clusters)
    print(f"   Input: {results}")
    print(f"   Output: {annotations}")
    
    # Example 2: JSON format
    print("\n2️⃣ JSON format parsing:")
    json_results = [
        '''```json
        {
          "annotations": [
            {"cluster": "0", "cell_type": "Plasma cells", "confidence": "high"},
            {"cluster": "1", "cell_type": "Dendritic cells", "confidence": "medium"}
          ]
        }
        ```'''
    ]
    json_clusters = ["0", "1"]
    
    json_annotations = format_results(json_results, json_clusters)
    print(f"   Input: JSON with annotations")
    print(f"   Output: {json_annotations}")

def demonstrate_langextract_configuration():
    """Demonstrate langextract-specific configuration options."""
    print("\n🔧 LangExtract Configuration Examples")
    print("=" * 50)
    
    from mllmcelltype.utils import format_results
    
    # Example 1: Force traditional parsing
    print("\n1️⃣ Force traditional parsing (langextract disabled):")
    complex_results = [
        "Based on marker analysis, the first cluster shows T cell characteristics.",
        "The second population exhibits B cell properties with high CD19.",
        "Natural killer features are prominent in the third group."
    ]
    clusters = ["0", "1", "2"]
    
    traditional_result = format_results(
        complex_results, 
        clusters, 
        use_langextract=False  # Force traditional
    )
    print(f"   Method: Traditional (forced)")
    print(f"   Output: {traditional_result}")
    
    # Example 2: Auto-detection mode
    print("\n2️⃣ Auto-detection mode (default):")
    auto_result = format_results(complex_results, clusters)
    print(f"   Method: Auto-detection")
    print(f"   Output: {auto_result}")
    
    # Example 3: Custom configuration
    print("\n3️⃣ Custom langextract configuration:")
    config = {
        "complexity_threshold": 0.3,  # Lower threshold = more likely to use langextract
        "model": "gemini-2.5-flash",
        "timeout": 15,
        "context": "This is PBMC single-cell data analysis"
    }
    
    configured_result = format_results(
        complex_results,
        clusters,
        langextract_config=config
    )
    print(f"   Method: Custom config (threshold=0.3)")
    print(f"   Output: {configured_result}")

def demonstrate_complex_parsing_scenarios():
    """Demonstrate complex parsing scenarios where langextract excels."""
    print("\n🧠 Complex Parsing Scenarios")
    print("=" * 50)
    
    from mllmcelltype.utils import format_results
    
    # Scenario 1: Mixed formats
    print("\n1️⃣ Mixed format response:")
    mixed_results = [
        "Cluster 0: T cells",
        "For cluster 1, the analysis suggests B cells based on CD19 expression",
        '{"cluster": "2", "cell_type": "Monocytes", "markers": ["CD14", "LYZ"]}'
    ]
    mixed_clusters = ["0", "1", "2"]
    
    mixed_result = format_results(mixed_results, mixed_clusters)
    print(f"   Input: Mixed formats")
    print(f"   Output: {mixed_result}")
    
    # Scenario 2: Malformed JSON
    print("\n2️⃣ Malformed JSON response:")
    malformed_json = [
        '''```json
        {
          "annotations": [
            {
              "cluster": "0"
              "cell_type": "CD4+ T cells"  // Missing comma
              "confidence": "high",
            },
            {
              "cluster": "1",
              "cell_type": "Regulatory T cells",  // Extra comma
            }
          ],  // Extra comma
        }
        ```'''
    ]
    malformed_clusters = ["0", "1"]
    
    malformed_result = format_results(malformed_json, malformed_clusters)
    print(f"   Input: Malformed JSON")
    print(f"   Output: {malformed_result}")
    
    # Scenario 3: Descriptive natural language
    print("\n3️⃣ Descriptive natural language:")
    descriptive_results = [
        "The first cluster, characterized by high CD3 and CD8A expression, "
        "represents CD8+ T cells with cytotoxic potential.",
        "Cluster 1 shows strong B cell markers including CD19, MS4A1, and "
        "immunoglobulin genes, indicating mature B lymphocytes.",
        "Based on GNLY, NKG7, and KLRD1 expression patterns, cluster 2 "
        "represents natural killer cells with activated phenotype."
    ]
    descriptive_clusters = ["0", "1", "2"]
    
    descriptive_result = format_results(descriptive_results, descriptive_clusters)
    print(f"   Input: Descriptive natural language")
    print(f"   Output: {descriptive_result}")

def demonstrate_error_handling():
    """Demonstrate robust error handling and fallback mechanisms."""
    print("\n🛡️ Error Handling & Fallback Mechanisms")
    print("=" * 50)
    
    from mllmcelltype.utils import format_results
    
    # Example 1: Empty input
    print("\n1️⃣ Empty input handling:")
    empty_result = format_results([], [])
    print(f"   Input: [], []")
    print(f"   Output: {empty_result}")
    
    # Example 2: Mismatched counts
    print("\n2️⃣ Mismatched result/cluster counts:")
    few_results = ["T cells"]
    many_clusters = ["0", "1", "2", "3"]
    
    mismatch_result = format_results(few_results, many_clusters)
    print(f"   Input: 1 result, 4 clusters")
    print(f"   Output: {mismatch_result}")
    
    # Example 3: Unparseable input
    print("\n3️⃣ Completely unparseable input:")
    garbage_results = ["???", "Unable to determine", "Error in analysis"]
    garbage_clusters = ["0", "1", "2"]
    
    garbage_result = format_results(garbage_results, garbage_clusters)
    print(f"   Input: Unparseable content")
    print(f"   Output: {garbage_result}")

def demonstrate_performance_characteristics():
    """Demonstrate performance characteristics of the enhanced function."""
    print("\n⚡ Performance Characteristics")
    print("=" * 50)
    
    import time
    from mllmcelltype.utils import format_results, _format_results_traditional
    
    # Test data
    results = ["Cluster 0: T cells", "Cluster 1: B cells", "Cluster 2: NK cells"]
    clusters = ["0", "1", "2"]
    
    # Traditional method
    start = time.time()
    traditional_result = _format_results_traditional(results, clusters)
    traditional_time = time.time() - start
    
    # Enhanced method (langextract disabled)
    start = time.time()
    enhanced_result = format_results(results, clusters, use_langextract=False)
    enhanced_time = time.time() - start
    
    print(f"\n📊 Performance Comparison:")
    print(f"   Traditional method: {traditional_time*1000:.2f}ms")
    print(f"   Enhanced method:    {enhanced_time*1000:.2f}ms")
    print(f"   Results identical:  {traditional_result == enhanced_result}")
    
    if traditional_time > 0:
        overhead = ((enhanced_time - traditional_time) / traditional_time) * 100
        print(f"   Overhead:           {overhead:.1f}%")
    else:
        print(f"   Overhead:           Both methods very fast")

def check_langextract_availability():
    """Check langextract availability and API key status."""
    print("🔍 LangExtract Availability Check")
    print("=" * 50)
    
    # Check langextract import
    try:
        import langextract
        print("✅ langextract library is available")
        print(f"   Version: {getattr(langextract, '__version__', 'unknown')}")
    except ImportError as e:
        print(f"❌ langextract library not available: {e}")
        print("   Install with: pip install langextract")
        return False
    
    # Check API keys
    api_keys = {
        "LANGEXTRACT_API_KEY": os.getenv("LANGEXTRACT_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"), 
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    }
    
    available_keys = [name for name, key in api_keys.items() if key]
    
    if available_keys:
        print(f"✅ API keys available: {', '.join(available_keys)}")
        print("   Full langextract functionality enabled")
        return True
    else:
        print("⚠️  No API keys detected")
        print("   LangExtract will fallback to traditional parsing")
        print("\n💡 To enable full functionality, set one of:")
        for key_name in api_keys.keys():
            print(f"   export {key_name}=your_api_key_here")
        return False

def main():
    """Run all demonstration examples."""
    print("🚀 mLLMCelltype LangExtract Integration Examples")
    print("=" * 60)
    
    # Check availability first
    langextract_available = check_langextract_availability()
    
    print("\n" + "=" * 60)
    
    # Run examples
    demonstrate_basic_usage()
    demonstrate_langextract_configuration() 
    demonstrate_complex_parsing_scenarios()
    demonstrate_error_handling()
    demonstrate_performance_characteristics()
    
    # Summary
    print("\n🎯 Summary")
    print("=" * 60)
    print("\n✅ Key Benefits of Enhanced format_results():")
    print("  • 100% backward compatible with existing code")
    print("  • Intelligent parsing strategy selection")
    print("  • Robust error handling and fallback mechanisms")
    print("  • Detailed logging for debugging and monitoring")
    print("  • Support for complex and malformed responses")
    if langextract_available:
        print("  • LangExtract integration for advanced parsing")
    else:
        print("  • Ready for LangExtract when API key is configured")
    
    print("\n📚 Usage Patterns:")
    print("  • Default usage: format_results(results, clusters)")
    print("  • Force traditional: format_results(results, clusters, use_langextract=False)")
    print("  • Custom config: format_results(results, clusters, langextract_config=config)")
    print("  • Auto-detection: Let the system choose the best method")
    
    print("\n🔧 Integration Notes:")
    print("  • Zero configuration required for basic usage")
    print("  • All existing code continues to work unchanged") 
    print("  • Optional langextract features enhance capability")
    print("  • Comprehensive error handling prevents failures")
    
    print("\n🎉 Integration completed successfully!")

if __name__ == "__main__":
    main()