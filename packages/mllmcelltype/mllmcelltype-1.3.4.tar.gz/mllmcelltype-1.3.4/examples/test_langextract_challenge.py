#!/usr/bin/env python3
"""
Challenge test for LangExtract integration - creating scenarios to trigger LangExtract.
This test artificially creates complex parsing scenarios to test LangExtract effectiveness.
"""

import os
import sys
import time
from typing import Dict, Any

# Add python directory to path for local development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import mLLMCelltype functions
from mllmcelltype import annotate_clusters, setup_logging
from mllmcelltype.langextract_config import load_langextract_config, print_langextract_config

# Set up logging
setup_logging()

# Check if API keys are available
api_keys = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"), 
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "QWEN_API_KEY": os.getenv("QWEN_API_KEY"),
}

available_apis = [k for k, v in api_keys.items() if v]
print(f"Available API keys: {', '.join(available_apis)}")

if not available_apis:
    print("No API keys found. Please set API keys as environment variables.")
    sys.exit(1)

# Create complex marker gene sets that might challenge traditional parsing
complex_marker_genes = {
    "0": ["CD3D", "CD3E", "CD3G", "IL7R", "TCF7", "LEF1", "CCR7", "SELL", "CD28", "CD27"],  # Naive T cells
    "1": ["CD8A", "CD8B", "CCL5", "GZMA", "GZMB", "PRF1", "EOMES", "TBX21", "IFNG", "TNF"],  # Cytotoxic T cells
    "2": ["CD4", "IL2RA", "FOXP3", "CTLA4", "TIGIT", "ICOS", "TNFRSF4", "TNFRSF18", "IL10", "TGFB1"],  # Regulatory T cells
    "3": ["MS4A1", "CD79A", "CD79B", "CD19", "CD20", "PAX5", "EBF1", "BCL6", "AID", "IRF4"],  # B cells
    "4": ["CD14", "CD16", "LYZ", "S100A8", "S100A9", "CSF1R", "CCR2", "CX3CR1", "ITGAM", "FCGR3A"],  # Monocytes
    "5": ["KLRB1", "NCAM1", "NKG7", "GNLY", "GZMA", "GZMB", "PRF1", "KLRD1", "KLRF1", "KIR2DL1"],  # NK cells
    "6": ["FCER1A", "CD1C", "CLEC9A", "XCR1", "BATF3", "IRF8", "ZBTB46", "CADM1", "CLEC10A", "CD68"],  # Dendritic cells
    "7": ["PPBP", "PF4", "TUBB1", "GP9", "ITGA2B", "ITGB3", "SELP", "PDGFA", "CXCL4", "CCL5"],  # Platelets
    "8": ["MKI67", "TOP2A", "PCNA", "CCNA2", "CCNB1", "CDC20", "CDKN3", "CKS1B", "CKS2", "TYMS"],  # Proliferating cells
    "9": ["IGLC1", "IGLC2", "IGLC3", "IGHG1", "IGHG2", "IGHG3", "IGHG4", "IGHA1", "IGHA2", "JCHAIN"]  # Plasma cells
}

print(f"Created complex marker gene dataset with {len(complex_marker_genes)} clusters")
print(f"Total markers: {sum(len(markers) for markers in complex_marker_genes.values())}")

# Test with different complexity thresholds
threshold_configs = [
    {"threshold": 0.0, "desc": "Very low threshold (should always use LangExtract)"},
    {"threshold": 0.3, "desc": "Low threshold"},
    {"threshold": 0.6, "desc": "Medium threshold"},
    {"threshold": 0.9, "desc": "High threshold (should rarely use LangExtract)"}
]

models_to_test = []
if os.getenv("OPENAI_API_KEY"):
    models_to_test.append(("openai", "gpt-4o-mini"))
if os.getenv("ANTHROPIC_API_KEY"):
    models_to_test.append(("anthropic", "claude-3-5-haiku-latest"))
if os.getenv("GEMINI_API_KEY"):
    models_to_test.append(("gemini", "gemini-2.0-flash-exp"))

if not models_to_test:
    print("No supported models available for testing")
    sys.exit(1)

results = []

print("\n" + "="*80)
print("LANGEXTRACT COMPLEXITY THRESHOLD CHALLENGE TEST")
print("="*80)

for provider, model in models_to_test:
    print(f"\nTesting model: {model}")
    print("-" * 50)
    
    for config in threshold_configs:
        threshold = config["threshold"]
        desc = config["desc"]
        
        print(f"\n🔬 Testing {desc} (threshold: {threshold})")
        
        # Configure LangExtract with specific threshold
        langextract_config = load_langextract_config({
            "enabled": True,
            "model": "gemini-2.0-flash-exp",
            "complexity_threshold": threshold,
            "api_timeout": 30,
            "max_retries": 3,
            "debug_mode": True
        })
        
        # Test traditional method
        start_time = time.time()
        annotations_traditional = annotate_clusters(
            marker_genes=complex_marker_genes,
            species="human",
            tissue="blood",
            provider=provider,
            model=model,
            use_langextract=False
        )
        traditional_time = time.time() - start_time
        
        # Test LangExtract method
        start_time = time.time()
        annotations_langextract = annotate_clusters(
            marker_genes=complex_marker_genes,
            species="human",
            tissue="blood",
            provider=provider,
            model=model,
            use_langextract=True,
            langextract_config=langextract_config
        )
        langextract_time = time.time() - start_time
        
        # Calculate similarity
        same_annotations = sum(1 for c in annotations_traditional.keys() 
                             if annotations_traditional[c] == annotations_langextract[c])
        total_clusters = len(annotations_traditional)
        similarity = same_annotations / total_clusters * 100
        
        result = {
            "model": model,
            "threshold": threshold,
            "traditional_time": traditional_time,
            "langextract_time": langextract_time,
            "similarity": similarity,
            "time_diff": langextract_time - traditional_time,
            "traditional_annotations": annotations_traditional,
            "langextract_annotations": annotations_langextract
        }
        results.append(result)
        
        print(f"  ⏱️  Traditional: {traditional_time:.3f}s, LangExtract: {langextract_time:.3f}s")
        print(f"  📊 Time difference: {langextract_time - traditional_time:+.3f}s")
        print(f"  🎯 Annotation similarity: {similarity:.1f}%")
        
        if similarity < 100:
            print(f"  🔍 Found {total_clusters - same_annotations} differing annotations:")
            for cluster in annotations_traditional.keys():
                if annotations_traditional[cluster] != annotations_langextract[cluster]:
                    print(f"    Cluster {cluster}: '{annotations_traditional[cluster]}' vs '{annotations_langextract[cluster]}'")

# Summary analysis
print("\n" + "="*80)
print("COMPREHENSIVE ANALYSIS SUMMARY")
print("="*80)

# Group results by model
for provider, model in models_to_test:
    model_results = [r for r in results if r["model"] == model]
    if not model_results:
        continue
        
    print(f"\n📊 {model.upper()} PERFORMANCE ANALYSIS:")
    print("-" * 50)
    
    for result in model_results:
        print(f"Threshold {result['threshold']:.1f}: "
              f"Similarity {result['similarity']:.1f}%, "
              f"Time Δ {result['time_diff']:+.3f}s")
    
    # Find best performing threshold
    best_similarity = max(r["similarity"] for r in model_results)
    best_time = min(r["langextract_time"] for r in model_results)
    
    print(f"Best similarity: {best_similarity:.1f}%")
    print(f"Fastest LangExtract: {best_time:.3f}s")

# Save detailed results
results_file = "langextract_challenge_results.txt"
with open(results_file, "w") as f:
    f.write("LangExtract Complexity Threshold Challenge Test Results\n")
    f.write("=" * 60 + "\n\n")
    
    f.write("TEST CONFIGURATION:\n")
    f.write(f"Models tested: {len(models_to_test)}\n")
    f.write(f"Complexity thresholds: {[c['threshold'] for c in threshold_configs]}\n")
    f.write(f"Complex clusters: {len(complex_marker_genes)}\n")
    f.write(f"Total markers: {sum(len(markers) for markers in complex_marker_genes.values())}\n\n")
    
    f.write("DETAILED RESULTS:\n")
    f.write("Model\tThreshold\tTrad_Time\tLang_Time\tTime_Diff\tSimilarity\n")
    
    for result in results:
        f.write(f"{result['model']}\t{result['threshold']:.1f}\t"
                f"{result['traditional_time']:.3f}\t{result['langextract_time']:.3f}\t"
                f"{result['time_diff']:+.3f}\t{result['similarity']:.1f}%\n")
    
    f.write("\nDETAILED ANNOTATIONS:\n")
    for result in results:
        f.write(f"\n{result['model']} - Threshold {result['threshold']}:\n")
        f.write("Cluster\tTraditional\tLangExtract\tMatch\n")
        for cluster in sorted(result['traditional_annotations'].keys(), key=int):
            trad = result['traditional_annotations'][cluster]
            lang = result['langextract_annotations'][cluster]
            match = "✓" if trad == lang else "✗"
            f.write(f"{cluster}\t{trad}\t{lang}\t{match}\n")

print(f"\n📄 Detailed results saved to {results_file}")

# Final recommendations
print("\n🎯 LANGEXTRACT PERFORMANCE RECOMMENDATIONS:")
print("-" * 50)

avg_similarity = sum(r["similarity"] for r in results) / len(results)
avg_time_improvement = sum(r["time_diff"] for r in results) / len(results)

print(f"Average annotation similarity: {avg_similarity:.1f}%")
print(f"Average time impact: {avg_time_improvement:+.3f}s")

if avg_similarity >= 95:
    print("✅ Excellent: LangExtract maintains high annotation quality")
elif avg_similarity >= 85:
    print("⚠️  Good: LangExtract shows minor differences in annotations")
else:
    print("❌ Concern: LangExtract shows significant annotation differences")

if avg_time_improvement < 0:
    print("🚀 Performance: LangExtract improves processing speed")
elif avg_time_improvement < 0.1:
    print("⚡ Performance: LangExtract has minimal time overhead")
else:
    print("🐌 Performance: LangExtract adds processing time")

print("\nTest completed successfully!")