"""Utility functions for LLMCellType."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
from typing import Any, Optional, Union

import pandas as pd

from .logger import write_log


def _get_cache_dir(cache_dir: Optional[str] = None) -> str:
    """Get cache directory path with consistent handling.

    Args:
        cache_dir: Custom cache directory or None for default

    Returns:
        str: Cache directory path
    """
    if cache_dir is None:
        cache_dir = os.path.join(os.path.expanduser("~"), ".llmcelltype", "cache")
    return cache_dir


def _handle_cache_error(error: Exception, operation: str, file_path: str = "") -> None:
    """Handle cache operation errors consistently.

    Args:
        error: The exception that occurred
        operation: Description of the operation (e.g., "loading", "saving")
        file_path: Optional file path for context
    """
    context = f" for {file_path}" if file_path else ""
    write_log(
        f"Error {operation} cache{context}: {str(error)}",
        level="error" if "saving" in operation else "warning",
    )


def load_api_key(provider: str) -> str:
    """Load API key for a specific provider from environment variables or .env file.

    Args:
        provider: The provider name (e.g., 'openai', 'anthropic')

    Returns:
        str: The API key

    """
    # Map of provider names to environment variable names
    env_var_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "gemini": "GEMINI_API_KEY",  # Changed from GOOGLE_API_KEY to match .env file
        "qwen": "QWEN_API_KEY",  # Changed from DASHSCOPE_API_KEY to match .env file
        "stepfun": "STEPFUN_API_KEY",
        "zhipu": "ZHIPU_API_KEY",
        "minimax": "MINIMAX_API_KEY",
        "grok": "GROK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }

    # Get environment variable name for provider
    env_var = env_var_map.get(provider.lower())
    if not env_var:
        write_log(f"WARNING: Unknown provider: {provider}", level="warning")
        env_var = f"{provider.upper()}_API_KEY"

    # Get API key from environment variable
    api_key = os.getenv(env_var)

    # If not found in environment, try to load from .env file
    if not api_key:
        try:
            # Try to find .env file in project root (current directory or parent directories)
            env_path = None
            current_dir = os.path.abspath(os.getcwd())

            # Check current directory and up to 3 parent directories
            for _ in range(4):
                potential_path = os.path.join(current_dir, ".env")
                if os.path.isfile(potential_path):
                    env_path = potential_path
                    break
                parent_dir = os.path.dirname(current_dir)
                if parent_dir == current_dir:  # Reached root directory
                    break
                current_dir = parent_dir

            # Also check for a .env file in the package directory
            package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            package_env_path = os.path.join(package_dir, ".env")
            if os.path.isfile(package_env_path):
                env_path = package_env_path

            if env_path:
                write_log(f"Found .env file at {env_path}")
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            if key == env_var:
                                api_key = value
                                write_log(f"Loaded API key for {provider} from .env file")
                                break
        except (OSError, ValueError) as e:
            write_log(f"Error loading .env file: {str(e)}", level="warning")

    if not api_key:
        write_log(f"WARNING: API key not found for provider: {env_var}", level="warning")

    return api_key


def create_cache_key(prompt: str, model: str, provider: str) -> str:
    """Create a cache key for a specific request.

    Args:
        prompt: The prompt text
        model: The model name
        provider: The provider name

    Returns:
        str: The cache key

    """
    # Normalize inputs to ensure consistent keys
    normalized_provider = str(provider).lower().strip()
    normalized_model = str(model).lower().strip()
    normalized_prompt = str(prompt).strip()

    # For OpenRouter models (containing '/'), ensure provider is 'openrouter'
    # This prevents cache key collisions between different providers
    if "/" in normalized_model:
        normalized_provider = "openrouter"

    # Create a string to hash with clear separators to avoid collisions
    hash_string = (
        f"provider:{normalized_provider}||model:{normalized_model}||prompt:{normalized_prompt}"
    )

    # Create hash
    hash_object = hashlib.sha256(hash_string.encode("utf-8"))
    return hash_object.hexdigest()


def save_to_cache(
    cache_key: str,
    results: Union[list[str], dict[str, Any]],
    cache_dir: Optional[str] = None,
) -> None:
    """Save results to cache.

    Args:
        cache_key: The cache key
        results: The results to cache (list of strings or dictionary)
        cache_dir: The cache directory. If None, uses default directory.

    """
    cache_dir = _get_cache_dir(cache_dir)
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    # Ensure results are in a consistent format
    cache_data = {"version": "1.0", "timestamp": time.time(), "data": results}

    # Save results to cache
    try:
        with open(cache_file, "w") as f:
            json.dump(cache_data, f, indent=2)
        write_log(f"Saved results to cache: {cache_file}")
    except (OSError, TypeError, ValueError) as e:
        _handle_cache_error(e, "saving", cache_file)


def load_from_cache(
    cache_key: str, cache_dir: Optional[str] = None
) -> Optional[Union[list[str], dict[str, Any]]]:
    """Load results from cache.

    Args:
        cache_key: The cache key
        cache_dir: The cache directory. If None, uses default directory.

    Returns:
        Optional[Union[list[str], dict[str, Any]]]: The cached results, or None if not found

    """
    cache_dir = _get_cache_dir(cache_dir)
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")

    # Check if cache file exists
    if not os.path.exists(cache_file):
        return None

    # Load results from cache
    try:
        with open(cache_file) as f:
            cache_content = json.load(f)

        # Handle different cache formats
        if isinstance(cache_content, dict) and "data" in cache_content:
            # New format with metadata
            results = cache_content["data"]
            write_log(
                f"Loaded results from cache (version {cache_content.get('version', 'unknown')}): {cache_file}"
            )
        else:
            # Old format (direct data)
            results = cache_content
            write_log(f"Loaded results from cache (legacy format): {cache_file}")

        return results
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        _handle_cache_error(e, "loading", cache_file)
        return None


def parse_marker_genes(marker_genes_df: pd.DataFrame) -> dict[str, list[str]]:
    """Parse marker genes dataframe into a dictionary.

    Args:
        marker_genes_df: DataFrame containing marker genes

    Returns:
        dict[str, list[str]]: Dictionary mapping cluster names to lists of marker genes

    """
    result = {}

    # Check if dataframe is empty
    if marker_genes_df.empty:
        write_log("WARNING: Empty marker genes dataframe", level="warning")
        return result

    # Get column names
    columns = marker_genes_df.columns.tolist()

    # Check if 'cluster' column exists
    if "cluster" not in columns:
        write_log("ERROR: 'cluster' column not found in marker genes dataframe", level="error")
        raise ValueError("'cluster' column not found in marker genes dataframe")

    # Check if 'gene' column exists
    if "gene" not in columns:
        write_log("ERROR: 'gene' column not found in marker genes dataframe", level="error")
        raise ValueError("'gene' column not found in marker genes dataframe")

    # Group by cluster and get list of genes
    for cluster, group in marker_genes_df.groupby("cluster"):
        result[str(cluster)] = group["gene"].tolist()

    return result


def get_annotation_metadata(
    annotation_result: dict[str, str],
) -> dict[str, dict[str, Any]]:
    """Retrieve metadata for a specific annotation result.

    Args:
        annotation_result: Dictionary mapping cluster IDs to cell type annotations

    Returns:
        dict[str, dict[str, Any]]: Dictionary mapping cluster IDs to metadata

    """
    try:
        # Create a unique key for this annotation result
        key = hashlib.sha256(str(annotation_result).encode()).hexdigest()

        # Check if metadata exists in cache
        cache_dir = os.path.expanduser("~/.mllmcelltype/metadata")
        cache_file = os.path.join(cache_dir, f"{key}.json")

        if os.path.exists(cache_file):
            with open(cache_file) as f:
                return json.load(f)
        write_log("No metadata found for the given annotation result", level="debug")
        return {}
    except (KeyError, TypeError, AttributeError, ValueError) as e:
        write_log(f"Failed to retrieve metadata: {str(e)}", level="debug")
        return {}


def format_results(
    results: list[str], 
    clusters: list[str],
    langextract_config: dict = None,
    use_langextract: bool = None
) -> dict[str, str]:
    """Format results into a dictionary mapping cluster names to annotations.

    This function now supports both traditional parsing and langextract-powered parsing.
    It intelligently selects the best parsing strategy based on complexity assessment.

    Args:
        results: List of annotation results (one line per cluster)
        clusters: List of cluster names
        langextract_config: Configuration for langextract parsing (optional)
        use_langextract: Force enable/disable langextract. If None, use auto-detection

    Returns:
        dict[str, str]: Dictionary mapping cluster names to annotations

    """
    start_time = time.time()
    
    write_log(
        f"Starting result formatting for {len(clusters)} clusters with {len(results)} result lines",
        level="info"
    )
    
    # Skip langextract initialization if explicitly disabled for performance
    if use_langextract is False:
        write_log("LangExtract explicitly disabled, using traditional parsing", level="debug")
        return _format_results_traditional(results, clusters)
    
    # Initialize langextract components with error handling
    try:
        from .langextract_controller import LangextractController
        from .langextract_parser import LangextractParser
        
        controller = LangextractController(
            use_langextract=use_langextract,
            langextract_config=langextract_config or {}
        )
        
        # Make intelligent decision about parsing strategy
        decision = controller.should_use_langextract(results, clusters)
        
        write_log(
            f"Parsing strategy decision: {'LangExtract' if decision['use_langextract'] else 'Traditional'} "
            f"(reason: {decision['reason']}, complexity: {decision['complexity_score']:.3f})"
        )
        
        # Try langextract if decided
        if decision['use_langextract']:
            try:
                # Get the model and load appropriate API key
                model = langextract_config.get('model', 'gemini-2.5-flash') if langextract_config else 'gemini-2.5-flash'
                
                # Get API key for the model's provider
                from .functions import get_provider
                provider = get_provider(model)
                api_key = load_api_key(provider) if provider else None
                
                parser = LangextractParser(
                    model=model,
                    timeout=langextract_config.get('timeout', 30) if langextract_config else 30,
                    api_key=api_key  # Explicitly pass the API key
                )
                
                langextract_result = parser.parse_cell_type_annotations_original(
                    results=results,
                    clusters=clusters,
                    additional_context=langextract_config.get('context') if langextract_config else None
                )
                
                if langextract_result['success']:
                    execution_time = time.time() - start_time
                    annotations = langextract_result['annotations']
                    
                    write_log(
                        f"LangExtract successfully parsed {len(annotations)}/{len(clusters)} annotations "
                        f"in {execution_time:.3f}s (langextract: {langextract_result['metadata']['execution_time']:.3f}s)"
                    )
                    
                    # Ensure all clusters have annotations, fill missing with fallback
                    for cluster in clusters:
                        cluster_str = str(cluster)
                        if cluster_str not in annotations:
                            write_log(f"Missing annotation for cluster {cluster_str}, will use fallback", level="warning")
                    
                    # If we have good coverage, return langextract result
                    coverage = len(annotations) / len(clusters) if clusters else 0
                    if coverage >= 0.5:  # At least 50% coverage
                        # Fill missing clusters with traditional parsing
                        if coverage < 1.0:
                            write_log("Filling missing clusters with traditional parsing", level="info")
                            traditional_result = _format_results_traditional(results, clusters)
                            for cluster in clusters:
                                cluster_str = str(cluster)
                                if cluster_str not in annotations and cluster_str in traditional_result:
                                    annotations[cluster_str] = traditional_result[cluster_str]
                        
                        return annotations
                    else:
                        write_log(
                            f"LangExtract coverage too low ({coverage:.1%}), falling back to traditional parsing",
                            level="warning"
                        )
                        
                else:
                    write_log(
                        f"LangExtract parsing failed: {langextract_result.get('error', 'Unknown error')}, "
                        "falling back to traditional parsing",
                        level="warning"
                    )
                    
            except Exception as e:
                write_log(f"LangExtract processing error: {str(e)}, falling back to traditional parsing", level="warning")
    
    except ImportError as e:
        write_log(f"LangExtract modules not available: {str(e)}, using traditional parsing", level="debug")
    except Exception as e:
        write_log(f"Error initializing langextract components: {str(e)}, using traditional parsing", level="warning")
    
    # Fall back to traditional parsing
    write_log("Using traditional parsing method", level="info")
    traditional_result = _format_results_traditional(results, clusters)
    
    execution_time = time.time() - start_time
    write_log(
        f"Traditional parsing completed in {execution_time:.3f}s, "
        f"found {len(traditional_result)}/{len(clusters)} annotations"
    )
    
    return traditional_result


def _format_results_traditional(results: list[str], clusters: list[str]) -> dict[str, str]:
    """Traditional format_results implementation with 4-layer fallback logic.
    
    This function contains the original parsing logic that was in format_results(),
    preserved exactly to maintain backward compatibility.
    
    Args:
        results: List of annotation results (one line per cluster)
        clusters: List of cluster names
        
    Returns:
        dict[str, str]: Dictionary mapping cluster names to annotations
    """
    import json

    # Clean up results (remove empty lines and whitespace)
    clean_results = [line.strip() for line in results if line.strip()]

    # Case 1: Try to parse the format "Cluster X: Annotation" (most common format from our prompts)
    result = {}
    cluster_pattern = r"Cluster\s+(\d+):\s*(.*)"

    # First pass: try to find annotations for each cluster by ID
    for cluster in clusters:
        cluster_str = str(cluster)

        # Look for exact matches (e.g., "Cluster 0: T cells")
        for line in clean_results:
            match = re.match(cluster_pattern, line)
            if match and match.group(1) == cluster_str:
                result[cluster_str] = match.group(2).strip()
                break

    # If we found annotations for all clusters, return the result
    if len(result) == len(clusters):
        write_log(
            "Successfully parsed response in 'Cluster X: Annotation' format (traditional)",
            level="info",
        )
        return result

    # Case 2: Try to parse JSON response
    try:
        # Join all lines and try to find JSON content
        full_text = "\n".join(clean_results)

        # Extract JSON content if it's wrapped in ```json and ``` markers
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", full_text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no code blocks, try to find JSON object directly
            json_match = re.search(r"(\{[\s\S]*\})", full_text)
            # Extract JSON content or use full text
            json_str = json_match.group(1) if json_match else full_text

        # Fix common JSON formatting issues
        # Add missing commas between JSON objects
        json_str = re.sub(r'("[^"]+")\s*\n\s*("[^"]+")', r"\1,\n\2", json_str)
        # Add missing commas after closing brackets
        json_str = re.sub(r'(\])\s*\n\s*("[^"]+")', r"\1,\n\2", json_str)
        # Add missing commas after closing braces
        json_str = re.sub(r'(\})\s*\n\s*("[^"]+")', r"\1,\n\2", json_str)
        # Add missing commas after closing braces before opening braces
        json_str = re.sub(r"(\})\s*\n\s*(\{)", r"\1,\n\2", json_str)

        # Parse JSON
        data = json.loads(json_str)

        # Extract annotations from JSON structure
        if "annotations" in data and isinstance(data["annotations"], list):
            json_result = {}
            metadata = {}

            for annotation in data["annotations"]:
                if "cluster" in annotation and "cell_type" in annotation:
                    cluster_id = annotation["cluster"]
                    json_result[cluster_id] = annotation["cell_type"]

                    # Store additional metadata if available
                    cluster_metadata = {}
                    if "confidence" in annotation:
                        cluster_metadata["confidence"] = annotation["confidence"]
                    if "key_markers" in annotation:
                        cluster_metadata["key_markers"] = annotation["key_markers"]

                    if cluster_metadata:
                        metadata[cluster_id] = cluster_metadata

            # If we found annotations for all clusters, return the result
            if len(json_result) == len(clusters):
                write_log("Successfully parsed JSON response (traditional)", level="info")

                # Store metadata in cache for later retrieval if needed
                if metadata:
                    try:
                        cache_dir = os.path.expanduser("~/.mllmcelltype/metadata")
                        os.makedirs(cache_dir, exist_ok=True)

                        # Create a unique key for this annotation result
                        key = hashlib.sha256(str(json_result).encode()).hexdigest()
                        cache_file = os.path.join(cache_dir, f"{key}.json")

                        with open(cache_file, "w") as f:
                            json.dump(metadata, f, indent=2)

                        write_log(f"Stored annotation metadata to {cache_file}", level="debug")
                    except (OSError, TypeError, ValueError) as e:
                        write_log(f"Failed to store metadata: {str(e)}", level="debug")

                return json_result
    except (json.JSONDecodeError, ValueError, KeyError, TypeError, AttributeError) as e:
        write_log(f"Failed to parse JSON response (traditional): {str(e)}", level="debug")

    # Case 3: Check if this is a simple response where each line corresponds to a cluster
    # This is the expected format from the R version
    if len(clean_results) >= len(clusters):
        # Simple case: one result per cluster
        simple_result = {}
        for i, cluster in enumerate(clusters):
            if i < len(clean_results):
                # Check if this line contains a cluster prefix and remove it
                line = clean_results[i]
                match = re.match(cluster_pattern, line)
                if match:
                    simple_result[str(cluster)] = match.group(2).strip()
                else:
                    simple_result[str(cluster)] = line.strip()
            else:
                simple_result[str(cluster)] = "Unknown"

        write_log("Successfully parsed response as simple line-by-line format (traditional)", level="info")
        return simple_result

    # Case 4: Fall back to the original method
    write_log(
        "WARNING: Could not parse complex LLM response, falling back to simple mapping (traditional)",
        level="warning",
    )
    result = {}
    for i, cluster in enumerate(clusters):
        if i < len(clean_results):
            result[str(cluster)] = clean_results[i]
        else:
            result[str(cluster)] = "Unknown"

    # Check if number of results matches number of clusters
    if len(result) != len(clusters):
        write_log(
            f"WARNING: Number of results ({len(result)}) does not match number of clusters ({len(clusters)}) (traditional)",
            level="warning",
        )

    return result


def _remove_common_prefixes(annotation: str) -> str:
    """Remove common prefixes from annotations."""
    # Remove "Cluster X:" prefix if present
    if annotation.lower().startswith("cluster ") and ":" in annotation:
        annotation = annotation.split(":", 1)[1].strip()

    # Remove number prefix if present (e.g. "1. T cells" -> "T cells")
    if ". " in annotation and annotation[0].isdigit():
        parts = annotation.split(". ", 1)
        if parts[0].isdigit():
            annotation = parts[1]

    # Remove common prefixes
    prefixes = ["cell type:", "cell type", "annotation:", "annotation"]
    for prefix in prefixes:
        if annotation.lower().startswith(prefix):
            annotation = annotation[len(prefix) :].strip()

    return annotation


def _extract_cell_type_from_description(annotation: str) -> str:
    """Extract cell type from descriptive text."""
    patterns = [
        r"([\w\s-]+)\s+(?:is|are)\s+the\s+most\s+accurate\s+cell\s+type",
        r"([\w\s-]+)\s+(?:is|are)\s+the\s+best\s+annotation",
        r"final\s+cell\s+type\s*:?\s*([\w\s-]+)",
        r"final\s+decision\s*:?\s*([\w\s-]+)",
        r"majority\s+prediction\s*:?\s*([\w\s-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, annotation.lower())
        if match:
            return match.group(1).strip()

    return annotation


def _clean_formatting(annotation: str) -> str:
    """Clean formatting marks and symbols."""
    # Remove quotes
    if annotation.startswith('"') and annotation.endswith('"'):
        annotation = annotation[1:-1]

    # Remove markdown emphasis marks
    annotation = annotation.replace("**:", "").replace("**", "").replace("*", "")

    # Remove common prefix markers
    if annotation.startswith("-"):
        annotation = annotation[1:].strip()

    # Remove prefixes like "Final Cell Type:"
    if ":" in annotation and any(
        x in annotation.lower() for x in ["final", "type", "determination", "conclusion"]
    ):
        parts = annotation.split(":", 1)
        annotation = parts[1].strip()

    # Remove trailing punctuation
    if annotation and annotation[-1] in [".", ",", ";"]:
        annotation = annotation[:-1]

    # Remove LaTeX formatting
    annotation = re.sub(r"\$\\boxed\{(.+?)\}\$", r"\1", annotation)
    annotation = re.sub(r"\$.+?\$", "", annotation)

    return annotation


def clean_annotation(annotation: str) -> str:
    """Clean up cell type annotation from LLM response.

    Args:
        annotation: Raw annotation string

    Returns:
        str: Cleaned annotation

    """
    # If input is empty or None, return an empty string
    if not annotation:
        return ""

    # Basic cleanup
    annotation = annotation.strip()

    # Apply cleaning steps
    annotation = _remove_common_prefixes(annotation)
    annotation = _extract_cell_type_from_description(annotation)
    annotation = _clean_formatting(annotation)

    # Truncate long descriptions
    if len(annotation) > 50:
        short_version = annotation.split(",")[0].split("(")[0].strip()
        if len(short_version) >= 10:
            annotation = short_version

    return annotation


def normalize_annotation_for_comparison(annotation: str) -> str:
    """Normalize cell type annotation for comparison purposes.

    This function performs more aggressive normalization than clean_annotation
    to help identify semantically similar annotations in the fallback consensus calculation.

    Args:
        annotation: Cell type annotation string

    Returns:
        str: Normalized annotation for comparison
    """
    if not annotation:
        return ""

    # Start with basic cleaning
    normalized = clean_annotation(annotation)

    # Convert to lowercase for comparison
    normalized = normalized.lower()

    # Remove common punctuation and symbols
    normalized = normalized.replace("-", " ")
    normalized = normalized.replace("+", " positive ")
    normalized = normalized.replace("/", " ")
    normalized = normalized.replace("_", " ")

    # Normalize common variations
    replacements = {
        "t cell": "t cells",
        "b cell": "b cells",
        "nk cell": "nk cells",
        "cd4 ": "cd4+ ",
        "cd8 ": "cd8+ ",
        "naive": "naive",
        "naïve": "naive",
        "tumour": "tumor",
        " cell$": " cells",  # Ensure plural at end
    }

    for old, new in replacements.items():
        if "$" in old:
            # Handle regex patterns
            import re

            normalized = re.sub(old, new, normalized)
        else:
            normalized = normalized.replace(old, new)

    # Remove extra whitespace
    normalized = " ".join(normalized.split())

    return normalized


def find_agreement(
    annotations: dict[str, dict[str, str]],
) -> tuple[dict[str, str], dict[str, float], dict[str, float]]:
    """Find the level of agreement between different model annotations.

    Args:
        annotations: Dictionary mapping model names to dictionaries of cluster annotations

    Returns:
        tuple[dict[str, str], dict[str, float], dict[str, float]]:
            - Consensus annotations
            - Consensus proportion (confidence scores)
            - Entropy scores (measure of uncertainty)

    """
    consensus = {}
    confidence = {}
    entropy_scores = {}

    # Ensure we have annotations
    if not annotations or not all(annotations.values()):
        return {}, {}, {}

    # Get all clusters
    all_clusters = set()
    for model_results in annotations.values():
        all_clusters.update(model_results.keys())

    # Process each cluster
    for cluster in all_clusters:
        # Collect all annotations for this cluster
        cluster_annotations = []

        for _model, results in annotations.items():
            if cluster in results:
                annotation = clean_annotation(results[cluster])
                if annotation:
                    cluster_annotations.append(
                        annotation.lower()
                    )  # Convert to lowercase for case-insensitive comparison

        # Count occurrences of each annotation
        annotation_counts = {}
        for annotation in cluster_annotations:
            annotation_counts[annotation] = annotation_counts.get(annotation, 0) + 1

        # Find most common annotation
        if annotation_counts:
            most_common = max(annotation_counts.items(), key=lambda x: x[1])
            most_common_annotation = most_common[0]
            most_common_count = most_common[1]

            # Calculate consensus proportion (confidence)
            consensus_proportion = (
                most_common_count / len(cluster_annotations) if cluster_annotations else 0
            )

            # Calculate entropy (measure of uncertainty)
            entropy = 0.0
            if len(cluster_annotations) > 1:
                # Calculate entropy based on distribution of annotations
                total = len(cluster_annotations)
                entropy = 0.0
                for count in annotation_counts.values():
                    p = count / total
                    entropy -= p * (math.log2(p) if p > 0 else 0)

            consensus[cluster] = most_common_annotation
            confidence[cluster] = consensus_proportion
            entropy_scores[cluster] = entropy
        else:
            consensus[cluster] = "Unknown"
            confidence[cluster] = 0.0
            entropy_scores[cluster] = 0.0

    return consensus, confidence, entropy_scores


def validate_cache(cache_key: str, cache_dir: Optional[str] = None) -> bool:
    """Validate cache content for a specific key.

    Args:
        cache_key: The cache key to validate
        cache_dir: The cache directory. If None, uses default directory.

    Returns:
        bool: True if cache is valid, False otherwise

    """
    cache_dir = _get_cache_dir(cache_dir)
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")

    # Check if cache file exists
    if not os.path.exists(cache_file):
        return False

    # Validate cache content
    try:
        with open(cache_file) as f:
            cache_content = json.load(f)

        # Check if cache content is in the new format
        if (
            isinstance(cache_content, dict)
            and "version" in cache_content
            and "data" in cache_content
        ):
            # New format with metadata
            return True
        if isinstance(cache_content, (list, dict)):
            # Legacy format - still valid but will be converted on next save
            return True
        # Invalid format
        write_log(f"Invalid cache format for key {cache_key}", level="warning")
        return False
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as e:
        _handle_cache_error(e, "validating", cache_file)
        return False


def clear_cache(cache_dir: Optional[str] = None, older_than: Optional[int] = None) -> int:
    """Clear cache.

    Args:
        cache_dir: Cache directory
        older_than: Only clear items older than this many seconds.
                   If None, clear all cache.

    Returns:
        int: Number of cache files removed

    """
    cache_dir = _get_cache_dir(cache_dir)

    if not os.path.exists(cache_dir):
        return 0

    # Get all cache files
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith(".json")]

    if not older_than:
        # Remove all cache files
        count = 0
        for f in cache_files:
            try:
                os.remove(os.path.join(cache_dir, f))
                count += 1
            except OSError as e:
                write_log(f"Error removing cache file {f}: {e}", level="warning")
        return count
    # Remove only older files
    now = time.time()
    count = 0
    for f in cache_files:
        file_path = os.path.join(cache_dir, f)
        try:
            # Check file age using metadata
            with open(file_path) as file:
                cache_data = json.load(file)

            # Handle different cache formats
            if isinstance(cache_data, dict) and "timestamp" in cache_data:
                # New format with metadata
                file_age = now - cache_data.get("timestamp", 0)
            else:
                # Legacy format - use file modification time
                file_age = now - os.path.getmtime(file_path)

            if file_age > older_than:
                os.remove(file_path)
                count += 1
        except OSError as e:
            write_log(f"Error processing cache file {f}: {e}", level="warning")

    return count


def get_cache_stats(cache_dir: Optional[str] = None) -> dict[str, Any]:
    """Get cache statistics.

    Args:
        cache_dir: The cache directory

    Returns:
        dict[str, Any]: Cache statistics

    """
    cache_dir = _get_cache_dir(cache_dir)

    if not os.path.exists(cache_dir):
        return {
            "status": "No cache directory",
            "count": 0,
            "size": 0,
            "oldest": None,
            "newest": None,
            "provider_counts": {},
        }

    # Get all cache files
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith(".json")]

    if not cache_files:
        return {
            "status": "Empty cache",
            "count": 0,
            "size": 0,
            "oldest": None,
            "newest": None,
            "provider_counts": {},
        }

    # Calculate statistics
    total_size = 0
    oldest = float("inf")
    newest = 0
    provider_counts = {}
    format_counts = {"legacy": 0, "v1.0": 0, "unknown": 0}
    valid_files = 0
    invalid_files = 0

    for f in cache_files:
        file_path = os.path.join(cache_dir, f)
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            total_size += file_size

            # Load cache data
            with open(file_path) as file:
                cache_data = json.load(file)

            valid_files += 1

            # Check cache format
            if isinstance(cache_data, dict):
                if "version" in cache_data and "data" in cache_data:
                    # New format with metadata
                    version = cache_data.get("version", "unknown")
                    format_counts[version if version in format_counts else "unknown"] += 1

                    # Get timestamp
                    timestamp = cache_data.get("timestamp", 0)
                    oldest = min(oldest, timestamp)
                    newest = max(newest, timestamp)

                    # Try to extract provider from metadata
                    if "provider" in cache_data:
                        provider = cache_data["provider"]
                        provider_counts[provider] = provider_counts.get(provider, 0) + 1
                else:
                    # Legacy format or other dict format
                    format_counts["legacy"] += 1

                    # Try to extract provider if available
                    if "provider" in cache_data:
                        provider = cache_data["provider"]
                        provider_counts[provider] = provider_counts.get(provider, 0) + 1
            else:
                # Unknown format
                format_counts["unknown"] += 1

        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            ValueError,
            TypeError,
            AttributeError,
        ) as e:
            invalid_files += 1
            write_log(f"Error processing cache file {f}: {e}", level="warning")

    # Convert timestamps to readable format
    if oldest != float("inf"):
        oldest_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(oldest))
    else:
        oldest_str = None

    if newest != 0:
        newest_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(newest))
    else:
        newest_str = None

    return {
        "status": "Cache available",
        "count": len(cache_files),
        "valid_files": valid_files,
        "invalid_files": invalid_files,
        "size": total_size,
        "size_readable": f"{total_size / (1024 * 1024):.2f} MB",
        "oldest": oldest_str,
        "newest": newest_str,
        "format_counts": format_counts,
        "provider_counts": provider_counts,
    }
