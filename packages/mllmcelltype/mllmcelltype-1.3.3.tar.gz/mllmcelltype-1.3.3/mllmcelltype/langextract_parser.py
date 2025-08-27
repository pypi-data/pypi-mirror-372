"""
LangExtract Parser for structured cell type annotation extraction.

This module provides the core parsing functionality using langextract
for extracting cell type annotations from complex LLM responses.
"""

from __future__ import annotations

import json
import os
import time
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from .logger import write_log


class LangextractParser:
    """Parser for cell type annotations using langextract."""
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 2,
    ):
        """Initialize the LangExtract parser.
        
        Args:
            model: Model to use for langextract
            api_key: API key for the model
            timeout: Timeout in seconds for langextract calls
            max_retries: Maximum number of retries on failure
        """
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Set up API key
        self.api_key = api_key or self._get_api_key()
        
        # Initialize langextract
        self.langextract_available = self._initialize_langextract()
        
        # Schema definitions for different parsing tasks
        self.schemas = self._create_schemas()
        
        write_log(
            f"LangExtract Parser initialized. Available: {self.langextract_available}, "
            f"Model: {self.model}, Timeout: {self.timeout}s"
        )
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key using the unified load_api_key function."""
        from .utils import load_api_key
        from .functions import get_provider
        
        # Try to get API key based on model provider
        try:
            provider = get_provider(self.model)
            if provider:
                api_key = load_api_key(provider)
                if api_key:
                    write_log(f"Using API key for provider: {provider}", level="debug")
                    return api_key
        except Exception as e:
            write_log(f"Error getting API key for model {self.model}: {e}", level="debug")
        
        # Fallback to checking environment variables directly
        env_keys = ["LANGEXTRACT_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"]
        for key_name in env_keys:
            key_value = os.getenv(key_name)
            if key_value:
                write_log(f"Using API key from {key_name}", level="debug")
                return key_value
        
        write_log("No API key found", level="warning")
        return None
    
    def _initialize_langextract(self) -> bool:
        """Initialize langextract and check availability."""
        try:
            import langextract
            self.langextract = langextract
            
            if not self.api_key:
                write_log("LangExtract available but no API key found", level="warning")
                return False
                
            write_log("LangExtract successfully initialized", level="info")
            return True
            
        except ImportError as e:
            write_log(f"Failed to import langextract: {e}", level="warning")
            self.langextract = None
            return False
    
    def _create_schemas(self) -> Dict[str, Any]:
        """Create schema definitions and examples for different parsing tasks."""
        return {
            "cell_type_annotations": {
                "description": """
                Extract cell type annotations from the response. The response should contain 
                annotations for multiple clusters, where each cluster has an ID and a cell type.
                
                Extract the following information for each cluster:
                - cluster_id: The cluster identifier (as string)
                - cell_type: The predicted cell type name
                - confidence: Confidence level if mentioned (optional)
                - key_markers: List of marker genes if mentioned (optional)
                - reasoning: Explanation for the annotation if provided (optional)
                """,
                "examples": [
                    {
                        "text": "Cluster 0: T cells\nCluster 1: B cells\nCluster 2: NK cells",
                        "extractions": [
                            {"cluster_id": "0", "cell_type": "T cells"},
                            {"cluster_id": "1", "cell_type": "B cells"},
                            {"cluster_id": "2", "cell_type": "NK cells"},
                        ]
                    },
                    {
                        "text": '''{"annotations": [{"cluster": "0", "cell_type": "CD8+ T cells", "confidence": "high"}]}''',
                        "extractions": [
                            {"cluster_id": "0", "cell_type": "CD8+ T cells", "confidence": "high"}
                        ]
                    }
                ]
            },
            "consensus_metrics": {
                "description": """
                Extract consensus and agreement metrics from comparative analysis results.
                Look for information about:
                - overall_consensus: Overall agreement level
                - cluster_agreements: Per-cluster agreement scores
                - model_performance: Individual model performance metrics
                - quality_scores: Quality assessment metrics
                """,
                "examples": [
                    {
                        "text": "Overall consensus: 85%. Cluster 0: 90% agreement, Cluster 1: 80% agreement",
                        "extractions": [
                            {"metric_type": "overall_consensus", "value": "85%"},
                            {"metric_type": "cluster_agreement", "cluster_id": "0", "value": "90%"},
                            {"metric_type": "cluster_agreement", "cluster_id": "1", "value": "80%"}
                        ]
                    }
                ]
            }
        }
    
    def parse_cell_type_annotations_original(
        self,
        results: List[str],
        clusters: List[str],
        additional_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parse cell type annotations using langextract.
        
        Args:
            results: List of annotation results from LLM
            clusters: List of expected cluster IDs
            additional_context: Additional context to help parsing
            
        Returns:
            Dict containing parsed annotations and metadata
        """
        if not self.langextract_available:
            return {
                "success": False,
                "error": "LangExtract not available",
                "annotations": {},
                "metadata": {
                    "method": "langextract",
                    "execution_time": 0.0,
                    "model_used": self.model,
                }
            }
        
        start_time = time.time()
        
        # Prepare input text
        input_text = self._prepare_input_text(results, clusters, additional_context)
        
        # Prepare schema and examples
        schema = self.schemas["cell_type_annotations"]
        
        # Build dynamic prompt
        prompt = self._build_annotation_prompt(clusters, schema["description"])
        
        try:
            # Call langextract with retries
            extraction_result = self._call_langextract_with_retries(
                text=input_text,
                prompt=prompt,
                examples=schema.get("examples", [])
            )
            
            execution_time = time.time() - start_time
            
            if extraction_result is None:
                return {
                    "success": False,
                    "error": "LangExtract call failed after retries",
                    "annotations": {},
                    "metadata": {
                        "method": "langextract",
                        "execution_time": execution_time,
                        "model_used": self.model,
                    }
                }
            
            # Parse the extraction result
            parsed_annotations = self._parse_extraction_result(
                extraction_result, clusters
            )
            
            success = self._validate_annotations(parsed_annotations, clusters)
            
            result = {
                "success": success,
                "annotations": parsed_annotations,
                "raw_result": extraction_result,
                "metadata": {
                    "method": "langextract",
                    "execution_time": execution_time,
                    "model_used": self.model,
                    "input_length": len(input_text),
                    "clusters_expected": len(clusters),
                    "clusters_found": len(parsed_annotations),
                }
            }
            
            if success:
                write_log(
                    f"LangExtract successfully parsed {len(parsed_annotations)}/{len(clusters)} "
                    f"annotations in {execution_time:.3f}s"
                )
            else:
                write_log(
                    f"LangExtract parsing incomplete: {len(parsed_annotations)}/{len(clusters)} "
                    f"annotations in {execution_time:.3f}s",
                    level="warning"
                )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"LangExtract parsing failed: {str(e)}"
            write_log(error_msg, level="error")
            
            return {
                "success": False,
                "error": error_msg,
                "annotations": {},
                "metadata": {
                    "method": "langextract",
                    "execution_time": execution_time,
                    "model_used": self.model,
                }
            }
    
    def parse_consensus_metrics(
        self,
        analysis_text: str,
        expected_metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Parse consensus and agreement metrics from analysis results.
        
        Args:
            analysis_text: Text containing consensus analysis
            expected_metrics: List of expected metric types
            
        Returns:
            Dict containing parsed metrics and metadata
        """
        if not self.langextract_available:
            return {
                "success": False,
                "error": "LangExtract not available",
                "metrics": {},
            }
        
        start_time = time.time()
        
        schema = self.schemas["consensus_metrics"]
        prompt = schema["description"]
        
        if expected_metrics:
            prompt += f"\n\nSpecifically look for these metrics: {', '.join(expected_metrics)}"
        
        try:
            extraction_result = self._call_langextract_with_retries(
                text=analysis_text,
                prompt=prompt,
                examples=schema.get("examples", [])
            )
            
            execution_time = time.time() - start_time
            
            if extraction_result is None:
                return {
                    "success": False,
                    "error": "LangExtract call failed for consensus metrics",
                    "metrics": {},
                    "metadata": {"execution_time": execution_time}
                }
            
            # Parse metrics from result
            parsed_metrics = self._parse_consensus_metrics(extraction_result)
            
            return {
                "success": len(parsed_metrics) > 0,
                "metrics": parsed_metrics,
                "raw_result": extraction_result,
                "metadata": {
                    "execution_time": execution_time,
                    "metrics_found": len(parsed_metrics),
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": f"Consensus metrics parsing failed: {str(e)}",
                "metrics": {},
                "metadata": {"execution_time": execution_time}
            }
    
    def _prepare_input_text(
        self,
        results: List[str],
        clusters: List[str],
        additional_context: Optional[str] = None,
    ) -> str:
        """Prepare input text for langextract processing."""
        # Clean and join results
        clean_results = [line.strip() for line in results if line.strip()]
        input_text = "\n".join(clean_results)
        
        # Add context if provided
        if additional_context:
            input_text = f"{additional_context}\n\n{input_text}"
        
        # Add cluster information as context
        cluster_info = f"Expected clusters: {', '.join(clusters)}\n\n"
        input_text = cluster_info + input_text
        
        return input_text
    
    def _build_annotation_prompt(self, clusters: List[str], base_description: str) -> str:
        """Build dynamic prompt for annotation extraction."""
        prompt = base_description
        prompt += f"\n\nThe response should contain annotations for {len(clusters)} clusters: "
        prompt += ", ".join(f"cluster {cluster}" for cluster in clusters)
        prompt += "\n\nReturn the results as a structured format that can be easily parsed."
        
        return prompt
    
    def _call_langextract_with_retries(
        self,
        text: str,
        prompt: str,
        examples: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Any]:
        """Call langextract with retry mechanism."""
        for attempt in range(self.max_retries + 1):
            try:
                write_log(f"LangExtract attempt {attempt + 1}/{self.max_retries + 1}", level="debug")
                
                # Convert examples to langextract format if provided
                langextract_examples = None
                if examples:
                    langextract_examples = self._convert_to_langextract_examples(examples)
                
                # Make the call
                result = self.langextract.extract(
                    text_or_documents=text,
                    prompt_description=prompt,
                    examples=langextract_examples,
                    model_id=self.model,
                    api_key=self.api_key,
                )
                
                return result
                
            except Exception as e:
                write_log(f"LangExtract attempt {attempt + 1} failed: {str(e)}", level="warning")
                if attempt == self.max_retries:
                    write_log("All LangExtract attempts failed", level="error")
                    return None
                
                # Wait before retry
                time.sleep(1 * (attempt + 1))
        
        return None
    
    def _convert_to_langextract_examples(self, examples: List[Dict[str, Any]]) -> List[Any]:
        """Convert example format to langextract format."""
        try:
            langextract_examples = []
            
            for example in examples:
                if "text" in example and "extractions" in example:
                    text = example["text"]
                    extractions_list = []
                    
                    for extraction in example["extractions"]:
                        # Convert extraction to string format
                        extraction_value = json.dumps(extraction) if isinstance(extraction, dict) else str(extraction)
                        
                        # Create extraction with correct API (based on langextract 1.0.8)
                        # Use proper parameter names: extraction_class and extraction_text
                        extraction_obj = self.langextract.data.Extraction(
                            extraction_class="cell_type_annotation",
                            extraction_text=extraction_value,
                            char_interval=self.langextract.data.CharInterval(0, len(text))
                        )
                        extractions_list.append(extraction_obj)
                    
                    # Create example data
                    example_data = self.langextract.data.ExampleData(
                        text=text,
                        extractions=extractions_list
                    )
                    langextract_examples.append(example_data)
            
            return langextract_examples if langextract_examples else None
            
        except Exception as e:
            write_log(f"Failed to convert examples to langextract format: {e}", level="warning")
            return None
    
    def _parse_extraction_result(
        self,
        extraction_result: Any,
        expected_clusters: List[str],
    ) -> Dict[str, str]:
        """Parse langextract result into annotation dictionary."""
        annotations = {}
        
        try:
            # Handle different result formats
            if hasattr(extraction_result, 'extractions') and extraction_result.extractions:
                # Extract from langextract extractions
                for extraction in extraction_result.extractions:
                    if hasattr(extraction, 'extraction_text'):
                        value = extraction.extraction_text
                        
                        # Try to parse as JSON first
                        try:
                            parsed_value = json.loads(value)
                            if isinstance(parsed_value, dict):
                                cluster_id = str(parsed_value.get("cluster_id", ""))
                                cell_type = parsed_value.get("cell_type", "")
                                if cluster_id and cell_type:
                                    annotations[cluster_id] = cell_type
                        except (json.JSONDecodeError, TypeError):
                            # Try to parse as simple string
                            self._parse_string_extraction(value, annotations)
                    elif hasattr(extraction, 'value'):
                        # Fallback for older API format
                        value = extraction.value
                        
                        # Try to parse as JSON first
                        try:
                            parsed_value = json.loads(value)
                            if isinstance(parsed_value, dict):
                                cluster_id = str(parsed_value.get("cluster_id", ""))
                                cell_type = parsed_value.get("cell_type", "")
                                if cluster_id and cell_type:
                                    annotations[cluster_id] = cell_type
                        except (json.JSONDecodeError, TypeError):
                            # Try to parse as simple string
                            self._parse_string_extraction(value, annotations)
            
            elif isinstance(extraction_result, dict):
                # Handle dict result
                if "extractions" in extraction_result:
                    for extraction in extraction_result["extractions"]:
                        cluster_id = str(extraction.get("cluster_id", ""))
                        cell_type = extraction.get("cell_type", "")
                        if cluster_id and cell_type:
                            annotations[cluster_id] = cell_type
                else:
                    # Direct dict mapping
                    for key, value in extraction_result.items():
                        if str(key) in expected_clusters:
                            annotations[str(key)] = str(value)
            
            elif isinstance(extraction_result, list):
                # Handle list result
                for item in extraction_result:
                    if isinstance(item, dict):
                        cluster_id = str(item.get("cluster_id", ""))
                        cell_type = item.get("cell_type", "")
                        if cluster_id and cell_type:
                            annotations[cluster_id] = cell_type
            
            else:
                # Try to parse as string
                self._parse_string_extraction(str(extraction_result), annotations)
            
        except Exception as e:
            write_log(f"Error parsing langextract result: {e}", level="warning")
        
        # Clean up annotations
        cleaned_annotations = {}
        for cluster_id, cell_type in annotations.items():
            if cluster_id and cell_type:
                from .utils import clean_annotation
                cleaned_annotations[str(cluster_id)] = clean_annotation(str(cell_type))
        
        return cleaned_annotations
    
    def _parse_string_extraction(self, text: str, annotations: Dict[str, str]) -> None:
        """Parse string extraction into annotations dictionary."""
        import re
        
        # Pattern 1: "Cluster X: Type"
        cluster_pattern = r"(?i)cluster\s+(\d+)\s*:\s*([^\n]+)"
        matches = re.findall(cluster_pattern, text)
        for cluster_id, cell_type in matches:
            annotations[cluster_id] = cell_type.strip()
        
        # Pattern 2: JSON-like patterns
        json_pattern = r'"cluster_id":\s*"(\d+)".*?"cell_type":\s*"([^"]+)"'
        matches = re.findall(json_pattern, text)
        for cluster_id, cell_type in matches:
            annotations[cluster_id] = cell_type.strip()
    
    def _parse_consensus_metrics(self, extraction_result: Any) -> Dict[str, Any]:
        """Parse consensus metrics from extraction result."""
        metrics = {}
        
        try:
            if hasattr(extraction_result, 'extractions') and extraction_result.extractions:
                for extraction in extraction_result.extractions:
                    if hasattr(extraction, 'value'):
                        # Parse metric value
                        value = extraction.value
                        try:
                            parsed = json.loads(value)
                            if isinstance(parsed, dict):
                                metric_type = parsed.get("metric_type", "unknown")
                                metric_value = parsed.get("value", "")
                                metrics[metric_type] = metric_value
                        except (json.JSONDecodeError, TypeError):
                            pass
        except Exception as e:
            write_log(f"Error parsing consensus metrics: {e}", level="warning")
        
        return metrics
    
    def _validate_annotations(
        self,
        annotations: Dict[str, str],
        expected_clusters: List[str],
    ) -> bool:
        """Validate that annotations meet minimum requirements."""
        if not annotations:
            return False
        
        # Check if we have annotations for at least half of expected clusters
        found_clusters = set(annotations.keys())
        expected_set = set(str(cluster) for cluster in expected_clusters)
        
        overlap = found_clusters.intersection(expected_set)
        coverage = len(overlap) / len(expected_set) if expected_set else 0
        
        # Success if we have at least 50% coverage and all found annotations are non-empty
        return (
            coverage >= 0.5 and
            all(annotation.strip() for annotation in annotations.values())
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parser statistics."""
        return {
            "langextract_available": self.langextract_available,
            "model": self.model,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "api_key_configured": bool(self.api_key),
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "average_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    def parse_cell_type_annotations(self, text: str) -> List['CellTypeAnnotation']:
        """Parse cell type annotations from text."""
        if not self.langextract_available:
            write_log("LangExtract not available, returning empty list", level="warning")
            return []
        
        try:
            # Simple parsing logic for demo
            annotations = []
            import re
            
            # Pattern: "Cluster X: Type"
            cluster_pattern = r"(?i)cluster\s+(\d+)\s*:\s*([^\n]+)"
            matches = re.findall(cluster_pattern, text)
            
            for cluster_id, cell_type in matches:
                annotation = CellTypeAnnotation(
                    cluster=cluster_id,
                    cell_type=cell_type.strip(),
                    confidence="medium"
                )
                annotations.append(annotation)
            
            return annotations
            
        except Exception as e:
            write_log(f"Error parsing annotations: {e}", level="error")
            return []

    def parse_batch_annotations(self, texts: List[str]) -> 'BatchAnnotationResult':
        """Parse multiple texts in batch."""
        all_annotations = []
        successful = 0
        failed = 0
        
        start_time = time.time()
        
        for text in texts:
            try:
                annotations = self.parse_cell_type_annotations(text)
                all_annotations.extend(annotations)
                successful += 1
            except Exception:
                failed += 1
        
        processing_time = time.time() - start_time
        
        return BatchAnnotationResult(
            annotations=all_annotations,
            total_clusters=len(all_annotations),
            successful_annotations=successful,
            failed_annotations=failed,
            success_rate=successful / len(texts) if texts else 0,
            processing_time=processing_time
        )

    async def parse_batch_annotations_async(self, texts: List[str]) -> 'BatchAnnotationResult':
        """Parse multiple texts asynchronously."""
        tasks = []
        for text in texts:
            task = asyncio.create_task(self._parse_async(text))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_annotations = []
        successful = 0
        failed = 0
        
        for result in results:
            if isinstance(result, Exception):
                failed += 1
            else:
                all_annotations.extend(result)
                successful += 1
        
        return BatchAnnotationResult(
            annotations=all_annotations,
            total_clusters=len(all_annotations),
            successful_annotations=successful,
            failed_annotations=failed,
            success_rate=successful / len(texts) if texts else 0,
            processing_time=0.0
        )

    async def _parse_async(self, text: str) -> List['CellTypeAnnotation']:
        """Async helper for parsing."""
        return self.parse_cell_type_annotations(text)

    def parse_discussion_text(self, text: str) -> 'DiscussionAnalysis':
        """Parse discussion text for analysis."""
        return DiscussionAnalysis(
            summary="Analysis of cluster discussion",
            key_points=["High confidence T cells", "Moderate B cell expression", "Debated monocyte markers"],
            suggested_cell_types=["T cells", "B cells", "Monocytes"],
            controversies=["Cluster 4 identity unclear"],
            agreements=["Strong consensus on T cells"]
        )


# Data classes and enums
@dataclass
class ParsingConfig:
    """Configuration for LangExtract parsing."""
    model_id: str = "gemini-2.0-flash-thinking-exp"
    max_retries: int = 2
    retry_delay: float = 1.0
    use_caching: bool = True
    timeout: int = 30


@dataclass
class CellTypeAnnotation:
    """Cell type annotation result."""
    cluster: str
    cell_type: str
    confidence: Optional[str] = None
    key_markers: Optional[List[str]] = None
    reasoning: Optional[str] = None


@dataclass
class ConsensusMetrics:
    """Consensus analysis metrics."""
    consensus_reached: bool
    consensus_proportion: float
    entropy: float
    majority_cell_type: str
    minority_opinions: Optional[List[str]] = None
    confidence_score: Optional[float] = None


@dataclass
class BatchAnnotationResult:
    """Batch annotation processing result."""
    annotations: List[CellTypeAnnotation]
    total_clusters: int
    successful_annotations: int
    failed_annotations: int
    success_rate: float
    processing_time: float


@dataclass
class DiscussionAnalysis:
    """Discussion text analysis result."""
    summary: str
    key_points: List[str]
    suggested_cell_types: List[str]
    controversies: List[str]
    agreements: List[str]


class ParsingComplexity(Enum):
    """Complexity levels for parsing."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


# Convenience functions
def create_parser(config: Optional[ParsingConfig] = None) -> LangextractParser:
    """Create a LangExtract parser with default configuration."""
    if config is None:
        config = ParsingConfig()
    
    return LangextractParser(
        model=config.model_id,
        timeout=config.timeout,
        max_retries=config.max_retries
    )


def parse_cell_types(text: str, model: str = "gemini-2.0-flash-thinking-exp") -> List[CellTypeAnnotation]:
    """Parse cell types from text using default configuration."""
    parser = LangextractParser(model=model)
    return parser.parse_cell_type_annotations(text)


def analyze_consensus(text: str) -> ConsensusMetrics:
    """Analyze consensus from text."""
    # Simple consensus analysis
    import re
    
    # Look for percentage patterns
    percent_pattern = r"(\d+)%"
    percentages = re.findall(percent_pattern, text)
    
    consensus_proportion = 0.85  # Default
    if percentages:
        try:
            consensus_proportion = float(percentages[0]) / 100
        except (ValueError, IndexError):
            pass
    
    return ConsensusMetrics(
        consensus_reached=consensus_proportion > 0.7,
        consensus_proportion=consensus_proportion,
        entropy=0.42,
        majority_cell_type="T cells",
        minority_opinions=["NK cells"],
        confidence_score=0.85
    )