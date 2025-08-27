#!/usr/bin/env python3
"""
Test suite for LangextractParser module

This module contains comprehensive tests for the LangextractParser functionality
including unit tests, integration tests, and performance tests.
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock

# Test imports
try:
    from mllmcelltype.langextract_parser import (
        LangextractParser,
        ParsingConfig,
        CellTypeAnnotation,
        ConsensusMetrics,
        BatchAnnotationResult,
        DiscussionAnalysis,
        ParsingComplexity,
        create_parser,
        parse_cell_types,
        analyze_consensus,
        LANGEXTRACT_AVAILABLE
    )
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False
    pytest.skip("LangextractParser not available", allow_module_level=True)


class TestParsingConfig:
    """Test cases for ParsingConfig model"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ParsingConfig()
        assert config.model_id == "gemini-2.0-flash-thinking-exp"
        assert config.max_retries == 3
        assert config.retry_delay == 2.0
        assert config.timeout == 30.0
        assert config.use_caching is True
        assert config.cache_ttl == 3600
        assert config.complexity_threshold == 0.7
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = ParsingConfig(
            model_id="custom-model",
            max_retries=5,
            retry_delay=1.5,
            timeout=60.0,
            use_caching=False,
            cache_ttl=7200,
            complexity_threshold=0.8
        )
        assert config.model_id == "custom-model"
        assert config.max_retries == 5
        assert config.retry_delay == 1.5
        assert config.timeout == 60.0
        assert config.use_caching is False
        assert config.cache_ttl == 7200
        assert config.complexity_threshold == 0.8
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test invalid max_retries
        with pytest.raises(ValueError):
            ParsingConfig(max_retries=0)
        
        with pytest.raises(ValueError):
            ParsingConfig(max_retries=11)
        
        # Test invalid retry_delay
        with pytest.raises(ValueError):
            ParsingConfig(retry_delay=0.05)
        
        # Test invalid timeout
        with pytest.raises(ValueError):
            ParsingConfig(timeout=1.0)
        
        # Test invalid cache_ttl
        with pytest.raises(ValueError):
            ParsingConfig(cache_ttl=30)
        
        # Test invalid complexity_threshold
        with pytest.raises(ValueError):
            ParsingConfig(complexity_threshold=1.5)


class TestCellTypeAnnotation:
    """Test cases for CellTypeAnnotation model"""
    
    def test_valid_annotation(self):
        """Test valid annotation creation"""
        annotation = CellTypeAnnotation(
            cluster="0",
            cell_type="T cells",
            confidence="high",
            key_markers=["CD3", "CD4"],
            reasoning="High CD3 expression"
        )
        assert annotation.cluster == "0"
        assert annotation.cell_type == "T cells"
        assert annotation.confidence == "high"
        assert annotation.key_markers == ["CD3", "CD4"]
        assert annotation.reasoning == "High CD3 expression"
    
    def test_required_fields(self):
        """Test required field validation"""
        # Valid minimal annotation
        annotation = CellTypeAnnotation(cluster="1", cell_type="B cells")
        assert annotation.cluster == "1"
        assert annotation.cell_type == "B cells"
        
        # Missing cluster
        with pytest.raises(ValueError):
            CellTypeAnnotation(cell_type="T cells")
        
        # Missing cell_type
        with pytest.raises(ValueError):
            CellTypeAnnotation(cluster="0")
        
        # Empty cluster
        with pytest.raises(ValueError):
            CellTypeAnnotation(cluster="", cell_type="T cells")
        
        # Empty cell_type
        with pytest.raises(ValueError):
            CellTypeAnnotation(cluster="0", cell_type="")
    
    def test_field_cleaning(self):
        """Test field cleaning and normalization"""
        annotation = CellTypeAnnotation(
            cluster="  0  ",
            cell_type="  T cells  "
        )
        assert annotation.cluster == "0"
        assert annotation.cell_type == "T cells"


class TestConsensusMetrics:
    """Test cases for ConsensusMetrics model"""
    
    def test_valid_metrics(self):
        """Test valid metrics creation"""
        metrics = ConsensusMetrics(
            consensus_reached=True,
            consensus_proportion=0.85,
            entropy=0.42,
            majority_cell_type="T cells",
            minority_opinions=["NK cells"],
            confidence_score=0.9
        )
        assert metrics.consensus_reached is True
        assert metrics.consensus_proportion == 0.85
        assert metrics.entropy == 0.42
        assert metrics.majority_cell_type == "T cells"
        assert metrics.minority_opinions == ["NK cells"]
        assert metrics.confidence_score == 0.9
    
    def test_validation_ranges(self):
        """Test field validation ranges"""
        # Valid ranges
        metrics = ConsensusMetrics(
            consensus_reached=False,
            consensus_proportion=0.0,
            entropy=0.0,
            majority_cell_type="Unknown"
        )
        assert metrics.consensus_proportion == 0.0
        assert metrics.entropy == 0.0
        
        # Invalid consensus_proportion
        with pytest.raises(ValueError):
            ConsensusMetrics(
                consensus_reached=True,
                consensus_proportion=1.5,
                entropy=0.5,
                majority_cell_type="T cells"
            )
        
        # Invalid entropy (negative)
        with pytest.raises(ValueError):
            ConsensusMetrics(
                consensus_reached=True,
                consensus_proportion=0.8,
                entropy=-0.1,
                majority_cell_type="T cells"
            )


@pytest.mark.skipif(not LANGEXTRACT_AVAILABLE, reason="LangExtract not available")
class TestLangextractParser:
    """Test cases for LangextractParser class"""
    
    def test_parser_initialization(self):
        """Test parser initialization"""
        # Default config
        parser = LangextractParser()
        assert parser.config.model_id == "gemini-2.0-flash-thinking-exp"
        assert parser.config.max_retries == 3
        
        # Custom config
        config = ParsingConfig(max_retries=5)
        parser = LangextractParser(config)
        assert parser.config.max_retries == 5
    
    def test_complexity_detection(self):
        """Test parsing complexity detection"""
        parser = LangextractParser()
        
        # Simple format
        simple_text = "Cluster 0: T cells\nCluster 1: B cells"
        complexity = parser._detect_parsing_complexity(simple_text)
        assert complexity == ParsingComplexity.SIMPLE
        
        # Complex format with JSON
        complex_text = '''```json
        {
          "annotations": [
            {"cluster": "0" "cell_type": "T cells"}
          ]
        }```'''
        complexity = parser._detect_parsing_complexity(complex_text)
        assert complexity in [ParsingComplexity.MODERATE, ParsingComplexity.COMPLEX]
        
        # Very complex natural language
        very_complex_text = """
        Based on the analysis, the first cluster appears to be T cells due to
        high CD3 expression. However, some researchers argue it could be NK cells.
        The second cluster shows CD19+ markers suggesting B cells, but confidence
        is medium due to overlapping expression patterns.
        """
        complexity = parser._detect_parsing_complexity(very_complex_text)
        assert complexity in [ParsingComplexity.COMPLEX, ParsingComplexity.VERY_COMPLEX]
    
    def test_example_selection(self):
        """Test example selection for different complexities"""
        parser = LangextractParser()
        
        # Test simple examples
        examples = parser._get_examples_for_complexity(ParsingComplexity.SIMPLE, "cell_type")
        assert len(examples) >= 1
        assert hasattr(examples[0], 'text')
        assert hasattr(examples[0], 'extractions')
        
        # Test consensus examples
        examples = parser._get_examples_for_complexity(ParsingComplexity.MODERATE, "consensus")
        assert len(examples) >= 1
        assert hasattr(examples[0], 'text')
        assert hasattr(examples[0], 'extractions')
    
    def test_cache_functionality(self):
        """Test caching functionality"""
        config = ParsingConfig(use_caching=True, cache_ttl=10)
        parser = LangextractParser(config)
        
        # Test cache key generation
        key1 = parser._create_cache_key("test text", "cell_type")
        key2 = parser._create_cache_key("test text", "cell_type")
        key3 = parser._create_cache_key("different text", "cell_type")
        
        assert key1 == key2  # Same input should generate same key
        assert key1 != key3  # Different input should generate different key
        
        # Test cache validity
        assert not parser._is_cache_valid("nonexistent_key")
        
        # Add item to cache
        parser._cache["test_key"] = {"result": "test", "timestamp": time.time()}
        assert parser._is_cache_valid("test_key")
        
        # Test cache expiry
        parser._cache["expired_key"] = {"result": "test", "timestamp": time.time() - 20}
        assert not parser._is_cache_valid("expired_key")
    
    def test_result_validation(self):
        """Test extraction result validation"""
        parser = LangextractParser()
        
        # Test invalid results
        assert not parser._validate_extraction_result(None)
        assert not parser._validate_extraction_result(Mock())
        
        # Test valid result
        mock_extraction = Mock()
        mock_extraction.value = "T cells"
        
        mock_result = Mock()
        mock_result.extractions = [mock_extraction]
        
        assert parser._validate_extraction_result(mock_result)
        
        # Test invalid extraction value
        mock_extraction.value = "1"  # Single digit
        assert not parser._validate_extraction_result(mock_result)
    
    @patch('mllmcelltype.langextract_parser.lx')
    def test_extraction_with_retry(self, mock_lx):
        """Test extraction with retry mechanism"""
        parser = LangextractParser(ParsingConfig(max_retries=2, retry_delay=0.1))
        
        # Test successful extraction
        mock_result = Mock()
        mock_lx.extract.return_value = mock_result
        
        result = parser._extract_with_retry("test", "prompt", [])
        assert result == mock_result
        assert mock_lx.extract.call_count == 1
        
        # Test retry on failure
        mock_lx.extract.reset_mock()
        mock_lx.extract.side_effect = [Exception("API Error"), mock_result]
        
        result = parser._extract_with_retry("test", "prompt", [])
        assert result == mock_result
        assert mock_lx.extract.call_count == 2
        
        # Test total failure
        mock_lx.extract.reset_mock()
        mock_lx.extract.side_effect = Exception("Persistent Error")
        
        with pytest.raises(Exception, match="failed after 2 attempts"):
            parser._extract_with_retry("test", "prompt", [])
    
    def test_performance_stats(self):
        """Test performance statistics collection"""
        parser = LangextractParser()
        
        # Add some metrics
        parser._performance_metrics['parse_times'] = [1.0, 2.0, 1.5]
        parser._performance_metrics['success_rates'] = [1.0, 1.0, 0.0]
        parser._performance_metrics['retry_counts'] = [0, 1, 2]
        
        stats = parser.get_performance_stats()
        
        assert 'avg_parse_time' in stats
        assert stats['avg_parse_time'] == 1.5
        assert 'overall_success_rate' in stats
        assert abs(stats['overall_success_rate'] - 0.667) < 0.01
        assert 'avg_retry_count' in stats
        assert stats['avg_retry_count'] == 1.0
        assert stats['total_requests'] == 3
    
    def test_config_update(self):
        """Test configuration updates"""
        parser = LangextractParser()
        original_retries = parser.config.max_retries
        
        parser.update_config(max_retries=5, retry_delay=1.0)
        
        assert parser.config.max_retries == 5
        assert parser.config.retry_delay == 1.0
        assert parser.config.max_retries != original_retries
    
    def test_cache_clearing(self):
        """Test cache clearing"""
        parser = LangextractParser()
        parser._cache["test"] = {"data": "value"}
        
        assert len(parser._cache) > 0
        parser.clear_cache()
        assert len(parser._cache) == 0


class TestConvenienceFunctions:
    """Test cases for convenience functions"""
    
    def test_create_parser(self):
        """Test create_parser function"""
        # Default parser
        parser = create_parser()
        assert isinstance(parser, LangextractParser)
        
        # Custom config
        config = ParsingConfig(max_retries=5)
        parser = create_parser(config)
        assert parser.config.max_retries == 5
    
    @patch('mllmcelltype.langextract_parser.LangextractParser')
    def test_parse_cell_types(self, mock_parser_class):
        """Test parse_cell_types convenience function"""
        mock_parser = Mock()
        mock_annotations = [CellTypeAnnotation(cluster="0", cell_type="T cells")]
        mock_parser.parse_cell_type_annotations.return_value = mock_annotations
        mock_parser_class.return_value = mock_parser
        
        result = parse_cell_types("test text", model_id="custom-model")
        
        assert result == mock_annotations
        mock_parser_class.assert_called_once()
        mock_parser.parse_cell_type_annotations.assert_called_once_with("test text")
    
    @patch('mllmcelltype.langextract_parser.LangextractParser')
    def test_analyze_consensus(self, mock_parser_class):
        """Test analyze_consensus convenience function"""
        mock_parser = Mock()
        mock_metrics = ConsensusMetrics(
            consensus_reached=True,
            consensus_proportion=0.8,
            entropy=0.5,
            majority_cell_type="T cells"
        )
        mock_parser.parse_consensus_metrics.return_value = mock_metrics
        mock_parser_class.return_value = mock_parser
        
        result = analyze_consensus("consensus text")
        
        assert result == mock_metrics
        mock_parser_class.assert_called_once()
        mock_parser.parse_consensus_metrics.assert_called_once_with("consensus text")


@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Test cases for asynchronous functionality"""
    
    @patch('mllmcelltype.langextract_parser.LangextractParser.parse_cell_type_annotations')
    async def test_async_parse_cell_types(self, mock_parse):
        """Test asynchronous cell type parsing"""
        mock_annotations = [CellTypeAnnotation(cluster="0", cell_type="T cells")]
        mock_parse.return_value = mock_annotations
        
        parser = LangextractParser()
        result = await parser.parse_cell_type_annotations_async("test text")
        
        assert result == mock_annotations
        mock_parse.assert_called_once_with("test text")
    
    @patch('mllmcelltype.langextract_parser.LangextractParser.parse_cell_type_annotations_async')
    async def test_async_batch_processing(self, mock_async_parse):
        """Test asynchronous batch processing"""
        mock_annotations = [CellTypeAnnotation(cluster="0", cell_type="T cells")]
        mock_async_parse.return_value = mock_annotations
        
        parser = LangextractParser()
        texts = ["text1", "text2"]
        
        result = await parser.parse_batch_annotations_async(texts)
        
        assert isinstance(result, BatchAnnotationResult)
        assert result.total_clusters == 2
        assert result.successful_annotations == 2  # 2 texts × 1 annotation each
        assert len(result.annotations) == 2
        assert mock_async_parse.call_count == 2


class TestErrorHandling:
    """Test cases for error handling scenarios"""
    
    def test_missing_langextract_import(self):
        """Test behavior when LangExtract is not available"""
        with patch('mllmcelltype.langextract_parser.LANGEXTRACT_AVAILABLE', False):
            with pytest.raises(ImportError, match="LangExtract is not installed"):
                LangextractParser()
    
    @patch('mllmcelltype.langextract_parser.lx')
    def test_api_error_handling(self, mock_lx):
        """Test API error handling"""
        parser = LangextractParser(ParsingConfig(max_retries=1, retry_delay=0.01))
        
        # Mock persistent API failure
        mock_lx.extract.side_effect = Exception("API unavailable")
        
        with pytest.raises(Exception):
            parser.parse_cell_type_annotations("test text")
    
    def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        parser = LangextractParser()
        
        # Test empty text
        with patch.object(parser, '_extract_with_retry') as mock_extract:
            mock_result = Mock()
            mock_result.extractions = []
            mock_extract.return_value = mock_result
            
            with pytest.raises(ValueError, match="failed validation"):
                parser.parse_cell_type_annotations("")


def test_module_imports():
    """Test that all required components can be imported"""
    assert IMPORTS_AVAILABLE, "Required imports not available"
    
    # Test that key classes are available
    assert LangextractParser is not None
    assert ParsingConfig is not None
    assert CellTypeAnnotation is not None
    assert ConsensusMetrics is not None
    assert BatchAnnotationResult is not None
    assert DiscussionAnalysis is not None
    
    # Test that functions are available
    assert create_parser is not None
    assert parse_cell_types is not None
    assert analyze_consensus is not None


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])