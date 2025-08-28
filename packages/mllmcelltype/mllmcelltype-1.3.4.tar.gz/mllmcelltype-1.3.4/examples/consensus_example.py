#!/usr/bin/env python
"""
Test script for LLM consensus annotation functionality with LangExtract integration.
"""

import os
import sys
from typing import Dict

# Add the package directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mllmcelltype.consensus import check_consensus, interactive_consensus_annotation
from mllmcelltype.utils import find_agreement

# Sample data for testing
test_predictions = {
    "model1": {"cluster1": "T cells", "cluster2": "B cells", "cluster3": "Macrophages"},
    "model2": {"cluster1": "CD4+ T cells", "cluster2": "B lymphocytes", "cluster3": "Monocytes"},
    "model3": {
        "cluster1": "T lymphocytes",
        "cluster2": "B cells",
        "cluster3": "Tissue-resident macrophages",
    },
}

# Test with different levels of agreement
test_predictions_with_disagreement = {
    "model1": {
        "cluster1": "T cells",
        "cluster2": "B cells",
        "cluster3": "Macrophages",
        "cluster4": "Dendritic cells",
    },
    "model2": {
        "cluster1": "CD4+ T cells",
        "cluster2": "B lymphocytes",
        "cluster3": "Monocytes",
        "cluster4": "Plasmacytoid dendritic cells",
    },
    "model3": {
        "cluster1": "T lymphocytes",
        "cluster2": "B cells",
        "cluster3": "Tissue-resident macrophages",
        "cluster4": "Natural killer cells",
    },
}


def print_results(
    title: str,
    consensus: Dict[str, str],
    consensus_proportion: Dict[str, float],
    entropy: Dict[str, float],
) -> None:
    """Print the results in a formatted way."""
    print(f"\n=== {title} ===")
    print(f"{'Cluster':<10} {'Consensus':<30} {'Proportion':<10} {'Entropy':<10}")
    print("-" * 60)

    for cluster in sorted(consensus.keys()):
        print(
            f"{cluster:<10} {consensus[cluster]:<30} {consensus_proportion[cluster]:.2f}      {entropy[cluster]:.2f}"
        )


def test_langextract_configurations():
    """Test different LangExtract configurations."""
    print("\n=== Testing LangExtract Configurations ===")
    
    # Test data with marker genes for interactive consensus
    marker_genes = {
        "cluster1": ["CD3E", "CD3D", "IL7R", "LDHB"],
        "cluster2": ["MS4A1", "CD79A", "CD79B", "IGHM"],
        "cluster3": ["LYZ", "S100A9", "S100A8", "FCN1"],
        "cluster4": ["NKG7", "GNLY", "GZMA", "GZMB"]
    }
    
    # Define models to test
    test_models = [
        {"provider": "openai", "model": "gpt-4o-mini"},
        {"provider": "anthropic", "model": "claude-3-5-haiku-latest"}
    ]
    
    # API keys - try environment variables first, then fall back to manual values
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY") or "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",
        "anthropic": os.getenv("ANTHROPIC_API_KEY") or "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",
        "qwen": os.getenv("QWEN_API_KEY") or "sk-4d1266fd8cac4ef7a36efe0c628d68a6",
        "gemini": os.getenv("GEMINI_API_KEY") or "AIzaSyDqD_trJuYDSIYO1TWHlOCveV9qQXUJ6uE"
    }
    
    # Filter out models without API keys
    available_models = []
    for model in test_models:
        provider = model["provider"]
        if api_keys.get(provider):
            available_models.append(model)
            print(f"✓ {provider} API key available")
        else:
            print(f"✗ {provider} API key missing")
    
    if not available_models:
        print("No API keys available for testing!")
        return
    
    # Test configurations
    configs_to_test = [
        {"name": "No LangExtract", "use_langextract": False, "config": None},
        {"name": "Conservative LangExtract", "use_langextract": True, "config": {"mode": "conservative"}},
        {"name": "Balanced LangExtract", "use_langextract": True, "config": {"mode": "balanced"}},
        {"name": "Aggressive LangExtract", "use_langextract": True, "config": {"mode": "aggressive"}}
    ]
    
    results = {}
    
    for config in configs_to_test:
        print(f"\n--- Testing {config['name']} ---")
        
        try:
            # Run interactive consensus annotation
            result = interactive_consensus_annotation(
                marker_genes=marker_genes,
                species="human",
                models=available_models[:2],  # Use first 2 available models
                api_keys=api_keys,
                tissue="PBMC",
                consensus_threshold=0.6,
                entropy_threshold=1.0,
                max_discussion_rounds=2,
                use_cache=False,  # Disable cache for testing
                verbose=True,
                use_langextract=config["use_langextract"],
                langextract_config=config["config"]
            )
            
            results[config["name"]] = result
            
            # Print results summary
            consensus = result.get("consensus", {})
            cp = result.get("consensus_proportion", {})
            entropy = result.get("entropy", {})
            controversial = result.get("controversial_clusters", [])
            
            print(f"Results for {config['name']}:")
            print(f"  Controversial clusters: {len(controversial)}")
            for cluster_id, annotation in consensus.items():
                cp_val = cp.get(cluster_id, 0)
                ent_val = entropy.get(cluster_id, 0)
                print(f"  {cluster_id}: {annotation} (CP: {cp_val:.2f}, H: {ent_val:.2f})")
                
        except Exception as e:
            print(f"Error testing {config['name']}: {str(e)}")
            results[config["name"]] = {"error": str(e)}
    
    return results


def main():
    print("Testing LLM Consensus Annotation with LangExtract Integration")
    print("============================================================")

    # Create a custom simple version of the consensus check prompt function
    def simple_consensus_check_prompt(annotations):
        prompt = """You are an expert in single-cell RNA-seq analysis and cell type annotation.

I need you to analyze the following cell type annotations from different models for the same cluster and determine if there is a consensus.

The annotations are:
{annotations}

Please analyze these annotations and determine:
1. If there is a consensus (1 for yes, 0 for no)
2. The consensus proportion (between 0 and 1)
3. An entropy value measuring the diversity of opinions (higher means more diverse)
4. The best consensus annotation

Respond with exactly 4 lines:
Line 1: 0 or 1 (consensus reached?)
Line 2: Consensus proportion (e.g., 0.75)
Line 3: Entropy value (e.g., 0.85)
Line 4: The consensus cell type (or most likely if no clear consensus)

Only output these 4 lines, nothing else."""

        # Format the annotations
        formatted_annotations = "\n".join([f"- {anno}" for anno in annotations])

        # Replace the placeholder
        prompt = prompt.replace("{annotations}", formatted_annotations)

        return prompt

    # Test prompt generation
    test_annotations = ["T cells", "CD4+ T cells", "T lymphocytes"]
    prompt = simple_consensus_check_prompt(test_annotations)
    print("\nGenerated prompt for consensus check:")
    print(prompt)

    # Test find_agreement function
    print("\nTesting find_agreement function:")
    consensus, consensus_proportion, entropy = find_agreement(test_predictions)
    print_results("Results from find_agreement", consensus, consensus_proportion, entropy)

    # Test check_consensus function without LangExtract
    print("\nTesting check_consensus function (Traditional Mode):")
    consensus, consensus_proportion, entropy, controversial = check_consensus(test_predictions)
    print_results("Traditional Mode Results", consensus, consensus_proportion, entropy)

    # Test with disagreement
    print("\nTesting with disagreement (Traditional Mode):")
    consensus, consensus_proportion, entropy, controversial = check_consensus(
        test_predictions_with_disagreement
    )
    print_results("Traditional Mode with Disagreement", consensus, consensus_proportion, entropy)
    print(f"Controversial clusters: {controversial}")

    # Test API key availability - try environment variables first, then fall back to manual values
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY") or "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",
        "anthropic": os.getenv("ANTHROPIC_API_KEY") or "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",
        "qwen": os.getenv("QWEN_API_KEY") or "sk-4d1266fd8cac4ef7a36efe0c628d68a6",
        "gemini": os.getenv("GEMINI_API_KEY") or "AIzaSyDqD_trJuYDSIYO1TWHlOCveV9qQXUJ6uE"
    }
    
    available_apis = [k for k, v in api_keys.items() if v]
    print(f"\nAvailable API keys: {available_apis}")

    # Test LLM consensus with different LangExtract configurations
    if available_apis:
        print("\n=== Testing LLM Consensus with LangExtract ===")
        
        # Test with LangExtract enabled
        try:
            print("\nTesting check_consensus with LangExtract (Conservative Mode):")
            consensus, consensus_proportion, entropy = check_consensus(
                test_predictions, 
                return_controversial=False,
                api_keys=api_keys
            )
            print_results(
                "LangExtract Conservative Mode Results", consensus, consensus_proportion, entropy
            )
        except Exception as e:
            print(f"\nError testing check_consensus with LangExtract: {str(e)}")

        # Run comprehensive LangExtract configuration tests
        langextract_results = test_langextract_configurations()
        
        # Compare results
        print("\n=== LangExtract Configuration Comparison ===")
        for config_name, result in langextract_results.items():
            if "error" not in result:
                controversial_count = len(result.get("controversial_clusters", []))
                total_clusters = len(result.get("consensus", {}))
                print(f"{config_name}: {controversial_count}/{total_clusters} controversial clusters")
            else:
                print(f"{config_name}: Error - {result['error']}")
                
    else:
        print("\nNo API keys available for LLM testing!")
        print("Please set at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, QWEN_API_KEY, GEMINI_API_KEY")


if __name__ == "__main__":
    main()
