#!/usr/bin/env python

"""
Simplified test of LangExtract integration in discussion mode.
Tests consensus annotation with high disagreement threshold to trigger discussions.
"""

import logging
import os
import sys
import time
from dotenv import load_dotenv

# Add package path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from python.mllmcelltype.consensus import interactive_consensus_annotation

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_test_marker_genes():
    """Get test marker gene data that should trigger discussions"""
    # Use controversial marker genes that might lead to disagreement
    # Mix clear and ambiguous markers
    marker_genes = {
        "0": ["CD3D", "CD3E", "CD3G", "TRAC", "IL7R", "CCR7"],  # Clear T cells
        "1": ["MS4A1", "CD79A", "CD79B", "IGHM", "IGHD"],       # Clear B cells  
        "2": ["LYZ", "CD68", "AIF1", "CST3", "TYROBP"],         # Clear Monocytes/Macrophages
        "3": ["GNLY", "NKG7", "CD247", "GZMA", "GZMB", "PRF1"], # NK cells
        "4": ["FCGR3A", "MS4A7", "CD16", "IFITM3", "LST1"],     # CD16+ Monocytes
        "5": ["PPBP", "PF4", "SDPR", "MMRN1", "SPARC"],         # Megakaryocytes/Platelets
        "6": ["HBB", "HBA1", "HBA2", "ALAS2", "GYPA"],          # Erythroid cells
        # Add some potentially controversial clusters with mixed markers
        "7": ["CD3D", "GNLY", "NKG7", "CD8A", "GZMK"],          # Could be NK-like T or T-like NK
        "8": ["CD14", "FCGR3A", "S100A9", "LYZ", "VCAN"],       # Intermediate monocytes
        "9": ["IGHM", "CD79A", "CD3E", "TRAC", "MS4A1"],        # Mixed B/T markers (controversial)
    }
    return marker_genes

def main():
    print("="*80)
    print("LANGEXTRACT DISCUSSION MODE INTEGRATION TEST")
    print("="*80)
    
    # Get test data
    marker_genes = get_test_marker_genes()
    print(f"Testing with {len(marker_genes)} clusters")
    
    # Check available API keys
    api_keys = {}
    for provider in ["openai", "anthropic", "gemini", "qwen"]:
        env_var = f"{provider.upper()}_API_KEY"
        if os.environ.get(env_var):
            api_keys[provider] = os.environ.get(env_var)
    
    print(f"Available API keys: {', '.join(api_keys.keys())}")
    
    # Select models to use
    models = []
    if "openai" in api_keys:
        models.append("gpt-4o-mini")  # Use mini for faster testing
    if "anthropic" in api_keys:
        models.append("claude-3-5-haiku-latest")  # Use haiku for faster testing
    if "gemini" in api_keys:
        models.append("gemini-2.0-flash-exp")
    if "qwen" in api_keys:
        models.append("qwen-max")
    
    print(f"Using models: {', '.join(models)}")
    
    # Use high consensus threshold to force discussions
    consensus_threshold = 1.0  # Only perfect agreement counts as consensus
    
    # Configure LangExtract with balanced settings
    langextract_config = {
        "enabled": True,
        "model": "gemini-2.0-flash-exp",
        "complexity_threshold": 0.6,
        "fallback_enabled": True,
        "cache_enabled": True,
        "api_timeout": 30,
        "max_retries": 3,
        "chunk_size": 1000,
        "overlap_size": 100,
        "min_confidence": 0.6,
        "extraction_method": "structured",
        "output_format": "json",
        "debug_mode": True  # Enable debug for detailed analysis
    }
    
    print("\nLangExtract Configuration:")
    for key, value in langextract_config.items():
        print(f"  {key}: {value}")
    print(f"Consensus threshold: {consensus_threshold} (requiring perfect agreement)")
    
    print("\nStarting consensus annotation with LangExtract...")
    start_time = time.time()
    
    try:
        # Run consensus annotation with LangExtract
        consensus_results = interactive_consensus_annotation(
            marker_genes=marker_genes,
            species="human", 
            models=models,
            api_keys=api_keys,
            tissue="blood",
            consensus_threshold=consensus_threshold,
            max_discussion_rounds=5,
            use_cache=False,  # Disable cache for fresh test
            verbose=True,
            use_langextract=True,
            langextract_config=langextract_config
        )
        
        execution_time = time.time() - start_time
        print(f"\n✅ Test completed in {execution_time:.2f} seconds")
        
        # Analyze results
        analyze_results(consensus_results, langextract_config, models, execution_time)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def analyze_results(consensus_results, langextract_config, models, execution_time):
    """Analyze and display the consensus results with LangExtract metrics"""
    
    print("\n" + "="*80)
    print("DETAILED RESULTS ANALYSIS")
    print("="*80)
    
    final_annotations = consensus_results["consensus"]
    discussion_logs = consensus_results.get("discussion_logs", {})
    langextract_metrics = consensus_results.get("langextract_metrics", {})
    
    # Basic statistics
    print(f"\nBASIC STATISTICS:")
    print(f"  Total clusters: {len(final_annotations)}")
    print(f"  Clusters with discussions: {len(discussion_logs)}")
    print(f"  Discussion rate: {len(discussion_logs)/len(final_annotations)*100:.1f}%")
    print(f"  Total execution time: {execution_time:.2f}s")
    
    # Consensus quality analysis
    high_confidence = sum(1 for cp in consensus_results["consensus_proportion"].values() if cp >= 0.8)
    medium_confidence = sum(1 for cp in consensus_results["consensus_proportion"].values() if 0.6 <= cp < 0.8)
    low_confidence = sum(1 for cp in consensus_results["consensus_proportion"].values() if cp < 0.6)
    
    print(f"\nCONSENSUS QUALITY:")
    print(f"  High confidence (CP ≥ 0.8): {high_confidence}")
    print(f"  Medium confidence (0.6 ≤ CP < 0.8): {medium_confidence}")
    print(f"  Low confidence (CP < 0.6): {low_confidence}")
    
    # Display final annotations
    print(f"\nFINAL ANNOTATIONS:")
    for cluster in sorted(final_annotations.keys(), key=int):
        cp = consensus_results["consensus_proportion"][cluster]
        entropy = consensus_results["entropy"][cluster]
        had_discussion = "🗣️" if cluster in discussion_logs else "✓"
        print(f"  {cluster}: {final_annotations[cluster]} (CP: {cp:.2f}, Entropy: {entropy:.2f}) {had_discussion}")
    
    # LangExtract performance analysis
    if langextract_metrics:
        print(f"\nLANGEXTRACT PERFORMANCE:")
        total_extractions = sum(metrics.get('extraction_count', 0) for metrics in langextract_metrics.values())
        successful_extractions = sum(1 for metrics in langextract_metrics.values() if metrics.get('success', False))
        total_parsing_time = sum(metrics.get('parsing_time', 0) for metrics in langextract_metrics.values())
        
        print(f"  Total extractions attempted: {total_extractions}")
        print(f"  Successful extractions: {successful_extractions}")
        print(f"  Success rate: {(successful_extractions/len(langextract_metrics)*100):.1f}%")
        print(f"  Total parsing time: {total_parsing_time:.2f}s")
        print(f"  Average parsing time: {(total_parsing_time/len(langextract_metrics)):.2f}s per cluster")
    
    # Discussion analysis
    if discussion_logs:
        print(f"\nDISCUSSION ANALYSIS:")
        total_rounds = sum(len(logs) for logs in discussion_logs.values())
        avg_rounds = total_rounds / len(discussion_logs)
        print(f"  Total discussion rounds: {total_rounds}")
        print(f"  Average rounds per controversial cluster: {avg_rounds:.1f}")
        
        print(f"\nDISCUSSION DETAILS:")
        for cluster, logs in discussion_logs.items():
            print(f"  Cluster {cluster}: {len(logs)} rounds")
            cp = consensus_results["consensus_proportion"][cluster]
            print(f"    Final consensus: {final_annotations[cluster]} (CP: {cp:.2f})")
            
            # Show first few lines of each discussion round
            for round_num, log in enumerate(logs):
                lines = log.split('\n')[:3]  # First 3 lines
                preview = ' '.join(lines).strip()[:150] + "..." if len(log) > 150 else ' '.join(lines).strip()
                print(f"    Round {round_num + 1}: {preview}")
                
                # Check for LangExtract usage indicators
                if "langextract" in log.lower() or "structured parsing" in log.lower():
                    print(f"      ✓ LangExtract processing detected")
            
            if cluster in langextract_metrics:
                cluster_metrics = langextract_metrics[cluster]
                print(f"    LangExtract metrics: {cluster_metrics}")
    else:
        print(f"\nNo discussions triggered - all clusters reached consensus quickly!")
    
    # Save detailed results
    save_detailed_results(consensus_results, langextract_config, models, execution_time)

def save_detailed_results(consensus_results, langextract_config, models, execution_time):
    """Save comprehensive test results to file"""
    
    result_file = "langextract_discussion_test_results.txt"
    
    with open(result_file, "w") as f:
        f.write("LANGEXTRACT DISCUSSION MODE TEST RESULTS\n")
        f.write("="*60 + "\n\n")
        
        f.write("TEST CONFIGURATION:\n")
        f.write(f"  Models used: {', '.join(models)}\n")
        f.write(f"  Consensus threshold: 1.0 (perfect agreement required)\n")
        f.write(f"  Max discussion rounds: 5\n")
        f.write(f"  Total execution time: {execution_time:.2f}s\n\n")
        
        f.write("LANGEXTRACT CONFIGURATION:\n")
        for key, value in langextract_config.items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")
        
        # Results summary
        final_annotations = consensus_results["consensus"] 
        discussion_logs = consensus_results.get("discussion_logs", {})
        
        f.write("RESULTS SUMMARY:\n")
        f.write(f"  Total clusters: {len(final_annotations)}\n")
        f.write(f"  Clusters with discussions: {len(discussion_logs)}\n")
        f.write(f"  Discussion rate: {len(discussion_logs)/len(final_annotations)*100:.1f}%\n\n")
        
        f.write("CLUSTER ANNOTATIONS:\n")
        f.write("Cluster\tAnnotation\tCP\tEntropy\tDiscussion\n")
        for cluster in sorted(final_annotations.keys(), key=int):
            cp = consensus_results["consensus_proportion"][cluster] 
            entropy = consensus_results["entropy"][cluster]
            had_discussion = "Yes" if cluster in discussion_logs else "No"
            f.write(f"{cluster}\t{final_annotations[cluster]}\t{cp:.2f}\t{entropy:.2f}\t{had_discussion}\n")
        
        # Detailed discussion logs
        if discussion_logs:
            f.write(f"\nDETAILED DISCUSSION LOGS:\n")
            f.write("="*60 + "\n")
            
            for cluster, logs in discussion_logs.items():
                f.write(f"\nCLUSTER {cluster} DISCUSSION:\n")
                f.write(f"Rounds: {len(logs)}\n")
                f.write(f"Final: {final_annotations[cluster]}\n")
                f.write("-"*40 + "\n")
                
                for round_num, log in enumerate(logs):
                    f.write(f"Round {round_num + 1}:\n")
                    f.write(f"{log}\n")
                    f.write("-"*20 + "\n")
    
    print(f"\nDetailed results saved to: {result_file}")

if __name__ == "__main__":
    print("Starting LangExtract Discussion Mode Integration Test...")
    success = main()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)