#!/usr/bin/env python

"""
Advanced test of LangExtract integration in discussion mode.
Creates highly complex discussion scenarios to trigger LangExtract parsing.
"""

import logging
import os
import sys
import time
import json
from dotenv import load_dotenv

# Add package path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from python.mllmcelltype.consensus import interactive_consensus_annotation

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_complex_test_data():
    """Get test data designed to create complex discussion scenarios"""
    # Create intentionally ambiguous marker combinations to force extensive discussions
    marker_genes = {
        "0": ["CD3D", "CD8A", "GNLY", "PRF1", "GZMB", "NKG7"],  # CD8+T vs NK confusion
        "1": ["CD19", "MS4A1", "CD79A", "IGHM", "TCF4", "IRF8"], # B cells vs pDC markers
        "2": ["CD14", "FCGR3A", "LYZ", "S100A8", "VCAN", "CSF1R"], # Classical vs Non-classical monocytes
        "3": ["CD34", "KIT", "FLT3", "RUNX1", "GATA1", "TAL1"],  # HSC vs early progenitors
        "4": ["CD3D", "CD4", "FOXP3", "IL2RA", "CTLA4", "IKZF2"], # Treg vs Th subsets
        "5": ["PPBP", "PF4", "GP1BB", "ITGA2B", "CD41", "CD61"],  # Platelets vs Megakaryocytes
        # Add some really tricky mixed phenotype clusters
        "6": ["CD3D", "CD19", "MS4A1", "TRAC", "IGHM", "CD79A"],  # B/T doublets
        "7": ["CD68", "CD163", "MSR1", "CD14", "LYZ", "ARG1"],    # M2 vs M1 macrophages  
        "8": ["KLRD1", "NCAM1", "CD3D", "GNLY", "CD8A", "PRF1"],  # NK vs NKT cells
        "9": ["CD34", "THY1", "ENG", "PDGFRB", "ACTA2", "COL1A1"], # MSC vs Fibroblast vs Pericyte
    }
    return marker_genes

def create_langextract_config():
    """Create LangExtract config optimized for complex discussion parsing"""
    return {
        "enabled": True,
        "model": "gpt-4o",  # Use more powerful model for complex parsing
        "complexity_threshold": 0.3,  # Lower threshold to trigger more frequently  
        "fallback_enabled": True,
        "cache_enabled": True,
        "api_timeout": 60,  # Longer timeout for complex parsing
        "max_retries": 5,
        "chunk_size": 2000,  # Larger chunks for complex discussions
        "overlap_size": 200,
        "min_confidence": 0.5,  # Lower confidence threshold
        "extraction_method": "structured",
        "output_format": "json",
        "debug_mode": True,
        # Advanced parsing parameters
        "use_advanced_parsing": True,
        "context_window": 3000,
        "semantic_analysis": True,
        "multi_pass_parsing": True
    }

def main():
    print("="*80)
    print("ADVANCED LANGEXTRACT DISCUSSION MODE TEST")  
    print("Focus: Complex discussion scenarios and LangExtract performance")
    print("="*80)
    
    # Get complex test data
    marker_genes = get_complex_test_data()
    print(f"Testing with {len(marker_genes)} complex/ambiguous clusters")
    
    # Check API keys
    api_keys = {}
    for provider in ["openai", "anthropic", "gemini", "qwen"]:
        env_var = f"{provider.upper()}_API_KEY"
        if os.environ.get(env_var):
            api_keys[provider] = os.environ.get(env_var)
    
    print(f"Available API keys: {', '.join(api_keys.keys())}")
    
    # Use diverse models for maximum disagreement
    models = []
    if "openai" in api_keys:
        models.append("gpt-4o")  # Use full GPT-4o for complex reasoning
    if "anthropic" in api_keys:
        models.append("claude-3-5-sonnet-latest")  # Use Sonnet for nuanced analysis
    if "gemini" in api_keys:
        models.append("gemini-2.0-flash-exp")
    if "qwen" in api_keys:
        models.append("qwen-max")
    
    print(f"Using models: {', '.join(models)}")
    
    # Very strict consensus to force discussions
    consensus_threshold = 1.0
    
    # Advanced LangExtract configuration
    langextract_config = create_langextract_config()
    
    print("\nAdvanced LangExtract Configuration:")
    for key, value in langextract_config.items():
        print(f"  {key}: {value}")
    print(f"Consensus threshold: {consensus_threshold}")
    
    print("\nStarting advanced consensus annotation with LangExtract...")
    start_time = time.time()
    
    try:
        # Run with extended discussion parameters
        consensus_results = interactive_consensus_annotation(
            marker_genes=marker_genes,
            species="human",
            models=models,
            api_keys=api_keys,
            tissue="blood",  
            consensus_threshold=consensus_threshold,
            entropy_threshold=0.5,  # Lower entropy threshold for more discussions
            max_discussion_rounds=7,  # More rounds for complex scenarios
            use_cache=False,
            verbose=True,
            use_langextract=True,
            langextract_config=langextract_config
        )
        
        execution_time = time.time() - start_time
        print(f"\n✅ Advanced test completed in {execution_time:.2f} seconds")
        
        # Comprehensive analysis
        analyze_advanced_results(consensus_results, langextract_config, models, execution_time)
        
    except Exception as e:
        print(f"❌ Advanced test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def analyze_advanced_results(consensus_results, langextract_config, models, execution_time):
    """Advanced analysis focusing on LangExtract performance in complex scenarios"""
    
    print("\n" + "="*80)
    print("ADVANCED RESULTS ANALYSIS - LANGEXTRACT PERFORMANCE")
    print("="*80)
    
    final_annotations = consensus_results["consensus"]
    discussion_logs = consensus_results.get("discussion_logs", {})
    langextract_metrics = consensus_results.get("langextract_metrics", {})
    
    # Enhanced statistics
    print(f"\nENHANCED STATISTICS:")
    print(f"  Total clusters: {len(final_annotations)}")
    print(f"  Clusters requiring discussion: {len(discussion_logs)}")
    print(f"  Discussion rate: {len(discussion_logs)/len(final_annotations)*100:.1f}%")
    print(f"  Total execution time: {execution_time:.2f}s")
    print(f"  Average time per cluster: {execution_time/len(final_annotations):.2f}s")
    
    # Consensus quality breakdown
    consensus_proportions = consensus_results["consensus_proportion"]
    perfect_consensus = sum(1 for cp in consensus_proportions.values() if cp == 1.0)
    high_consensus = sum(1 for cp in consensus_proportions.values() if 0.8 <= cp < 1.0)
    medium_consensus = sum(1 for cp in consensus_proportions.values() if 0.6 <= cp < 0.8)
    low_consensus = sum(1 for cp in consensus_proportions.values() if cp < 0.6)
    
    print(f"\nCONSENSUS QUALITY BREAKDOWN:")
    print(f"  Perfect consensus (CP = 1.0): {perfect_consensus}")
    print(f"  High consensus (0.8 ≤ CP < 1.0): {high_consensus}")
    print(f"  Medium consensus (0.6 ≤ CP < 0.8): {medium_consensus}")
    print(f"  Low consensus (CP < 0.6): {low_consensus}")
    
    # LangExtract performance deep dive
    if langextract_metrics:
        print(f"\nLANGEXTRACT DEEP PERFORMANCE ANALYSIS:")
        
        total_invocations = 0
        successful_invocations = 0
        total_parsing_time = 0
        complexity_scores = []
        
        for cluster, metrics in langextract_metrics.items():
            invocations = metrics.get('extraction_count', 0)
            success = metrics.get('success', False)
            parsing_time = metrics.get('parsing_time', 0)
            complexity = metrics.get('complexity_score', 0)
            
            total_invocations += invocations
            if success:
                successful_invocations += 1
            total_parsing_time += parsing_time
            complexity_scores.append(complexity)
        
        success_rate = (successful_invocations / len(langextract_metrics)) * 100 if langextract_metrics else 0
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        
        print(f"  Total LangExtract invocations: {total_invocations}")
        print(f"  Successful invocations: {successful_invocations}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Total parsing time: {total_parsing_time:.2f}s")
        print(f"  Average complexity score: {avg_complexity:.3f}")
        print(f"  Complexity threshold: {langextract_config['complexity_threshold']}")
        print(f"  Clusters above threshold: {sum(1 for c in complexity_scores if c >= langextract_config['complexity_threshold'])}")
    else:
        print(f"\n⚠️  No LangExtract metrics found - may indicate traditional parsing was used")
    
    # Discussion complexity analysis
    if discussion_logs:
        print(f"\nDISCUSSION COMPLEXITY ANALYSIS:")
        
        total_rounds = sum(len(logs) for logs in discussion_logs.values())
        avg_rounds = total_rounds / len(discussion_logs)
        max_rounds = max(len(logs) for logs in discussion_logs.values())
        
        print(f"  Total discussion rounds: {total_rounds}")
        print(f"  Average rounds per cluster: {avg_rounds:.1f}")
        print(f"  Maximum rounds for any cluster: {max_rounds}")
        
        # Analyze discussion length and complexity
        discussion_lengths = []
        for cluster, logs in discussion_logs.items():
            for log in logs:
                discussion_lengths.append(len(log))
        
        if discussion_lengths:
            avg_length = sum(discussion_lengths) / len(discussion_lengths)
            max_length = max(discussion_lengths)
            print(f"  Average discussion length: {avg_length:.0f} characters")
            print(f"  Maximum discussion length: {max_length} characters")
        
        print(f"\nDETAILED DISCUSSION BREAKDOWN:")
        for cluster, logs in discussion_logs.items():
            cp = consensus_results["consensus_proportion"][cluster]
            entropy = consensus_results["entropy"][cluster]
            
            print(f"  Cluster {cluster}: {len(logs)} rounds → {final_annotations[cluster]}")
            print(f"    Final CP: {cp:.2f}, Entropy: {entropy:.2f}")
            
            # Check for LangExtract usage in discussions
            langextract_used = False
            for log in logs:
                if any(keyword in log.lower() for keyword in ['langextract', 'structured parsing', 'advanced parsing']):
                    langextract_used = True
                    break
            
            print(f"    LangExtract detected in discussions: {'✓' if langextract_used else '✗'}")
            
            # Show complexity of first discussion round
            if logs:
                first_round_length = len(logs[0])
                print(f"    First round length: {first_round_length} characters")
    
    # Final annotations with difficulty assessment
    print(f"\nFINAL ANNOTATIONS WITH DIFFICULTY ASSESSMENT:")
    for cluster in sorted(final_annotations.keys(), key=int):
        cp = consensus_results["consensus_proportion"][cluster]
        entropy = consensus_results["entropy"][cluster]
        had_discussion = "🗣️" if cluster in discussion_logs else "✓"
        
        # Difficulty assessment
        if cp == 1.0:
            difficulty = "Easy"
        elif cp >= 0.8:
            difficulty = "Moderate"
        elif cp >= 0.6:
            difficulty = "Hard"
        else:
            difficulty = "Very Hard"
        
        print(f"  {cluster}: {final_annotations[cluster]} | CP: {cp:.2f} | Entropy: {entropy:.2f} | {difficulty} | {had_discussion}")
    
    # Save advanced results
    save_advanced_results(consensus_results, langextract_config, models, execution_time, discussion_logs)

def save_advanced_results(consensus_results, langextract_config, models, execution_time, discussion_logs):
    """Save comprehensive advanced test results"""
    
    result_file = "advanced_langextract_discussion_results.json"
    
    # Create comprehensive results dictionary
    results = {
        "test_info": {
            "test_name": "Advanced LangExtract Discussion Mode Test",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "execution_time": execution_time,
            "models": models,
            "consensus_threshold": 1.0,
            "max_discussion_rounds": 7
        },
        "langextract_config": langextract_config,
        "results_summary": {
            "total_clusters": len(consensus_results["consensus"]),
            "clusters_with_discussions": len(discussion_logs),
            "discussion_rate": len(discussion_logs) / len(consensus_results["consensus"]) * 100,
            "perfect_consensus": sum(1 for cp in consensus_results["consensus_proportion"].values() if cp == 1.0),
            "high_consensus": sum(1 for cp in consensus_results["consensus_proportion"].values() if 0.8 <= cp < 1.0),
            "medium_consensus": sum(1 for cp in consensus_results["consensus_proportion"].values() if 0.6 <= cp < 0.8),
            "low_consensus": sum(1 for cp in consensus_results["consensus_proportion"].values() if cp < 0.6)
        },
        "cluster_results": {
            cluster: {
                "annotation": consensus_results["consensus"][cluster],
                "consensus_proportion": consensus_results["consensus_proportion"][cluster],
                "entropy": consensus_results["entropy"][cluster],
                "had_discussion": cluster in discussion_logs,
                "discussion_rounds": len(discussion_logs.get(cluster, [])),
                "discussion_total_length": sum(len(log) for log in discussion_logs.get(cluster, []))
            }
            for cluster in consensus_results["consensus"].keys()
        },
        "langextract_metrics": consensus_results.get("langextract_metrics", {}),
        "discussion_logs": discussion_logs
    }
    
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nAdvanced results saved to: {result_file}")
    
    # Also save a human-readable summary
    summary_file = "advanced_langextract_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("ADVANCED LANGEXTRACT DISCUSSION MODE TEST SUMMARY\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Test completed at: {results['test_info']['timestamp']}\n")
        f.write(f"Execution time: {execution_time:.2f}s\n") 
        f.write(f"Models: {', '.join(models)}\n\n")
        
        f.write("PERFORMANCE METRICS:\n")
        f.write(f"  Discussion rate: {results['results_summary']['discussion_rate']:.1f}%\n")
        f.write(f"  Perfect consensus: {results['results_summary']['perfect_consensus']}\n")
        f.write(f"  High consensus: {results['results_summary']['high_consensus']}\n")
        f.write(f"  Medium consensus: {results['results_summary']['medium_consensus']}\n")
        f.write(f"  Low consensus: {results['results_summary']['low_consensus']}\n\n")
        
        f.write("CLUSTER DIFFICULTY RANKING:\n")
        sorted_clusters = sorted(
            results['cluster_results'].items(),
            key=lambda x: (x[1]['consensus_proportion'], -x[1]['entropy'])
        )
        
        for cluster, data in sorted_clusters:
            f.write(f"  {cluster}: {data['annotation']} (CP: {data['consensus_proportion']:.2f}, "
                   f"Rounds: {data['discussion_rounds']})\n")
    
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    print("Starting Advanced LangExtract Discussion Mode Test...")
    success = main()
    if success:
        print("\n✅ Advanced test completed successfully!")
    else:
        print("\n❌ Advanced test failed!")
        sys.exit(1)