"""Main annotation module for LLMCellType."""

from __future__ import annotations

import os
import time
from typing import Optional, Union

import pandas as pd

from .functions import PROVIDER_FUNCTIONS
from .logger import setup_logging, write_log
from .prompts import create_batch_prompt, create_prompt
from .utils import (
    create_cache_key,
    format_results,
    load_api_key,
    load_from_cache,
    parse_marker_genes,
    save_to_cache,
)


def annotate_clusters(
    marker_genes: Union[dict[str, list[str]], pd.DataFrame],
    species: str,
    provider: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    tissue: Optional[str] = None,
    additional_context: Optional[str] = None,
    prompt_template: Optional[str] = None,
    use_cache: bool = True,
    cache_dir: Optional[str] = None,
    log_dir: Optional[str] = None,
    log_level: str = "INFO",
    base_urls: Optional[Union[str, dict[str, str]]] = None,
    use_langextract: Optional[bool] = None,
    langextract_config: Optional[dict] = None,
) -> dict[str, str]:
    """Annotate cell clusters using LLM.

    Args:
        marker_genes: Dictionary mapping cluster names to lists of marker genes,
                     or DataFrame with 'cluster' and 'gene' columns
        species: Species name (e.g., 'human', 'mouse')
        provider: LLM provider (e.g., 'openai', 'anthropic')
        model: Model name (e.g., 'gpt-4o', 'claude-3-opus-20240229')
        api_key: API key for the provider
        tissue: Tissue name (e.g., 'brain', 'liver')
        additional_context: Additional context to include in the prompt
        prompt_template: Custom prompt template
        use_cache: Whether to use cache
        cache_dir: Directory to store cache files
        log_dir: Directory to store log files
        log_level: Logging level
        base_urls: Custom base URLs for API endpoints. Can be:
                  - str: Single URL applied to all providers
                  - dict: Provider-specific URLs (e.g., {'openai': 'https://proxy.com/v1'})
        use_langextract: Whether to use langextract for enhanced output parsing.
                        If None, uses environment variable or default
        langextract_config: Configuration dictionary for langextract.
                           If None, uses default configuration

    Returns:
        Dict[str, str]: Dictionary mapping cluster names to annotations

    """
    # Setup logging
    setup_logging(log_dir=log_dir, log_level=log_level)
    write_log(f"Starting annotation with provider: {provider}")

    # Parse marker genes if DataFrame
    if isinstance(marker_genes, pd.DataFrame):
        marker_genes = parse_marker_genes(marker_genes)

    # Get clusters
    clusters = list(marker_genes.keys())
    write_log(f"Found {len(clusters)} clusters")

    # Set default model based on provider
    if not model:
        model = get_default_model(provider)
        write_log(f"Using default model for {provider}: {model}")
    
    # Handle langextract configuration with intelligent defaults
    final_langextract_config = _resolve_langextract_config_intelligent(
        model=model,
        provider=provider,
        use_langextract=use_langextract,
        langextract_config=langextract_config
    )

    # Get API key if not provided
    if not api_key:
        api_key = load_api_key(provider)
        if not api_key:
            error_msg = f"API key not found for provider: {provider}"
            write_log(f"ERROR: {error_msg}", level="error")
            raise ValueError(error_msg)

    # Create prompt
    prompt = create_prompt(
        marker_genes=marker_genes,
        species=species,
        tissue=tissue,
        additional_context=additional_context,
        prompt_template=prompt_template,
    )

    # Check cache
    if use_cache:
        cache_key = create_cache_key(prompt, model, provider)
        cached_results = load_from_cache(cache_key, cache_dir)
        if cached_results:
            write_log("Using cached results")
            return format_results(cached_results, clusters, langextract_config=final_langextract_config)

    # 解析base URL
    from .url_utils import resolve_provider_base_url

    base_url = resolve_provider_base_url(provider, base_urls)

    # Get provider function
    provider_func = PROVIDER_FUNCTIONS.get(provider.lower())
    if not provider_func:
        error_msg = f"Unknown provider: {provider}"
        write_log(f"ERROR: {error_msg}", level="error")
        raise ValueError(error_msg)

    # Process request
    try:
        write_log(f"Processing request with {provider} using model {model}")
        start_time = time.time()

        # Call provider function with base_url
        results = provider_func(prompt, model, api_key, base_url)

        end_time = time.time()
        write_log(f"Request processed in {end_time - start_time:.2f} seconds")

        # Save to cache
        if use_cache:
            save_to_cache(cache_key, results, cache_dir)

        # Format results
        return format_results(results, clusters, langextract_config=final_langextract_config)

    except Exception as e:
        error_msg = f"Error during annotation: {str(e)}"
        write_log(f"ERROR: {error_msg}", level="error")
        raise


def batch_annotate_clusters(
    marker_genes_list: list[Union[dict[str, list[str]], pd.DataFrame]],
    species: str,
    provider: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    tissue: Optional[Union[str, list[str]]] = None,
    additional_context: Optional[str] = None,
    prompt_template: Optional[str] = None,
    use_cache: bool = True,
    cache_dir: Optional[str] = None,
    log_dir: Optional[str] = None,
    log_level: str = "INFO",
    base_urls: Optional[Union[str, dict[str, str]]] = None,
    use_langextract: Optional[bool] = None,
    langextract_config: Optional[dict] = None,
) -> list[dict[str, str]]:
    """Batch annotate multiple sets of cell clusters using LLM.

    Args:
        marker_genes_list: List of dictionaries mapping cluster names to lists of
            marker genes, or list of DataFrames with 'cluster' and 'gene' columns
        species: Species name (e.g., 'human', 'mouse')
        provider: LLM provider (e.g., 'openai', 'anthropic')
        model: Model name (e.g., 'gpt-4o', 'claude-3-opus-20240229')
        api_key: API key for the provider
        tissue: Tissue name (e.g., 'brain', 'liver')
        additional_context: Additional context to include in the prompt
        prompt_template: Custom prompt template
        use_cache: Whether to use cache
        cache_dir: Directory to store cache files
        log_dir: Directory to store log files
        log_level: Logging level
        base_urls: Custom base URLs for API endpoints. Can be:
                  - str: Single URL applied to all providers
                  - dict: Provider-specific URLs (e.g., {'openai': 'https://proxy.com/v1'})
        use_langextract: Whether to use langextract for enhanced output parsing.
                        If None, uses environment variable or default
        langextract_config: Configuration dictionary for langextract.
                           If None, uses default configuration

    Returns:
        List[Dict[str, str]]: List of dictionaries mapping cluster names to annotations

    """
    # Setup logging
    setup_logging(log_dir=log_dir, log_level=log_level)
    write_log(f"Starting batch annotation with provider: {provider}")

    # Handle langextract configuration
    final_langextract_config = _resolve_langextract_config(
        use_langextract=use_langextract,
        langextract_config=langextract_config
    )

    # Parse marker genes if DataFrames
    parsed_marker_genes_list = []
    for marker_genes in marker_genes_list:
        if isinstance(marker_genes, pd.DataFrame):
            parsed_marker_genes_list.append(parse_marker_genes(marker_genes))
        else:
            parsed_marker_genes_list.append(marker_genes)

    # Get clusters for each set
    clusters_list = [list(marker_genes.keys()) for marker_genes in parsed_marker_genes_list]
    write_log(f"Found {len(clusters_list)} sets of clusters")

    # Set default model based on provider
    if not model:
        model = get_default_model(provider)
        write_log(f"Using default model for {provider}: {model}")

    # Get API key if not provided
    if not api_key:
        api_key = load_api_key(provider)
        if not api_key:
            error_msg = f"API key not found for provider: {provider}"
            write_log(f"ERROR: {error_msg}", level="error")
            raise ValueError(error_msg)

    # Create batch prompt
    # If tissue is a list, use the first one for the batch prompt
    # Individual tissues will be used when processing each dataset separately
    batch_tissue = tissue[0] if isinstance(tissue, list) and len(tissue) > 0 else tissue

    prompt = create_batch_prompt(
        marker_genes_list=parsed_marker_genes_list,
        species=species,
        tissue=batch_tissue,
        additional_context=additional_context,
        prompt_template=prompt_template,
    )

    # Check cache
    if use_cache:
        cache_key = create_cache_key(prompt, model, provider)
        cached_results = load_from_cache(cache_key, cache_dir)
        if cached_results:
            write_log("Using cached results")
            # Parse cached results into sets
            result_sets = []
            start_idx = 0
            for clusters in clusters_list:
                end_idx = start_idx + len(clusters)
                set_results = cached_results[start_idx:end_idx]
                result_sets.append(format_results(set_results, clusters, langextract_config=final_langextract_config))
                start_idx = end_idx
            return result_sets

    # Analyze base URL
    from .url_utils import resolve_provider_base_url

    base_url = resolve_provider_base_url(provider, base_urls)

    # Get provider function
    provider_func = PROVIDER_FUNCTIONS.get(provider.lower())
    if not provider_func:
        error_msg = f"Unknown provider: {provider}"
        write_log(f"ERROR: {error_msg}", level="error")
        raise ValueError(error_msg)

    # Process request
    try:
        write_log(f"Processing batch request with {provider} using model {model}")
        start_time = time.time()

        # Call provider function with base_url
        results = provider_func(prompt, model, api_key, base_url)

        end_time = time.time()
        write_log(f"Batch request processed in {end_time - start_time:.2f} seconds")

        # Save to cache
        if use_cache:
            save_to_cache(cache_key, results, cache_dir)

        # Parse results into sets
        # The LLM response format is typically:
        # Set 1:
        # Cluster 1: T cells
        # Cluster 2: B cells
        # ...
        #
        # Set 2:
        # ...

        # First, filter out empty lines and parse the results
        filtered_results = [line for line in results if line.strip()]

        # Initialize result sets
        result_sets = []
        current_set = None
        current_set_results = {}

        for line in filtered_results:
            line = line.strip()

            # Check if this is a set header
            if line.startswith("Set "):
                # If we have a current set, add it to results
                if current_set is not None and current_set_results:
                    result_sets.append(current_set_results)
                    current_set_results = {}

                # Extract set number
                try:
                    current_set = int(line.split()[1].rstrip(":")) - 1
                except (IndexError, ValueError):
                    current_set = len(result_sets)

            # Check if this is a cluster annotation
            elif line.startswith("Cluster "):
                try:
                    # Parse "Cluster X: Annotation"
                    parts = line.split(":", 1)
                    cluster_num = parts[0].split()[1]
                    annotation = parts[1].strip() if len(parts) > 1 else ""

                    # Add to current set results
                    if current_set is not None:
                        current_set_results[cluster_num] = annotation
                except (IndexError, ValueError):
                    write_log(f"Warning: Could not parse line: {line}", level="warning")

        # Add the last set if it exists
        if current_set is not None and current_set_results:
            result_sets.append(current_set_results)

        # Try to parse JSON format if present
        if not result_sets:
            try:
                # Join all results and try to parse as JSON
                full_text = "\n".join(filtered_results)

                # Try to find JSON in the text
                import json
                import re

                # Extract JSON content if it's wrapped in ```json and ``` markers
                json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", full_text)
                json_str = json_match.group(1) if json_match else None

                if not json_str:
                    # If no code blocks, try to find JSON object directly
                    json_match = re.search(r"(\{[\s\S]*\})", full_text)
                    json_str = json_match.group(1) if json_match else None

                if json_str:
                    try:
                        data = json.loads(json_str)

                        # Check if it's a batch response with sets
                        if "sets" in data and isinstance(data["sets"], list):
                            # Parse each set
                            for set_data in data["sets"]:
                                set_results = {}
                                if "clusters" in set_data and isinstance(
                                    set_data["clusters"], list
                                ):
                                    for cluster in set_data["clusters"]:
                                        if "id" in cluster and "cell_type" in cluster:
                                            set_results[str(cluster["id"])] = cluster["cell_type"]
                                    result_sets.append(set_results)
                        # Check if it's a batch response with annotations array
                        elif "annotations" in data and isinstance(data["annotations"], list):
                            # Group by set if specified
                            set_groups = {}
                            for annotation in data["annotations"]:
                                if (
                                    "set" in annotation
                                    and "cluster" in annotation
                                    and "cell_type" in annotation
                                ):
                                    set_id = annotation["set"]
                                    if set_id not in set_groups:
                                        set_groups[set_id] = {}
                                    set_groups[set_id][str(annotation["cluster"])] = annotation[
                                        "cell_type"
                                    ]

                            # Add all sets in order
                            for set_id in sorted(set_groups.keys()):
                                result_sets.append(set_groups[set_id])
                    except json.JSONDecodeError:
                        write_log("Warning: Failed to parse JSON response", level="warning")
            except (ValueError, KeyError, AttributeError, TypeError) as e:
                write_log(
                    f"Warning: Error while trying to parse JSON: {str(e)}",
                    level="warning",
                )

        # If we still didn't get any properly formatted results, fall back to the
        # old method
        if not result_sets:
            write_log(
                "Warning: Could not parse batch results, falling back to default parsing",
                level="warning",
            )
            result_sets = []
            for i, clusters in enumerate(clusters_list):
                result_sets.append(
                    {
                        str(cluster): f"Set {i + 1} results not properly parsed"
                        for cluster in clusters
                    }
                )

        return result_sets

    except Exception as e:
        error_msg = f"Error during batch annotation: {str(e)}"
        write_log(f"ERROR: {error_msg}", level="error")
        raise


def get_default_model(provider: str) -> str:
    """Get default model for a provider.

    Args:
        provider: Provider name

    Returns:
        str: Default model name

    """
    default_models = {
        "openai": "gpt-4.1",
        "anthropic": "claude-sonnet-4-20250514",
        "deepseek": "deepseek-chat",
        "gemini": "gemini-2.5-pro-preview-03-25",
        "qwen": "qwen-max-2025-01-25",
        "stepfun": "step-2-16k",
        "zhipu": "glm-4",
        "minimax": "MiniMax-Text-01",
        "grok": "grok-3-beta",
        "openrouter": "openai/gpt-4.1",
    }

    return default_models.get(provider.lower(), "unknown")


def get_model_response(
    prompt: str,
    provider: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    use_cache: bool = True,
    cache_dir: Optional[str] = None,
    base_url: Optional[str] = None,
) -> str:
    """Get response from a model for a given prompt.

    Args:
        prompt: The prompt to send to the model
        provider: The provider name (e.g., 'openai', 'anthropic')
        model: The model name. If None, uses the default model for the provider.
        api_key: The API key for the provider. If None, loads from environment.
        use_cache: Whether to use cache
        cache_dir: The cache directory
        base_url: Optional custom base URL

    Returns:
        str: The model response

    """

    # Check if provider is valid
    if not provider:
        raise ValueError("Provider name is required")

    # Set default model if not provided
    if not model:
        model = get_default_model(provider)
        write_log(f"Using default model for {provider}: {model}")

    # Get API key if not provided
    if not api_key:
        from .utils import load_api_key

        api_key = load_api_key(provider)
        if not api_key:
            error_msg = f"API key not found for provider: {provider}"
            write_log(f"ERROR: {error_msg}", level="error")
            raise ValueError(error_msg)

    # Check cache
    if use_cache:
        from .utils import create_cache_key, load_from_cache

        cache_key = create_cache_key(prompt, model, provider)
        cached_result = load_from_cache(cache_key, cache_dir)
        if cached_result:
            write_log(f"Using cached result for {model}")
            if isinstance(cached_result, list):
                return "\n".join(cached_result)
            return cached_result

    # Get provider function
    provider_func = PROVIDER_FUNCTIONS.get(provider.lower())
    if not provider_func:
        error_msg = f"Unknown provider: {provider}"
        write_log(f"ERROR: {error_msg}", level="error")
        raise ValueError(error_msg)

    # Call provider function
    try:
        write_log(f"Requesting response from {provider} ({model})")
        result = provider_func(prompt, model, api_key, base_url)

        # Save to cache
        if use_cache:
            from .utils import save_to_cache

            save_to_cache(cache_key, result, cache_dir)

        # Convert list to string if needed
        if isinstance(result, list):
            return "\n".join(result)

        return result
    except Exception as e:
        error_msg = f"Error getting model response: {str(e)}"
        write_log(f"ERROR: {error_msg}", level="error")
        raise


def _resolve_langextract_config(
    use_langextract: Optional[bool] = None,
    langextract_config: Optional[dict] = None
) -> dict:
    """Resolve langextract configuration - simplified.
    
    Args:
        use_langextract: Whether to use langextract. Default is False
        langextract_config: Configuration dict with optional settings
    
    Returns:
        dict: Resolved configuration for langextract
    """
    # Simple default configuration
    final_config = {
        'enabled': bool(use_langextract) if use_langextract is not None else False,
        'complexity_threshold': 0.4,  # Default threshold
        'model': 'gemini-2.5-flash',  # Default model
        'timeout': 30
    }
    
    # Override with provided config if any
    if langextract_config:
        final_config.update(langextract_config)
        # Ensure enabled flag is consistent with use_langextract parameter
        if use_langextract is not None:
            final_config['enabled'] = bool(use_langextract)
    
    write_log(f"Langextract config: enabled={final_config['enabled']}, threshold={final_config.get('complexity_threshold', 0.4)}", level="debug")
    return final_config

def _resolve_langextract_config_intelligent(
    model: str,
    provider: str,
    use_langextract: Optional[bool] = None,
    langextract_config: Optional[dict] = None
) -> dict:
    """Intelligently resolve langextract configuration based on model quality.
    
    Args:
        model: Model name being used
        provider: Provider name
        use_langextract: User override for langextract usage
        langextract_config: User-provided configuration
    
    Returns:
        dict: Resolved configuration with intelligent defaults
    """
    try:
        from .model_quality_config import get_recommended_config
        
        # Get intelligent recommendations
        recommended = get_recommended_config(model, provider)
        
        # Start with recommended config
        final_config = {
            'enabled': recommended['use_langextract'],
            'complexity_threshold': recommended['langextract_config']['complexity_threshold'],
            'model': recommended['langextract_config']['model'],
            'timeout': recommended['langextract_config'].get('timeout', 30)
        }
        
        # Override with user settings if provided
        if use_langextract is not None:
            final_config['enabled'] = bool(use_langextract)
            write_log(f"User override: use_langextract={use_langextract}")
        
        if langextract_config:
            final_config.update(langextract_config)
        
        # Log the decision
        write_log(
            f"LangExtract config for {model} ({provider}): "
            f"enabled={final_config['enabled']}, "
            f"threshold={final_config['complexity_threshold']}, "
            f"reason={recommended.get('reason', 'unknown')}"
        )
        
        return final_config
        
    except ImportError:
        # Fallback to simple config if intelligent config not available
        write_log("Intelligent config not available, using simple defaults", level="debug")
        return _resolve_langextract_config(use_langextract, langextract_config)
