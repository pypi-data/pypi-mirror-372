#!/usr/bin/env python3
"""
Test script for mLLMCelltype with Scanpy integration and LangExtract.
Uses API keys from environment variables and tests LangExtract performance.
"""

import os
import sys
import time
from typing import Dict, Any

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

# Add python directory to path for local development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "python")))

# Import mLLMCelltype functions
from mllmcelltype import annotate_clusters, interactive_consensus_annotation, setup_logging
from mllmcelltype.langextract_config import load_langextract_config, print_langextract_config

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
setup_logging()

# Download and load example data (PBMC dataset)
print("Downloading example data...")
adata = sc.datasets.pbmc3k()
print(f"Loaded dataset with {adata.shape[0]} cells and {adata.shape[1]} genes")

# Preprocess the data
print("Preprocessing data...")
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, svd_solver="arpack")
sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)
print(f"Identified {len(adata.obs['leiden'].cat.categories)} clusters")

# Run differential expression analysis to get marker genes
print("Finding marker genes...")
sc.tl.rank_genes_groups(adata, "leiden", method="wilcoxon")

# Extract marker genes for each cluster
marker_genes = {}
for i in range(len(adata.obs["leiden"].cat.categories)):
    # Extract top 10 genes for each cluster
    genes = [adata.uns["rank_genes_groups"]["names"][str(i)][j] for j in range(10)]
    marker_genes[str(i)] = genes
    print(f"Cluster {i} markers: {', '.join(genes[:3])}...")

# Check if API keys are available
api_keys = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "QWEN_API_KEY": os.getenv("QWEN_API_KEY"),
}

available_apis = [k for k, v in api_keys.items() if v]
print(f"Available API keys: {', '.join(available_apis)}")

# Set up LangExtract configuration
langextract_config = load_langextract_config({
    "enabled": True,
    "model": "gemini-2.0-flash-exp",
    "complexity_threshold": 0.7,
    "api_timeout": 30,
    "max_retries": 3,
    "debug_mode": True
})

print("\nLangExtract Configuration:")
print_langextract_config(langextract_config)

if not available_apis:
    print("No API keys found in .env file. Please add your API keys.")
    sys.exit(1)

# Determine which models to use based on available API keys (updated to latest models)
models = []
if os.getenv("OPENAI_API_KEY"):
    models.append("gpt-4o-mini")
if os.getenv("ANTHROPIC_API_KEY"):
    models.append("claude-3-5-haiku-latest")
if os.getenv("GEMINI_API_KEY"):
    models.append("gemini-2.0-flash-exp")
if os.getenv("QWEN_API_KEY"):
    models.append("qwen-max")

print(f"Using models: {', '.join(models)}")

# Initialize timing variables to avoid undefined variables
traditional_time = 0
langextract_time = 0
similarity = 0

# Test single model annotation even if we have multiple models
if len(models) >= 1:
    print(f"\nTesting single model annotation with first model: {models[0]}...")
    provider = (
        "openai"
        if "gpt" in models[0]
        else "anthropic"
        if "claude" in models[0]
        else "gemini"
        if "gemini" in models[0]
        else "qwen"
    )
    
    # Test traditional annotation
    print("Running traditional annotation...")
    start_time = time.time()
    annotations_traditional = annotate_clusters(
        marker_genes=marker_genes,
        species="human",
        tissue="blood",
        provider=provider,
        model=models[0],
        use_langextract=False
    )
    traditional_time = time.time() - start_time
    print(f"Traditional annotation completed in {traditional_time:.2f} seconds")
    
    # Test LangExtract annotation
    print("Running LangExtract annotation...")
    start_time = time.time()
    annotations_langextract = annotate_clusters(
        marker_genes=marker_genes,
        species="human",
        tissue="blood",
        provider=provider,
        model=models[0],
        use_langextract=True,
        langextract_config=langextract_config
    )
    langextract_time = time.time() - start_time
    print(f"LangExtract annotation completed in {langextract_time:.2f} seconds")
    print(f"Time difference: {langextract_time - traditional_time:.2f} seconds")
    
    # Calculate similarity
    same_annotations = sum(1 for c in annotations_traditional.keys() if annotations_traditional[c] == annotations_langextract[c])
    total_clusters = len(annotations_traditional)
    similarity = same_annotations / total_clusters * 100
    
    print(f"\nSingle model annotation comparison:")
    print("Cluster\tTraditional\t\tLangExtract")
    print("-" * 60)
    for cluster in sorted(annotations_traditional.keys(), key=int):
        trad = annotations_traditional[cluster][:20] + "..." if len(annotations_traditional[cluster]) > 20 else annotations_traditional[cluster]
        lang = annotations_langextract[cluster][:20] + "..." if len(annotations_langextract[cluster]) > 20 else annotations_langextract[cluster]
        print(f"{cluster}\t{trad:<20}\t{lang}")
    
    print(f"\nAnnotation similarity: {similarity:.1f}% ({same_annotations}/{total_clusters} clusters identical)")

if len(models) < 2:
    print("Warning: For consensus annotation, at least 2 models are recommended.")
    if len(models) == 0:
        print("No models available. Please add API keys to environment variables.")
        sys.exit(1)
    else:
        print("Continuing with available models...")
        
# Add single model annotations to AnnData object if they exist
if 'annotations_traditional' in locals():
    adata.obs["cell_type_traditional"] = adata.obs["leiden"].astype(str).map(annotations_traditional)
    adata.obs["cell_type_langextract"] = adata.obs["leiden"].astype(str).map(annotations_langextract)

# Run consensus annotation with multiple models - traditional vs LangExtract
print("\nRunning consensus annotation with multiple models...")
print("Testing traditional consensus annotation...")
start_time = time.time()

consensus_results_traditional = interactive_consensus_annotation(
    marker_genes=marker_genes,
    species="human",
    tissue="blood",
    models=models,
    consensus_threshold=0.7,
    max_discussion_rounds=3,
    verbose=True,
    use_langextract=False
)
traditional_consensus_time = time.time() - start_time

print(f"\nTesting LangExtract consensus annotation...")
start_time = time.time()

consensus_results_langextract = interactive_consensus_annotation(
    marker_genes=marker_genes,
    species="human",
    tissue="blood",
    models=models,
    consensus_threshold=0.7,
    max_discussion_rounds=3,
    verbose=True,
    use_langextract=True,
    langextract_config=langextract_config
)
langextract_consensus_time = time.time() - start_time

print(f"\nConsensus annotation time comparison:")
print(f"Traditional: {traditional_consensus_time:.2f} seconds")
print(f"LangExtract: {langextract_consensus_time:.2f} seconds")
print(f"Difference: {langextract_consensus_time - traditional_consensus_time:.2f} seconds")

# Access the final consensus annotations from both methods
final_annotations_traditional = consensus_results_traditional["consensus"]
final_annotations_langextract = consensus_results_langextract["consensus"]

# Add consensus annotations to AnnData object
adata.obs["consensus_traditional"] = adata.obs["leiden"].astype(str).map(final_annotations_traditional)
adata.obs["consensus_langextract"] = adata.obs["leiden"].astype(str).map(final_annotations_langextract)

# Add consensus metrics for both methods
adata.obs["consensus_proportion_trad"] = (
    adata.obs["leiden"].astype(str).map(consensus_results_traditional["consensus_proportion"])
)
adata.obs["entropy_trad"] = adata.obs["leiden"].astype(str).map(consensus_results_traditional["entropy"])

adata.obs["consensus_proportion_lang"] = (
    adata.obs["leiden"].astype(str).map(consensus_results_langextract["consensus_proportion"])
)
adata.obs["entropy_lang"] = adata.obs["leiden"].astype(str).map(consensus_results_langextract["entropy"])

# Visualize results if matplotlib is available
if MATPLOTLIB_AVAILABLE:
    plt.figure(figsize=(15, 12))
    
    # Traditional vs LangExtract consensus
    sc.pl.umap(
        adata, color="consensus_traditional", legend_loc="on data", save="_consensus_traditional.png"
    )
    sc.pl.umap(
        adata, color="consensus_langextract", legend_loc="on data", save="_consensus_langextract.png"
    )
    
    # Consensus metrics comparison
    sc.pl.umap(adata, color="consensus_proportion_trad", save="_consensus_proportion_traditional.png")
    sc.pl.umap(adata, color="consensus_proportion_lang", save="_consensus_proportion_langextract.png")
    sc.pl.umap(adata, color="entropy_trad", save="_entropy_traditional.png")
    sc.pl.umap(adata, color="entropy_lang", save="_entropy_langextract.png")

    print("\nResults saved as:")
    print("- figures/umap_consensus_traditional.png")
    print("- figures/umap_consensus_langextract.png")
    print("- figures/umap_consensus_proportion_traditional.png")
    print("- figures/umap_consensus_proportion_langextract.png")
    print("- figures/umap_entropy_traditional.png")
    print("- figures/umap_entropy_langextract.png")
else:
    print("\nSkipping visualization (matplotlib not available)")

# Print consensus annotations comparison with uncertainty metrics
print("\nConsensus annotations comparison with uncertainty metrics:")
print("\nTraditional Consensus:")
for cluster in sorted(final_annotations_traditional.keys(), key=int):
    cp = consensus_results_traditional["consensus_proportion"][cluster]
    entropy = consensus_results_traditional["entropy"][cluster]
    print(f"Cluster {cluster}: {final_annotations_traditional[cluster]} (CP: {cp:.2f}, Entropy: {entropy:.2f})")

print("\nLangExtract Consensus:")
for cluster in sorted(final_annotations_langextract.keys(), key=int):
    cp = consensus_results_langextract["consensus_proportion"][cluster]
    entropy = consensus_results_langextract["entropy"][cluster]
    print(f"Cluster {cluster}: {final_annotations_langextract[cluster]} (CP: {cp:.2f}, Entropy: {entropy:.2f})")

# Calculate consensus similarity
consensus_same = sum(1 for c in final_annotations_traditional.keys() 
                    if final_annotations_traditional[c] == final_annotations_langextract[c])
consensus_total = len(final_annotations_traditional)
consensus_similarity = consensus_same / consensus_total * 100
print(f"\nConsensus similarity: {consensus_similarity:.1f}% ({consensus_same}/{consensus_total} clusters identical)")

# Calculate average metrics
avg_cp_trad = sum(consensus_results_traditional["consensus_proportion"].values()) / len(consensus_results_traditional["consensus_proportion"])
avg_entropy_trad = sum(consensus_results_traditional["entropy"].values()) / len(consensus_results_traditional["entropy"])
avg_cp_lang = sum(consensus_results_langextract["consensus_proportion"].values()) / len(consensus_results_langextract["consensus_proportion"])
avg_entropy_lang = sum(consensus_results_langextract["entropy"].values()) / len(consensus_results_langextract["entropy"])

print(f"\nAverage Metrics Comparison:")
print(f"Traditional - CP: {avg_cp_trad:.3f}, Entropy: {avg_entropy_trad:.3f}")
print(f"LangExtract - CP: {avg_cp_lang:.3f}, Entropy: {avg_entropy_lang:.3f}")

# Save comprehensive results
result_file = "langextract_comparison_results.txt"
with open(result_file, "w") as f:
    f.write("LangExtract vs Traditional Annotation Comparison Report\n")
    f.write("=" * 60 + "\n\n")
    
    f.write("PERFORMANCE METRICS:\n")
    f.write(f"Traditional annotation time: {traditional_time:.2f}s (single model)\n")
    f.write(f"LangExtract annotation time: {langextract_time:.2f}s (single model)\n")
    f.write(f"Traditional consensus time: {traditional_consensus_time:.2f}s\n")
    f.write(f"LangExtract consensus time: {langextract_consensus_time:.2f}s\n\n")
    
    f.write("ANNOTATION SIMILARITY:\n")
    f.write(f"Single model similarity: {similarity:.1f}%\n")
    f.write(f"Consensus similarity: {consensus_similarity:.1f}%\n\n")
    
    f.write("UNCERTAINTY METRICS:\n")
    f.write(f"Traditional avg CP: {avg_cp_trad:.3f}, avg Entropy: {avg_entropy_trad:.3f}\n")
    f.write(f"LangExtract avg CP: {avg_cp_lang:.3f}, avg Entropy: {avg_entropy_lang:.3f}\n\n")
    
    f.write("DETAILED CLUSTER ANNOTATIONS:\n")
    f.write("Cluster\tTraditional\tLangExtract\tTrad_CP\tTrad_Entropy\tLang_CP\tLang_Entropy\n")
    for cluster in sorted(final_annotations_traditional.keys(), key=int):
        trad_cp = consensus_results_traditional["consensus_proportion"][cluster]
        trad_entropy = consensus_results_traditional["entropy"][cluster]
        lang_cp = consensus_results_langextract["consensus_proportion"][cluster]
        lang_entropy = consensus_results_langextract["entropy"][cluster]
        f.write(f"{cluster}\t{final_annotations_traditional[cluster]}\t{final_annotations_langextract[cluster]}\t{trad_cp:.3f}\t{trad_entropy:.3f}\t{lang_cp:.3f}\t{lang_entropy:.3f}\n")

print(f"\nComprehensive results saved to {result_file}")

# Final summary
print("\n" + "=" * 60)
print("LANGEXTRACT INTEGRATION TEST SUMMARY")
print("=" * 60)
print(f"✓ Tested {len(models)} models: {', '.join(models)}")
print(f"✓ Processed {len(marker_genes)} clusters from PBMC dataset")
print(f"✓ Single model annotation similarity: {similarity:.1f}%")
print(f"✓ Consensus annotation similarity: {consensus_similarity:.1f}%")
print(f"✓ LangExtract configuration: {langextract_config['model']} with threshold {langextract_config['complexity_threshold']}")
print(f"✓ Performance impact: {langextract_time - traditional_time:+.2f}s (single), {langextract_consensus_time - traditional_consensus_time:+.2f}s (consensus)")
print("\nTest completed successfully!")
