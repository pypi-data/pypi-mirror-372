#!/usr/bin/env python3
"""
LangExtract + Cache Integration Test

This script tests the integration between LangExtract and the caching system,
providing detailed performance metrics and validation of cache behavior.
"""

import sys
import os
import time
from typing import Dict, Any

# Add the python package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mllmcelltype import (
    get_cache_stats,
    clear_cache,
    annotate_clusters,
)


def create_test_data():
    """Create test marker gene data."""
    return {
        # Simple case - clear cell types
        "simple": {
            "0": ["CD3D", "CD3E", "CD4"],  # T helper cells
            "1": ["CD8A", "CD8B"],         # Cytotoxic T cells  
            "2": ["MS4A1", "CD19"],        # B cells
        },
        
        # Complex case - more ambiguous marker combinations
        "complex": {
            "0": ["CD68", "CD163", "MSR1", "C1QA", "C1QB"],  # Macrophages
            "1": ["FCGR3A", "LST1", "AIF1", "SERPINA1"],     # Monocytes
            "2": ["CD1C", "FCER1A", "CLEC10A"],              # Dendritic cells
            "3": ["KLRB1", "NCR1", "GZMB", "PRF1"],          # NK cells
        },
        
        # Stress test - many marker genes
        "stress": {
            "0": ["CD3D", "CD3E", "CD3G", "CD4", "IL7R", "CCR7", "SELL", "TCF7"],
            "1": ["CD8A", "CD8B", "GZMK", "CCL5", "CST7", "GZMA", "EOMES", "TBX21"],
            "2": ["MS4A1", "CD79A", "CD79B", "CD19", "BANK1", "BLK", "PAX5"],
        }
    }


def test_langextract_availability():
    """Test if LangExtract is properly configured."""
    print("=== Testing LangExtract Availability ===\n")
    
    # Test with a minimal dataset
    test_markers = {"0": ["CD3D"]}
    
    try:
        # Test with LangExtract explicitly enabled
        result = annotate_clusters(
            marker_genes=test_markers,
            species="human",
            use_langextract=True,
            model="gpt-4o-mini",
            use_cache=False  # Don't cache this test
        )
        
        print("✓ LangExtract is properly configured and working")
        return True
        
    except Exception as e:
        print(f"✗ LangExtract configuration issue: {str(e)}")
        return False


def test_cache_key_generation():
    """Test that different LangExtract configs generate different cache keys."""
    print("\n=== Testing Cache Key Generation ===\n")
    
    test_markers = {"0": ["CD3D", "CD4"]}
    
    # Clear cache for clean test
    cleared = clear_cache()
    print(f"Cleared {cleared} cache files")
    
    configs_to_test = [
        {"complexity_threshold": 0.3},
        {"complexity_threshold": 0.5},
        {"complexity_threshold": 0.7},
        None,  # Default config
    ]
    
    cache_files_created = []
    
    for i, config in enumerate(configs_to_test):
        print(f"\nTest {i+1}: LangExtract config = {config}")
        
        start_time = time.time()
        result = annotate_clusters(
            marker_genes=test_markers,
            species="human",
            use_langextract=True,
            langextract_config=config,
            model="gpt-4o-mini",
            use_cache=True
        )
        duration = time.time() - start_time
        
        stats = get_cache_stats()
        current_files = stats.get('valid_files', 0)
        cache_files_created.append(current_files)
        
        print(f"   Duration: {duration:.2f}s")
        print(f"   Cache files after: {current_files}")
        print(f"   Result: {result.get('0', 'N/A')}")
    
    # Analyze cache behavior
    print(f"\nCache files progression: {cache_files_created}")
    
    if len(set(cache_files_created)) > 1:
        print("✓ Different LangExtract configs create separate cache entries")
    else:
        print("⚠️  All configs may be using the same cache entry")
    
    return cache_files_created


def test_cache_performance():
    """Test cache performance with LangExtract."""
    print("\n=== Testing Cache Performance ===\n")
    
    test_data = create_test_data()
    results = {}
    
    for test_name, markers in test_data.items():
        print(f"\nTesting with {test_name} dataset ({len(markers)} clusters)...")
        
        # Clear cache for this test
        clear_cache()
        
        # First run (cold cache)
        print("  First run (building cache)...")
        start_time = time.time()
        result1 = annotate_clusters(
            marker_genes=markers,
            species="human", 
            use_langextract=True,
            langextract_config={"complexity_threshold": 0.5},
            model="gpt-4o-mini",
            use_cache=True
        )
        first_duration = time.time() - start_time
        
        # Second run (cache hit)
        print("  Second run (cache hit)...")
        start_time = time.time()
        result2 = annotate_clusters(
            marker_genes=markers,
            species="human",
            use_langextract=True,
            langextract_config={"complexity_threshold": 0.5},
            model="gpt-4o-mini", 
            use_cache=True
        )
        second_duration = time.time() - start_time
        
        # Performance metrics
        speedup = first_duration / second_duration if second_duration > 0 else float('inf')
        time_saved = first_duration - second_duration
        
        results[test_name] = {
            'first_duration': first_duration,
            'second_duration': second_duration,
            'speedup': speedup,
            'time_saved': time_saved,
            'consistent_results': result1 == result2
        }
        
        print(f"    First run:  {first_duration:.3f}s")
        print(f"    Second run: {second_duration:.3f}s")
        print(f"    Speedup:    {speedup:.1f}x")
        print(f"    Time saved: {time_saved:.3f}s")
        print(f"    Consistent: {'✓' if result1 == result2 else '✗'}")
    
    return results


def test_cache_invalidation():
    """Test cache invalidation with different parameters."""
    print("\n=== Testing Cache Invalidation ===\n")
    
    base_markers = {"0": ["CD3D", "CD4"]}
    
    # Clear cache
    clear_cache()
    
    # Base configuration
    base_result = annotate_clusters(
        marker_genes=base_markers,
        species="human",
        use_langextract=True,
        langextract_config={"complexity_threshold": 0.5},
        model="gpt-4o-mini",
        use_cache=True
    )
    
    base_stats = get_cache_stats()
    print(f"Base run - Cache files: {base_stats.get('valid_files', 0)}")
    
    # Test different parameters that should create new cache entries
    test_cases = [
        {"species": "mouse"},  # Different species
        {"model": "gpt-4o"},   # Different model
        {"langextract_config": {"complexity_threshold": 0.3}},  # Different config
        {"use_langextract": False},  # Disable LangExtract
    ]
    
    for i, changes in enumerate(test_cases):
        print(f"\nTest case {i+1}: {changes}")
        
        # Prepare parameters
        params = {
            "marker_genes": base_markers,
            "species": "human",
            "use_langextract": True,
            "langextract_config": {"complexity_threshold": 0.5},
            "model": "gpt-4o-mini",
            "use_cache": True
        }
        params.update(changes)
        
        start_time = time.time()
        result = annotate_clusters(**params)
        duration = time.time() - start_time
        
        stats = get_cache_stats()
        cache_files = stats.get('valid_files', 0)
        
        print(f"   Duration: {duration:.3f}s")
        print(f"   Cache files: {cache_files}")
        print(f"   Result differs: {'✓' if result != base_result else '✗'}")


def test_cache_with_errors():
    """Test cache behavior when LangExtract encounters errors."""
    print("\n=== Testing Cache with Error Conditions ===\n")
    
    # Test with invalid model (should fall back gracefully)
    try:
        clear_cache()
        
        print("Testing with invalid model...")
        result = annotate_clusters(
            marker_genes={"0": ["CD3D"]},
            species="human",
            use_langextract=True,
            model="invalid-model-name",
            use_cache=True
        )
        print("✗ Should have failed with invalid model")
        
    except Exception as e:
        print(f"✓ Correctly handled invalid model: {type(e).__name__}")
    
    # Test with empty markers
    try:
        print("\nTesting with empty markers...")
        result = annotate_clusters(
            marker_genes={},
            species="human",
            use_langextract=True,
            model="gpt-4o-mini",
            use_cache=True
        )
        print("✗ Should have failed with empty markers")
        
    except Exception as e:
        print(f"✓ Correctly handled empty markers: {type(e).__name__}")


def generate_performance_report(results: Dict[str, Any]):
    """Generate a comprehensive performance report."""
    print("\n" + "="*60)
    print("=== LANGEXTRACT + CACHE PERFORMANCE REPORT ===")
    print("="*60)
    
    if not results:
        print("No performance data available")
        return
    
    print(f"\n{'Dataset':<10} {'First Run':<10} {'Cache Hit':<10} {'Speedup':<10} {'Consistent':<10}")
    print("-" * 60)
    
    total_speedup = 0
    consistent_count = 0
    
    for test_name, data in results.items():
        speedup_str = f"{data['speedup']:.1f}x" if data['speedup'] != float('inf') else "∞"
        consistent_str = "✓" if data['consistent_results'] else "✗"
        
        print(f"{test_name:<10} {data['first_duration']:<10.3f} {data['second_duration']:<10.3f} {speedup_str:<10} {consistent_str:<10}")
        
        if data['speedup'] != float('inf'):
            total_speedup += data['speedup']
        if data['consistent_results']:
            consistent_count += 1
    
    avg_speedup = total_speedup / len(results) if results else 0
    consistency_rate = (consistent_count / len(results)) * 100 if results else 0
    
    print("-" * 60)
    print(f"Average Speedup: {avg_speedup:.1f}x")
    print(f"Consistency Rate: {consistency_rate:.1f}%")
    
    # Cache statistics
    final_stats = get_cache_stats()
    print(f"\nFinal Cache Statistics:")
    print(f"  Total cache files: {final_stats.get('valid_files', 0)}")
    print(f"  Cache size: {final_stats.get('total_size_mb', 0):.2f} MB")
    print(f"  Cache status: {final_stats.get('status', 'Unknown')}")


def main():
    """Main test function."""
    print("🧪 LangExtract + Cache Integration Test")
    print("="*50)
    
    # Test LangExtract availability
    if not test_langextract_availability():
        print("\n❌ LangExtract not available - skipping integration tests")
        return
    
    # Test cache key generation
    test_cache_key_generation()
    
    # Test cache performance
    performance_results = test_cache_performance()
    
    # Test cache invalidation
    test_cache_invalidation()
    
    # Test error conditions
    test_cache_with_errors()
    
    # Generate final report
    generate_performance_report(performance_results)
    
    print("\n✅ LangExtract + Cache integration testing completed!")


if __name__ == "__main__":
    main()