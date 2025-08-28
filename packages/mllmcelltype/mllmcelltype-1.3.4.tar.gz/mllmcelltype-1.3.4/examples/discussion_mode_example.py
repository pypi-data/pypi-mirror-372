#!/usr/bin/env python

"""
Test the discussion mode functionality of LLMCelltype.
Force trigger discussion mode by setting a high consensus threshold.
"""

import logging
import os
import sys

# Try to import matplotlib for visualization (optional)
try:
    import matplotlib
    import matplotlib.pyplot as plt

    matplotlib.use("Agg")  # Use Agg backend, which is a non-interactive backend
    plt.ioff()
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Plots will be skipped.")


import scanpy as sc
from dotenv import load_dotenv

# Add package path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python"))

from mllmcelltype.consensus import interactive_consensus_annotation

# Load API keys from .env file
# Try to find .env file in various locations
env_path = None

# Try current directory
if os.path.exists(".env"):
    env_path = ".env"

# Try parent directories
if not env_path:
    current_dir = os.path.abspath(os.getcwd())
    for _ in range(3):  # Check up to 3 parent directories
        parent_dir = os.path.dirname(current_dir)
        potential_path = os.path.join(parent_dir, ".env")
        if os.path.exists(potential_path):
            env_path = potential_path
            break
        if parent_dir == current_dir:  # Reached root directory
            break
        current_dir = parent_dir

# Try package directory
if not env_path:
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    potential_path = os.path.join(package_dir, ".env")
    if os.path.exists(potential_path):
        env_path = potential_path

if env_path:
    load_dotenv(env_path)
    print(f"Loaded environment variables from {env_path}")
else:
    print("No .env file found. Please set API keys as environment variables.")

# Set up logging

logging.basicConfig(level=logging.INFO)


# Download example data
def download_example_data():
    """Download example dataset"""
    print("Downloading example data...")
    # Use scanpy's built-in PBMC dataset
    adata = sc.datasets.pbmc3k()
    return adata


# Preprocess data
def preprocess_data(adata):
    """Preprocess single-cell data"""
    print("Preprocessing data...")
    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_genes(adata, min_cells=3)

    # Calculate quality control metrics
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)

    # Filter cells
    adata = adata[adata.obs.n_genes_by_counts < 2500, :]
    adata = adata[adata.obs.pct_counts_mt < 5, :]

    # Normalize and log-transform
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # Select highly variable genes
    sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
    adata = adata[:, adata.var.highly_variable]

    # Scale data
    sc.pp.scale(adata, max_value=10)

    # Dimensionality reduction and clustering
    sc.tl.pca(adata, svd_solver="arpack")
    sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=0.5)

    print(f"Identified {len(adata.obs['leiden'].unique())} clusters")
    return adata


# Find marker genes for each cluster
def find_marker_genes(adata):
    """Find marker genes for each cluster"""
    print("Finding marker genes...")
    sc.tl.rank_genes_groups(adata, "leiden", method="wilcoxon")

    # Extract top 10 marker genes for each cluster
    marker_genes = {}
    for i in range(len(adata.obs["leiden"].unique())):
        cluster_id = str(i)
        markers = [gene for gene in adata.uns["rank_genes_groups"]["names"][cluster_id][:20]]
        marker_genes[cluster_id] = markers
        print(f"Cluster {cluster_id} markers: {', '.join(markers[:3])}...")

    return marker_genes


def main():
    # Download and preprocess data
    adata = download_example_data()
    adata = preprocess_data(adata)
    marker_genes = find_marker_genes(adata)

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
        models.append("gpt-4o")
    if "anthropic" in api_keys:
        models.append("claude-3-5-sonnet-latest")
    if "gemini" in api_keys:
        models.append("gemini-2.5-pro")
    if "qwen" in api_keys:
        models.append("qwen-max")

    print(f"Using models: {', '.join(models)}")

    # Set consensus threshold to 1.0, only complete agreement is considered consensus
    consensus_threshold = 1.0  # Set to the highest threshold

    # Configure LangExtract with balanced configuration for complex discussion parsing
    langextract_config = {
        "enabled": True,
        "model": "gemini-2.0-flash-exp",
        "complexity_threshold": 0.6,  # Balanced threshold for discussion complexity
        "fallback_enabled": True,
        "cache_enabled": True,
        "api_timeout": 30,
        "max_retries": 3,
        "chunk_size": 1000,
        "overlap_size": 100,
        "min_confidence": 0.6,
        "extraction_method": "structured",
        "output_format": "json",
        "debug_mode": False
    }

    print("\nRunning consensus annotation with discussion mode (high threshold) and LangExtract...")
    print("LangExtract Configuration:")
    for key, value in langextract_config.items():
        print(f"  {key}: {value}")
    
    # Run consensus annotation with LangExtract enabled
    consensus_results = interactive_consensus_annotation(
        marker_genes=marker_genes,
        species="human",
        models=models,
        api_keys=api_keys,
        tissue="blood",
        consensus_threshold=consensus_threshold,  # Use high threshold
        max_discussion_rounds=5,  # Maximum 5 rounds of discussion
        use_cache=False,  # Disable cache for fresh test
        verbose=True,
        use_langextract=True,  # Enable LangExtract
        langextract_config=langextract_config  # Use balanced config
    )

    # Extract final annotations
    final_annotations = consensus_results["consensus"]

    # Add consensus annotations to AnnData object
    adata.obs["consensus_cell_type"] = adata.obs["leiden"].astype(str).map(final_annotations)

    # Add consensus proportion and entropy metrics to AnnData object
    adata.obs["consensus_proportion"] = (
        adata.obs["leiden"].astype(str).map(consensus_results["consensus_proportion"])
    )
    adata.obs["entropy"] = adata.obs["leiden"].astype(str).map(consensus_results["entropy"])

    # Visualize results if matplotlib is available
    if MATPLOTLIB_AVAILABLE:
        plt.figure(figsize=(12, 10))
        sc.pl.umap(
            adata,
            color="consensus_cell_type",
            legend_loc="on data",
            save="_consensus_annotation.png",
        )
        sc.pl.umap(adata, color="consensus_proportion", save="_consensus_proportion.png")
        sc.pl.umap(adata, color="entropy", save="_entropy.png")

        print("\nResults saved as:")
        print("- figures/umap_consensus_annotation.png")
        print("- figures/umap_consensus_proportion.png")
        print("- figures/umap_entropy.png")
    else:
        print("\nSkipping visualization (matplotlib not available)")

    # Print consensus annotations and uncertainty metrics
    print("\nConsensus annotations with uncertainty metrics:")
    for cluster in sorted(final_annotations.keys(), key=int):
        cp = consensus_results["consensus_proportion"][cluster]
        entropy = consensus_results["entropy"][cluster]
        print(
            f"Cluster {cluster}: {final_annotations[cluster]} (CP: {cp:.2f}, Entropy: {entropy:.2f})"
        )

    # Print detailed discussion analysis
    print("\n" + "="*80)
    print("DISCUSSION MODE ANALYSIS WITH LANGEXTRACT")
    print("="*80)
    
    discussion_logs = consensus_results.get("discussion_logs", {})
    langextract_metrics = consensus_results.get("langextract_metrics", {})
    
    if discussion_logs:
        print(f"\nFound discussions for {len(discussion_logs)} controversial clusters")
        
        for cluster, logs in discussion_logs.items():
            print(f"\n{'='*60}")
            print(f"CLUSTER {cluster} DISCUSSION ANALYSIS")
            print(f"{'='*60}")
            
            print(f"Total discussion rounds: {len(logs)}")
            
            # Show each round
            for round_num, log in enumerate(logs):
                print(f"\n--- Round {round_num + 1} ---")
                print(f"Discussion length: {len(log)} characters")
                
                # Show first 300 characters of each round for analysis
                print("Discussion excerpt:")
                print(f"  {log[:300]}...")
                
                # Check if LangExtract was used in this round
                if "langextract" in log.lower():
                    print("  ✓ LangExtract processing detected in this round")
                
            # Show LangExtract metrics for this cluster if available
            if cluster in langextract_metrics:
                cluster_metrics = langextract_metrics[cluster]
                print(f"\nLangExtract Performance for Cluster {cluster}:")
                for metric, value in cluster_metrics.items():
                    print(f"  {metric}: {value}")
    else:
        print("No discussion logs found - all clusters reached consensus quickly.")
    
    # Overall LangExtract performance summary
    if langextract_metrics:
        print(f"\n{'='*60}")
        print("LANGEXTRACT OVERALL PERFORMANCE")
        print(f"{'='*60}")
        
        # Calculate aggregate metrics
        total_extractions = sum(metrics.get('extraction_count', 0) for metrics in langextract_metrics.values())
        total_parsing_time = sum(metrics.get('parsing_time', 0) for metrics in langextract_metrics.values())
        successful_extractions = sum(1 for metrics in langextract_metrics.values() if metrics.get('success', False))
        
        print(f"Total LangExtract calls: {total_extractions}")
        print(f"Successful extractions: {successful_extractions}")
        print(f"Success rate: {(successful_extractions/len(langextract_metrics)*100):.1f}%")
        print(f"Total parsing time: {total_parsing_time:.2f}s")
        print(f"Average parsing time per cluster: {(total_parsing_time/len(langextract_metrics)):.2f}s")
    
    # Analyze consensus quality with LangExtract
    print(f"\n{'='*60}")
    print("CONSENSUS QUALITY ANALYSIS")
    print(f"{'='*60}")
    
    high_confidence_clusters = [c for c, cp in consensus_results["consensus_proportion"].items() if cp >= 0.8]
    medium_confidence_clusters = [c for c, cp in consensus_results["consensus_proportion"].items() if 0.6 <= cp < 0.8]
    low_confidence_clusters = [c for c, cp in consensus_results["consensus_proportion"].items() if cp < 0.6]
    
    print(f"High confidence clusters (CP ≥ 0.8): {len(high_confidence_clusters)} - {high_confidence_clusters}")
    print(f"Medium confidence clusters (0.6 ≤ CP < 0.8): {len(medium_confidence_clusters)} - {medium_confidence_clusters}")
    print(f"Low confidence clusters (CP < 0.6): {len(low_confidence_clusters)} - {low_confidence_clusters}")
    
    # Check which clusters had discussions vs high confidence
    discussed_clusters = set(discussion_logs.keys())
    high_conf_no_discussion = [c for c in high_confidence_clusters if c not in discussed_clusters]
    low_conf_with_discussion = [c for c in low_confidence_clusters if c in discussed_clusters]
    
    print(f"\nHigh confidence without discussion: {high_conf_no_discussion}")
    print(f"Low confidence despite discussion: {low_conf_with_discussion}")
    
    if low_conf_with_discussion:
        print("\n⚠️  Clusters with persistent disagreement despite discussion - potential areas for improvement")

    # Save comprehensive results with LangExtract analysis
    result_file = "langextract_discussion_results.txt"
    with open(result_file, "w") as f:
        f.write("LANGEXTRACT DISCUSSION MODE TEST RESULTS\n")
        f.write("="*50 + "\n\n")
        
        # Configuration
        f.write("LangExtract Configuration:\n")
        for key, value in langextract_config.items():
            f.write(f"  {key}: {value}\n")
        f.write(f"\nConsensus Threshold: {consensus_threshold}\n")
        f.write(f"Max Discussion Rounds: 5\n")
        f.write(f"Models Used: {', '.join(models)}\n\n")
        
        # Summary table
        f.write("CLUSTER ANNOTATIONS SUMMARY\n")
        f.write("-"*80 + "\n")
        f.write("Cluster\tCell Type\tConsensus Proportion\tEntropy\tHad Discussion\n")
        for cluster in sorted(final_annotations.keys(), key=int):
            cp = consensus_results["consensus_proportion"][cluster]
            entropy = consensus_results["entropy"][cluster]
            had_discussion = "Yes" if cluster in discussion_logs else "No"
            f.write(f"{cluster}\t{final_annotations[cluster]}\t{cp:.2f}\t{entropy:.2f}\t{had_discussion}\n")
        
        # Consensus quality analysis
        f.write(f"\n\nCONSENSUS QUALITY ANALYSIS\n")
        f.write("-"*80 + "\n")
        f.write(f"High confidence clusters (CP ≥ 0.8): {len(high_confidence_clusters)}\n")
        f.write(f"Medium confidence clusters (0.6 ≤ CP < 0.8): {len(medium_confidence_clusters)}\n")
        f.write(f"Low confidence clusters (CP < 0.6): {len(low_confidence_clusters)}\n")
        f.write(f"Clusters requiring discussion: {len(discussion_logs)}\n")
        
        # LangExtract performance
        if langextract_metrics:
            f.write(f"\n\nLANGEXTRACT PERFORMANCE SUMMARY\n")
            f.write("-"*80 + "\n")
            total_extractions = sum(metrics.get('extraction_count', 0) for metrics in langextract_metrics.values())
            total_parsing_time = sum(metrics.get('parsing_time', 0) for metrics in langextract_metrics.values())
            successful_extractions = sum(1 for metrics in langextract_metrics.values() if metrics.get('success', False))
            
            f.write(f"Total LangExtract calls: {total_extractions}\n")
            f.write(f"Successful extractions: {successful_extractions}\n")
            f.write(f"Success rate: {(successful_extractions/len(langextract_metrics)*100):.1f}%\n")
            f.write(f"Total parsing time: {total_parsing_time:.2f}s\n")
            f.write(f"Average parsing time per cluster: {(total_parsing_time/len(langextract_metrics)):.2f}s\n")

        # Detailed discussion logs
        f.write(f"\n\nDETAILED DISCUSSION LOGS\n")
        f.write("="*80 + "\n")
        if discussion_logs:
            for cluster, logs in discussion_logs.items():
                f.write(f"\nCLUSTER {cluster} DISCUSSION ({len(logs)} rounds)\n")
                f.write("-"*60 + "\n")
                
                # LangExtract metrics for this cluster
                if cluster in langextract_metrics:
                    f.write("LangExtract Metrics:\n")
                    cluster_metrics = langextract_metrics[cluster]
                    for metric, value in cluster_metrics.items():
                        f.write(f"  {metric}: {value}\n")
                    f.write("\n")
                
                for round_num, log in enumerate(logs):
                    f.write(f"Round {round_num + 1} ({len(log)} characters):\n")
                    f.write(f"{log}\n")
                    f.write("-"*40 + "\n")
        else:
            f.write("No discussions were triggered - all clusters reached consensus quickly.\n")

    print(f"\nComprehensive results saved to {result_file}")
    print("\nTest completed successfully!")


if __name__ == "__main__":
    main()
