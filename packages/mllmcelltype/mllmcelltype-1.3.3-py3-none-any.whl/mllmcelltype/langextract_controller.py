"""
LangExtract Controller for intelligent parsing strategy selection.

This module provides the core logic for determining when to use langextract
versus traditional parsing methods based on complexity assessment.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional, Union

from .logger import write_log


class LangextractController:
    """Controls the intelligent selection between langextract and traditional parsing."""
    
    def __init__(
        self,
        use_langextract: Optional[bool] = None,
        langextract_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the LangExtract controller.
        
        Args:
            use_langextract: Force enable/disable langextract. If None, use auto-detection
            langextract_config: Configuration for langextract parsing
        """
        self.use_langextract = use_langextract
        self.langextract_config = langextract_config or {}
        
        # Default configuration - simplified
        self.default_config = {
            "complexity_threshold": 0.4,  # Lowered threshold for better triggering
            "model": "gemini-2.5-flash",  # Default model for langextract
        }
        
        # Merge user config with defaults
        self.config = {**self.default_config, **self.langextract_config}
        
        # Initialize langextract availability
        self.langextract_available = self._check_langextract_availability()
        
        write_log(
            f"LangExtract Controller initialized. Available: {self.langextract_available}, "
            f"Use langextract: {self.use_langextract}, "
            f"Complexity threshold: {self.config['complexity_threshold']}"
        )
    
    def _check_langextract_availability(self) -> bool:
        """Check if langextract is available and properly configured."""
        try:
            import langextract  # noqa
            
            # Simple check - try to get API key for the model
            from .utils import load_api_key
            from .functions import get_provider
            
            try:
                provider = get_provider(self.config['model'])
                api_key = load_api_key(provider) if provider else None
                
                if api_key:
                    write_log("LangExtract is available with API key", level="info")
                    return True
                else:
                    write_log("LangExtract is available but no API key found", level="warning")
                    return False
            except Exception:
                write_log("LangExtract is available but no API key found", level="warning")
                return False
                
        except ImportError as e:
            write_log(f"LangExtract not available: {e}", level="warning")
            return False
    
    def should_use_langextract(
        self, 
        results: List[str], 
        clusters: List[str]
    ) -> Dict[str, Any]:
        """Determine whether to use langextract based on complexity assessment.
        
        Args:
            results: List of annotation results from LLM
            clusters: List of cluster names
            
        Returns:
            Dict with decision, complexity score, and reasoning
        """
        start_time = time.time()
        
        # If explicitly disabled, return False
        if self.use_langextract is False:
            return {
                "use_langextract": False,
                "reason": "Explicitly disabled by configuration",
                "complexity_score": 0.0,
                "assessment_time": time.time() - start_time,
                "fallback_available": True,
            }
        
        # If explicitly enabled, check availability first
        if self.use_langextract is True:
            if not self.langextract_available:
                return {
                    "use_langextract": False,
                    "reason": "Explicitly enabled but langextract not available",
                    "complexity_score": 1.0,
                    "assessment_time": time.time() - start_time,
                    "fallback_available": True,
                }
            else:
                return {
                    "use_langextract": True,
                    "reason": "Explicitly enabled and available",
                    "complexity_score": 1.0,
                    "assessment_time": time.time() - start_time,
                    "fallback_available": True,
                }
        
        # Auto-detection mode - assess complexity
        if not self.langextract_available:
            return {
                "use_langextract": False,
                "reason": "LangExtract not available for auto-detection",
                "complexity_score": 0.0,
                "assessment_time": time.time() - start_time,
                "fallback_available": True,
            }
        
        # Perform complexity assessment
        complexity_result = self._assess_complexity(results, clusters)
        use_langextract = complexity_result["complexity_score"] >= self.config["complexity_threshold"]
        
        reason = (
            f"Complexity score {complexity_result['complexity_score']:.3f} "
            f"{'≥' if use_langextract else '<'} threshold {self.config['complexity_threshold']}"
        )
        
        result = {
            "use_langextract": use_langextract,
            "reason": reason,
            "complexity_score": complexity_result["complexity_score"],
            "complexity_factors": complexity_result["factors"],
            "assessment_time": time.time() - start_time,
            "fallback_available": True,
        }
        
        write_log(
            f"Strategy decision: {'LangExtract' if use_langextract else 'Traditional'} "
            f"(score: {complexity_result['complexity_score']:.3f}, "
            f"time: {result['assessment_time']:.3f}s)"
        )
        
        return result
    
    def _assess_complexity(self, results: List[str], clusters: List[str]) -> Dict[str, Any]:
        """Assess the complexity of parsing task to determine optimal strategy.
        
        Args:
            results: List of annotation results from LLM
            clusters: List of cluster names
            
        Returns:
            Dict with complexity score and contributing factors
        """
        # Clean up results
        clean_results = [line.strip() for line in results if line.strip()]
        full_text = "\n".join(clean_results)
        
        factors = {}
        complexity_score = 0.0
        
        # Factor 1: JSON structure complexity (0.0-0.3)
        json_complexity = self._assess_json_complexity(full_text)
        factors["json_complexity"] = json_complexity
        complexity_score += json_complexity * 0.3
        
        # Factor 2: Format inconsistency (0.0-0.25)
        format_inconsistency = self._assess_format_inconsistency(clean_results, clusters)
        factors["format_inconsistency"] = format_inconsistency
        complexity_score += format_inconsistency * 0.25
        
        # Factor 3: Natural language complexity (0.0-0.2)
        natural_language_complexity = self._assess_natural_language_complexity(full_text)
        factors["natural_language_complexity"] = natural_language_complexity
        complexity_score += natural_language_complexity * 0.2
        
        # Factor 4: Parsing difficulty indicators (0.0-0.15)
        parsing_difficulty = self._assess_parsing_difficulty(full_text)
        factors["parsing_difficulty"] = parsing_difficulty
        complexity_score += parsing_difficulty * 0.15
        
        # Factor 5: Traditional method failure prediction (0.0-0.1)
        traditional_failure_risk = self._assess_traditional_failure_risk(clean_results, clusters)
        factors["traditional_failure_risk"] = traditional_failure_risk
        complexity_score += traditional_failure_risk * 0.1
        
        # Ensure complexity score is within bounds
        complexity_score = max(0.0, min(1.0, complexity_score))
        
        return {
            "complexity_score": complexity_score,
            "factors": factors,
            "total_lines": len(clean_results),
            "total_characters": len(full_text),
        }
    
    def _assess_json_complexity(self, text: str) -> float:
        """Assess JSON structure complexity."""
        json_indicators = 0.0
        
        # Check for JSON code blocks
        if re.search(r"```(?:json)?\s*\{", text):
            json_indicators += 0.3
            
            # Check for malformed JSON patterns
            malformed_patterns = [
                r'\{[^}]*"[^"]*"[^,}\]]*"[^"]*"[^,}\]]*\}',  # Missing commas
                r'("[^"]+")\s*\n\s*("[^"]+"):',  # Line breaks in properties
                r'"[^"]*\'|\'[^"]*"',  # Mixed quotes
                r'\},\s*\]|\],\s*\}',  # Trailing commas
                r'\{\s*\}|\[\s*\]',  # Empty objects/arrays
                r'//.*|/\*.*?\*/',  # Comments in JSON
            ]
            
            malformed_count = sum(1 for pattern in malformed_patterns if re.search(pattern, text))
            json_indicators += min(0.7, malformed_count * 0.2)
        
        return min(1.0, json_indicators)
    
    def _assess_format_inconsistency(self, results: List[str], clusters: List[str]) -> float:
        """Assess format inconsistency across results."""
        if not results:
            return 0.0
        
        # Analyze format patterns
        format_patterns = {
            "cluster_colon": 0,  # "Cluster X: Type"
            "numbered_list": 0,  # "1. Type"
            "bullet_points": 0,  # "- Type"
            "json_objects": 0,   # JSON-like structures
            "natural_language": 0,  # Descriptive sentences
            "mixed_format": 0,   # Multiple formats in one line
        }
        
        for line in results:
            line_patterns = 0
            
            if re.search(r"(?i)cluster\s+\d+\s*:", line):
                format_patterns["cluster_colon"] += 1
                line_patterns += 1
            
            if re.search(r"^\s*\d+\.\s+", line):
                format_patterns["numbered_list"] += 1
                line_patterns += 1
            
            if re.search(r"^\s*[-*]\s+", line):
                format_patterns["bullet_points"] += 1
                line_patterns += 1
            
            if re.search(r'[{"].*["}]', line):
                format_patterns["json_objects"] += 1
                line_patterns += 1
            
            if len(line.split()) > 8 and not re.search(r"cluster\s+\d+|^\d+\.|^[-*]", line.lower()):
                format_patterns["natural_language"] += 1
                line_patterns += 1
            
            if line_patterns > 1:
                format_patterns["mixed_format"] += 1
        
        # Calculate inconsistency score
        active_formats = sum(1 for count in format_patterns.values() if count > 0)
        if active_formats <= 1:
            return 0.0  # Consistent format
        elif active_formats == 2:
            return 0.3  # Minor inconsistency
        else:
            return min(1.0, 0.5 + (active_formats - 2) * 0.25)  # Major inconsistency
    
    def _assess_natural_language_complexity(self, text: str) -> float:
        """Assess natural language complexity."""
        complexity = 0.0
        
        # Check for descriptive language patterns
        descriptive_patterns = [
            r"(?i)based on.*markers?",
            r"(?i)according to.*expression",
            r"(?i)suggests?.*cell type",
            r"(?i)indicates?.*phenotype",
            r"(?i)consistent with.*population",
            r"(?i)likely.*represents?",
        ]
        
        pattern_count = sum(1 for pattern in descriptive_patterns if re.search(pattern, text))
        complexity += min(0.6, pattern_count * 0.15)
        
        # Check for reasoning and explanations
        if re.search(r"(?i)(because|due to|since|given that)", text):
            complexity += 0.2
        
        # Check for complex sentence structures
        sentence_complexity = len(re.findall(r"[.!?]+", text))
        if sentence_complexity > len(text.split("\n")) * 0.5:  # More sentences than lines
            complexity += 0.2
        
        return min(1.0, complexity)
    
    def _assess_parsing_difficulty(self, text: str) -> float:
        """Assess general parsing difficulty indicators."""
        difficulty = 0.0
        
        # Check for problematic characters and patterns
        problematic_patterns = [
            r"[^\x00-\x7F]",  # Non-ASCII characters
            r"\\[rntf]|\\u[0-9a-fA-F]{4}",  # Escape sequences
            r"\$[^$]*\$",  # LaTeX-like formatting
            r"\*{2,}|\*[^*]*\*",  # Markdown emphasis
            r"```[^`]*```",  # Code blocks
            r"#{1,6}\s",  # Markdown headers
        ]
        
        pattern_count = sum(1 for pattern in problematic_patterns if re.search(pattern, text))
        difficulty += min(0.5, pattern_count * 0.1)
        
        # Check for encoding issues
        if "?" in text or "�" in text:
            difficulty += 0.2
        
        # Check for extremely long lines (potential formatting issues)
        lines = text.split("\n")
        long_line_count = sum(1 for line in lines if len(line) > 200)
        if long_line_count > 0:
            difficulty += min(0.3, long_line_count * 0.1)
        
        return min(1.0, difficulty)
    
    def _assess_traditional_failure_risk(self, results: List[str], clusters: List[str]) -> float:
        """Predict likelihood of traditional parsing failure."""
        risk = 0.0
        
        if not results or not clusters:
            return 1.0  # High risk if no input
        
        # Check if number of results matches clusters
        if len(results) != len(clusters):
            risk += 0.4
        
        # Check for obvious parsing challenges
        challenge_patterns = [
            r"(?i)error|failed|invalid",
            r"(?i)unable to|cannot|could not",
            r"(?i)unclear|ambiguous|uncertain",
            r"\?\?\?|…|\.{3,}",  # Uncertainty indicators
        ]
        
        challenge_count = sum(1 for result in results 
                             for pattern in challenge_patterns 
                             if re.search(pattern, result))
        
        risk += min(0.4, challenge_count * 0.1)
        
        # Check for empty or very short results
        empty_count = sum(1 for result in results if len(result.strip()) < 3)
        risk += min(0.2, empty_count * 0.05)
        
        return min(1.0, risk)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            **self.config,
            "use_langextract": self.use_langextract,
            "langextract_available": self.langextract_available,
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration."""
        self.config.update(new_config)
        write_log(f"LangExtract Controller configuration updated: {new_config}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "langextract_available": self.langextract_available,
            "current_threshold": self.config["complexity_threshold"],
            "model": self.config.get("model", "gemini-2.5-flash"),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert controller configuration to dictionary for serialization."""
        return {
            "use_langextract": self.use_langextract,
            "langextract_available": self.langextract_available,
            "config": self.config.copy(),
            "class": "LangextractController"
        }


# Factory functions for creating pre-configured controllers
def create_default_controller() -> LangextractController:
    """Create a controller with default settings.
    
    Returns:
        LangextractController: Controller with default configuration
    """
    return LangextractController()


def create_conservative_controller() -> LangextractController:
    """Create a controller with conservative settings (higher threshold).
    
    Conservative settings use a higher complexity threshold, requiring stronger
    indicators before switching to langextract parsing.
    
    Returns:
        LangextractController: Controller with conservative configuration
    """
    conservative_config = {
        "complexity_threshold": 0.7,
    }
    return LangextractController(langextract_config=conservative_config)


def create_aggressive_controller() -> LangextractController:
    """Create a controller with aggressive settings (lower threshold).
    
    Aggressive settings use a lower complexity threshold, switching to
    langextract parsing more readily.
    
    Returns:
        LangextractController: Controller with aggressive configuration
    """
    aggressive_config = {
        "complexity_threshold": 0.2,
    }
    return LangextractController(langextract_config=aggressive_config)