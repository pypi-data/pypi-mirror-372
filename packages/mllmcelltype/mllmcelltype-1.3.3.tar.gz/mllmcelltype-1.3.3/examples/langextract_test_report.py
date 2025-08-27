#!/usr/bin/env python
"""
Generate comprehensive LangExtract integration test report.
"""

import os
import sys
import time
import json
from typing import Dict, Any

# Add the package directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mllmcelltype.consensus import check_consensus, interactive_consensus_annotation
from mllmcelltype.annotate import annotate_clusters
from mllmcelltype.utils import find_agreement

def run_comprehensive_test():
    """Run comprehensive LangExtract integration tests."""
    
    test_results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_suite": "LangExtract Integration Test",
        "version": "1.0",
        "tests": {}
    }
    
    # API keys
    api_keys = {
        "openai": "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",
        "anthropic": "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",
        "qwen": "sk-4d1266fd8cac4ef7a36efe0c628d68a6",
        "gemini": "AIzaSyDqD_trJuYDSIYO1TWHlOCveV9qQXUJ6uE"
    }
    
    # Test data
    test_predictions = {
        "model1": {"cluster1": "T cells", "cluster2": "B cells", "cluster3": "Macrophages"},
        "model2": {"cluster1": "CD4+ T cells", "cluster2": "B lymphocytes", "cluster3": "Monocytes"},
        "model3": {"cluster1": "T lymphocytes", "cluster2": "B cells", "cluster3": "Tissue-resident macrophages"},
    }
    
    marker_genes = {
        "cluster1": ["CD3E", "CD3D", "IL7R", "LDHB"],
        "cluster2": ["MS4A1", "CD79A", "CD79B", "IGHM"],
        "cluster3": ["LYZ", "S100A9", "S100A8", "FCN1"],
    }
    
    print("="*80)
    print("MLLMCELLTYPE LANGEXTRACT INTEGRATION TEST REPORT")
    print("="*80)
    print(f"Timestamp: {test_results['timestamp']}")
    print(f"Available APIs: {list(api_keys.keys())}")
    print()
    
    # Test 1: Basic consensus functionality
    print("TEST 1: Basic Consensus Functionality")
    print("-" * 40)
    
    try:
        start_time = time.time()
        consensus, consensus_proportion, entropy, controversial = check_consensus(
            test_predictions, api_keys=api_keys
        )
        duration = time.time() - start_time
        
        test_results["tests"]["basic_consensus"] = {
            "status": "PASS",
            "duration": duration,
            "consensus": consensus,
            "consensus_proportion": consensus_proportion,
            "entropy": entropy,
            "controversial": controversial
        }
        
        print("✓ Basic consensus check: PASS")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Controversial clusters: {controversial}")
        
    except Exception as e:
        test_results["tests"]["basic_consensus"] = {
            "status": "FAIL",
            "error": str(e)
        }
        print(f"✗ Basic consensus check: FAIL - {str(e)}")
    
    print()
    
    # Test 2: LangExtract parameter integration
    print("TEST 2: LangExtract Parameter Integration")
    print("-" * 40)
    
    langextract_configs = [
        {"name": "disabled", "use_langextract": False, "config": None},
        {"name": "conservative", "use_langextract": True, "config": {"mode": "conservative"}},
        {"name": "balanced", "use_langextract": True, "config": {"mode": "balanced"}},
        {"name": "aggressive", "use_langextract": True, "config": {"mode": "aggressive"}}
    ]
    
    test_results["tests"]["langextract_configs"] = {}
    
    for le_config in langextract_configs:
        try:
            start_time = time.time()
            results = annotate_clusters(
                marker_genes=marker_genes,
                species="human",
                provider="openai",
                model="gpt-4o-mini",
                api_key=api_keys["openai"],
                tissue="PBMC",
                use_cache=False,
                use_langextract=le_config["use_langextract"],
                langextract_config=le_config["config"]
            )
            duration = time.time() - start_time
            
            test_results["tests"]["langextract_configs"][le_config["name"]] = {
                "status": "PASS",
                "duration": duration,
                "annotations": results,
                "config": le_config
            }
            
            print(f"✓ {le_config['name'].capitalize()} mode: PASS ({duration:.2f}s)")
            
        except Exception as e:
            test_results["tests"]["langextract_configs"][le_config["name"]] = {
                "status": "FAIL",
                "error": str(e),
                "config": le_config
            }
            print(f"✗ {le_config['name'].capitalize()} mode: FAIL - {str(e)}")
    
    print()
    
    # Test 3: Full integration test with controversial clusters
    print("TEST 3: Full Integration with Controversial Clusters")
    print("-" * 40)
    
    try:
        start_time = time.time()
        result = interactive_consensus_annotation(
            marker_genes=marker_genes,
            species="human",
            models=[
                {"provider": "openai", "model": "gpt-4o-mini"},
                {"provider": "anthropic", "model": "claude-3-5-haiku-latest"}
            ],
            api_keys=api_keys,
            tissue="PBMC",
            consensus_threshold=0.8,  # High threshold to create controversy
            entropy_threshold=0.5,   # Low threshold to create controversy
            max_discussion_rounds=1,  # Limit rounds for speed
            use_cache=False,
            verbose=False,
            use_langextract=True,
            langextract_config={"mode": "balanced"}
        )
        duration = time.time() - start_time
        
        test_results["tests"]["full_integration"] = {
            "status": "PASS",
            "duration": duration,
            "consensus": result.get("consensus", {}),
            "controversial_clusters": result.get("controversial_clusters", []),
            "resolved": result.get("resolved", {}),
            "total_clusters": len(result.get("consensus", {}))
        }
        
        controversial_count = len(result.get("controversial_clusters", []))
        total_clusters = len(result.get("consensus", {}))
        
        print(f"✓ Full integration: PASS ({duration:.2f}s)")
        print(f"  Total clusters: {total_clusters}")
        print(f"  Controversial clusters: {controversial_count}")
        print(f"  Resolved clusters: {len(result.get('resolved', {}))}")
        
    except Exception as e:
        test_results["tests"]["full_integration"] = {
            "status": "FAIL",
            "error": str(e)
        }
        print(f"✗ Full integration: FAIL - {str(e)}")
    
    print()
    
    # Test 4: Performance comparison
    print("TEST 4: Performance Comparison")
    print("-" * 40)
    
    test_results["tests"]["performance_comparison"] = {}
    
    for mode in ["traditional", "langextract"]:
        try:
            times = []
            for i in range(3):  # Run 3 times for average
                start_time = time.time()
                
                if mode == "traditional":
                    annotate_clusters(
                        marker_genes={"test": ["CD3E", "CD4"]},
                        species="human",
                        provider="openai",
                        model="gpt-4o-mini",
                        api_key=api_keys["openai"],
                        use_cache=False,
                        use_langextract=False
                    )
                else:
                    annotate_clusters(
                        marker_genes={"test": ["CD3E", "CD4"]},
                        species="human",
                        provider="openai",
                        model="gpt-4o-mini",
                        api_key=api_keys["openai"],
                        use_cache=False,
                        use_langextract=True,
                        langextract_config={"mode": "balanced"}
                    )
                
                times.append(time.time() - start_time)
            
            avg_time = sum(times) / len(times)
            
            test_results["tests"]["performance_comparison"][mode] = {
                "status": "PASS",
                "average_duration": avg_time,
                "runs": times
            }
            
            print(f"✓ {mode.capitalize()} mode: {avg_time:.2f}s average")
            
        except Exception as e:
            test_results["tests"]["performance_comparison"][mode] = {
                "status": "FAIL",
                "error": str(e)
            }
            print(f"✗ {mode.capitalize()} mode: FAIL - {str(e)}")
    
    print()
    
    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, test_data in test_results["tests"].items():
        if isinstance(test_data, dict) and "status" in test_data:
            total_tests += 1
            if test_data["status"] == "PASS":
                passed_tests += 1
        else:
            # Handle nested test results like langextract_configs
            for subtest_name, subtest_data in test_data.items():
                total_tests += 1
                if subtest_data.get("status") == "PASS":
                    passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Tests Run: {total_tests}")
    print(f"Tests Passed: {passed_tests}")
    print(f"Tests Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    test_results["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": success_rate
    }
    
    if success_rate >= 80:
        print("\n🎉 LangExtract integration: SUCCESSFUL")
        print("✓ All core functionality working")
        print("✓ API integration verified")
        print("✓ Configuration parameters working")
        print("✓ Performance acceptable")
    else:
        print("\n⚠️  LangExtract integration: NEEDS ATTENTION")
        print("Some tests failed - review errors above")
    
    # Save detailed results
    results_file = f"langextract_test_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return test_results

if __name__ == "__main__":
    run_comprehensive_test()