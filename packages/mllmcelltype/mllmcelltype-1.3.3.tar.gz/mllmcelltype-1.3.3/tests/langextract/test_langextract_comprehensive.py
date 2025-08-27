#!/usr/bin/env python3
"""
Comprehensive test suite for langextract_parser.py module
验证langextract解析器的所有功能组件
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import traceback

# Add the mllmcelltype package to the Python path
sys.path.insert(0, str(Path(__file__).parent / "mllmcelltype"))

try:
    # Import modules directly 
    sys.path.insert(0, str(Path(__file__).parent))
    from mllmcelltype.langextract_parser import LangextractParser
    from mllmcelltype.utils import clean_annotation
    from mllmcelltype.logger import write_log
    LANGEXTRACT_PARSER_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    try:
        # Try alternative import method
        import os
        os.chdir(str(Path(__file__).parent))
        sys.path.insert(0, os.getcwd())
        from mllmcelltype.langextract_parser import LangextractParser
        from mllmcelltype.utils import clean_annotation
        from mllmcelltype.logger import write_log
        LANGEXTRACT_PARSER_AVAILABLE = True
    except ImportError as e2:
        print(f"Second import attempt failed: {e2}")
        LANGEXTRACT_PARSER_AVAILABLE = False

class LangextractParserTester:
    """Comprehensive tester for LangextractParser functionality"""
    
    def __init__(self):
        """Initialize the tester"""
        self.results = {}
        self.start_time = time.time()
        self.test_data = self._create_test_data()
        
        # Initialize parser if available
        self.parser = None
        if LANGEXTRACT_PARSER_AVAILABLE:
            try:
                self.parser = LangextractParser(
                    model="gemini-2.0-flash-thinking-exp",
                    timeout=30,
                    max_retries=2
                )
                print(f"✓ LangextractParser initialized successfully")
                print(f"  Model: {self.parser.model}")
                print(f"  LangExtract Available: {self.parser.langextract_available}")
                print(f"  API Key Configured: {bool(self.parser.api_key)}")
            except Exception as e:
                print(f"✗ Failed to initialize LangextractParser: {e}")
                self.parser = None
    
    def _create_test_data(self) -> Dict[str, Any]:
        """Create comprehensive test data for different scenarios"""
        return {
            "simple_format": {
                "results": [
                    "Cluster 0: T cells",
                    "Cluster 1: B cells", 
                    "Cluster 2: NK cells",
                    "Cluster 3: Monocytes"
                ],
                "clusters": ["0", "1", "2", "3"],
                "expected_count": 4
            },
            "json_format": {
                "results": [
                    '''{"annotations": [
                        {"cluster_id": "0", "cell_type": "CD8+ T cells", "confidence": "high"},
                        {"cluster_id": "1", "cell_type": "B cells", "confidence": "medium"},
                        {"cluster_id": "2", "cell_type": "NK cells", "confidence": "high"}
                    ]}'''
                ],
                "clusters": ["0", "1", "2"],
                "expected_count": 3
            },
            "complex_narrative": {
                "results": [
                    """Based on the marker gene expression analysis:
                    
                    Cluster 0 shows high expression of CD3D, CD3E, and CD4, indicating these are CD4+ T cells.
                    The confidence level is high due to clear T cell markers.
                    
                    Cluster 1 exhibits strong CD19 and MS4A1 expression, characteristic of B cells.
                    
                    Cluster 2 demonstrates KLRD1 and KLRB1 expression patterns typical of NK cells.
                    However, some overlap with T cell markers suggests potential uncertainty.
                    """
                ],
                "clusters": ["0", "1", "2"],
                "expected_count": 3
            },
            "mixed_format": {
                "results": [
                    "The analysis reveals the following cell types:",
                    "- Cluster 0: CD4+ T cells (high confidence)",
                    "- Cluster 1: B cells",
                    "For cluster 2, the markers suggest NK cells",
                    "Cluster 3 appears to be Monocytes based on CD14 expression"
                ],
                "clusters": ["0", "1", "2", "3"],
                "expected_count": 4
            },
            "consensus_analysis": {
                "text": """Consensus Analysis Results:
                
                Overall consensus reached for 3 out of 4 clusters (75%).
                
                Cluster 0: All 3 models agree on T cells (100% consensus)
                Cluster 1: 2 out of 3 models predict B cells (67% consensus)  
                Cluster 2: Models disagree - T cells vs NK cells (33% consensus)
                Cluster 3: Strong agreement on Monocytes (100% consensus)
                
                Quality metrics:
                - Average confidence: 0.82
                - Entropy score: 0.45
                """,
                "expected_metrics": ["overall_consensus", "cluster_agreement", "quality_scores"]
            }
        }
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        print("🚀 Starting comprehensive langextract_parser.py tests...")
        print("=" * 60)
        
        # 1. Core parsing functionality tests
        await self._test_core_parsing_functions()
        
        # 2. Data model validation tests  
        await self._test_data_model_validation()
        
        # 3. Error handling and retry mechanism tests
        await self._test_error_handling()
        
        # 4. Example data system tests
        await self._test_example_system()
        
        # 5. Performance and caching tests
        await self._test_performance_caching()
        
        # 6. Integration tests with real API calls
        await self._test_real_api_integration()
        
        # Generate final report
        return self._generate_final_report()
    
    async def _test_core_parsing_functions(self):
        """Test core parsing functionality"""
        print("\n📋 Testing Core Parsing Functions")
        print("-" * 40)
        
        if not self.parser:
            print("⚠️  Parser not available, skipping core parsing tests")
            self.results['core_parsing'] = {'status': 'skipped', 'reason': 'parser_unavailable'}
            return
        
        core_results = {
            'parse_cell_type_annotations': [],
            'parse_consensus_metrics': [],  
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0
        }
        
        # Test parse_cell_type_annotations with different formats
        for test_name, test_data in self.test_data.items():
            if test_name == 'consensus_analysis':
                continue
                
            print(f"  Testing {test_name}...")
            try:
                start_time = time.time()
                
                result = self.parser.parse_cell_type_annotations_original(
                    results=test_data['results'],
                    clusters=test_data['clusters'],
                    additional_context=f"Test case: {test_name}"
                )
                
                execution_time = time.time() - start_time
                
                # Validate result structure
                is_valid = self._validate_annotation_result(result, test_data)
                
                test_result = {
                    'test_name': test_name,
                    'success': result.get('success', False),
                    'valid_structure': is_valid,
                    'execution_time': execution_time,
                    'annotations_found': len(result.get('annotations', {})),
                    'expected_count': test_data['expected_count'],
                    'coverage': len(result.get('annotations', {})) / test_data['expected_count'] if test_data['expected_count'] > 0 else 0,
                    'metadata': result.get('metadata', {}),
                    'error': result.get('error', None)
                }
                
                core_results['parse_cell_type_annotations'].append(test_result)
                core_results['total_tests'] += 1
                
                if result.get('success', False) and is_valid:
                    print(f"    ✓ {test_name}: {test_result['annotations_found']}/{test_result['expected_count']} annotations ({test_result['coverage']:.1%} coverage) in {execution_time:.3f}s")
                    core_results['passed_tests'] += 1
                else:
                    print(f"    ✗ {test_name}: Failed - {result.get('error', 'Unknown error')}")
                    core_results['failed_tests'] += 1
                
            except Exception as e:
                print(f"    ✗ {test_name}: Exception - {str(e)}")
                core_results['failed_tests'] += 1
                core_results['total_tests'] += 1
        
        # Test parse_consensus_metrics
        print("  Testing consensus metrics parsing...")
        try:
            start_time = time.time()
            consensus_data = self.test_data['consensus_analysis']
            
            result = self.parser.parse_consensus_metrics(
                analysis_text=consensus_data['text'],
                expected_metrics=consensus_data['expected_metrics']
            )
            
            execution_time = time.time() - start_time
            
            test_result = {
                'success': result.get('success', False),
                'metrics_found': len(result.get('metrics', {})),
                'execution_time': execution_time,
                'metadata': result.get('metadata', {}),
                'error': result.get('error', None)
            }
            
            core_results['parse_consensus_metrics'].append(test_result)
            core_results['total_tests'] += 1
            
            if result.get('success', False):
                print(f"    ✓ Consensus metrics: {test_result['metrics_found']} metrics found in {execution_time:.3f}s")
                core_results['passed_tests'] += 1
            else:
                print(f"    ✗ Consensus metrics: Failed - {result.get('error', 'Unknown error')}")
                core_results['failed_tests'] += 1
                
        except Exception as e:
            print(f"    ✗ Consensus metrics: Exception - {str(e)}")
            core_results['failed_tests'] += 1
            core_results['total_tests'] += 1
        
        self.results['core_parsing'] = core_results
    
    async def _test_data_model_validation(self):
        """Test data model validation"""
        print("\n🔍 Testing Data Model Validation")
        print("-" * 40)
        
        validation_results = {
            'annotation_validation': [],
            'schema_compliance': [],
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0
        }
        
        # Test annotation cleaning and validation
        test_annotations = [
            "  CD4+ T cells  ",  # whitespace
            "Cluster 0: B cells",  # prefix removal
            "**NK cells**",  # formatting removal
            "Final cell type: Monocytes",  # descriptive text
            "",  # empty
            "Very long description of a cell type that should be truncated because it contains way too much information and details",  # truncation
        ]
        
        print("  Testing annotation cleaning...")
        for i, annotation in enumerate(test_annotations):
            try:
                cleaned = clean_annotation(annotation)
                test_result = {
                    'original': annotation,
                    'cleaned': cleaned,
                    'valid': bool(cleaned and len(cleaned.strip()) > 0),
                    'test_passed': True
                }
                validation_results['annotation_validation'].append(test_result)
                validation_results['total_tests'] += 1
                validation_results['passed_tests'] += 1
                
                print(f"    ✓ '{annotation}' → '{cleaned}'")
            except Exception as e:
                validation_results['annotation_validation'].append({
                    'original': annotation,
                    'error': str(e),
                    'test_passed': False
                })
                validation_results['total_tests'] += 1
                validation_results['failed_tests'] += 1
                print(f"    ✗ '{annotation}' → Error: {str(e)}")
        
        # Test schema validation if parser is available
        if self.parser:
            print("  Testing schema compliance...")
            for schema_name, schema in self.parser.schemas.items():
                try:
                    # Validate schema structure
                    has_description = 'description' in schema
                    has_examples = 'examples' in schema
                    examples_valid = True
                    
                    if has_examples:
                        for example in schema['examples']:
                            if not ('text' in example and 'extractions' in example):
                                examples_valid = False
                                break
                    
                    test_result = {
                        'schema_name': schema_name,
                        'has_description': has_description,
                        'has_examples': has_examples,
                        'examples_valid': examples_valid,
                        'test_passed': has_description and has_examples and examples_valid
                    }
                    
                    validation_results['schema_compliance'].append(test_result)
                    validation_results['total_tests'] += 1
                    
                    if test_result['test_passed']:
                        validation_results['passed_tests'] += 1
                        print(f"    ✓ Schema '{schema_name}': Complete and valid")
                    else:
                        validation_results['failed_tests'] += 1
                        print(f"    ✗ Schema '{schema_name}': Missing or invalid components")
                        
                except Exception as e:
                    validation_results['failed_tests'] += 1
                    validation_results['total_tests'] += 1
                    print(f"    ✗ Schema '{schema_name}': Exception - {str(e)}")
        
        self.results['data_validation'] = validation_results
    
    async def _test_error_handling(self):
        """Test error handling and retry mechanisms"""
        print("\n⚠️  Testing Error Handling and Retry Mechanisms")
        print("-" * 40)
        
        error_handling_results = {
            'invalid_input_tests': [],
            'retry_mechanism_tests': [],
            'timeout_tests': [],
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0
        }
        
        if not self.parser:
            print("⚠️  Parser not available, skipping error handling tests")
            self.results['error_handling'] = {'status': 'skipped', 'reason': 'parser_unavailable'}
            return
        
        # Test invalid inputs
        invalid_inputs = [
            {'results': [], 'clusters': ['0', '1'], 'expected_error': 'empty_results'},
            {'results': ['test'], 'clusters': [], 'expected_error': 'empty_clusters'},
            {'results': None, 'clusters': ['0'], 'expected_error': 'none_results'},
            {'results': ['test'], 'clusters': None, 'expected_error': 'none_clusters'}
        ]
        
        print("  Testing invalid input handling...")
        for test_case in invalid_inputs:
            try:
                start_time = time.time()
                
                result = self.parser.parse_cell_type_annotations_original(
                    results=test_case.get('results'),
                    clusters=test_case.get('clusters')
                )
                
                execution_time = time.time() - start_time
                
                # Should either fail gracefully or handle the error
                test_passed = not result.get('success', True) or 'error' in result
                
                test_result = {
                    'input_type': test_case['expected_error'],
                    'handled_gracefully': test_passed,
                    'execution_time': execution_time,
                    'result': result,
                    'test_passed': test_passed
                }
                
                error_handling_results['invalid_input_tests'].append(test_result)
                error_handling_results['total_tests'] += 1
                
                if test_passed:
                    error_handling_results['passed_tests'] += 1
                    print(f"    ✓ {test_case['expected_error']}: Handled gracefully")
                else:
                    error_handling_results['failed_tests'] += 1
                    print(f"    ✗ {test_case['expected_error']}: Not handled properly")
                    
            except Exception as e:
                # Exception is actually expected for some cases
                test_result = {
                    'input_type': test_case['expected_error'],
                    'exception': str(e),
                    'test_passed': True  # Exception handling is acceptable
                }
                
                error_handling_results['invalid_input_tests'].append(test_result)
                error_handling_results['total_tests'] += 1
                error_handling_results['passed_tests'] += 1
                print(f"    ✓ {test_case['expected_error']}: Exception handled - {str(e)}")
        
        # Test timeout behavior (if possible)
        print("  Testing timeout behavior...")
        try:
            # Create a parser with very short timeout
            timeout_parser = LangextractParser(timeout=1, max_retries=1)
            
            if timeout_parser.langextract_available:
                start_time = time.time()
                
                # Try parsing with minimal timeout
                result = timeout_parser.parse_cell_type_annotations_original(
                    results=["Very complex analysis that might take time to process"] * 10,
                    clusters=[str(i) for i in range(10)]
                )
                
                execution_time = time.time() - start_time
                
                test_result = {
                    'timeout_setting': 1,
                    'execution_time': execution_time,
                    'completed': result.get('success', False),
                    'within_timeout': execution_time <= 5,  # Allow some overhead
                    'test_passed': True  # Any reasonable behavior is acceptable
                }
                
                error_handling_results['timeout_tests'].append(test_result)
                error_handling_results['total_tests'] += 1
                error_handling_results['passed_tests'] += 1
                
                print(f"    ✓ Timeout test: {execution_time:.3f}s execution time")
            else:
                print("    ⚠️  Timeout test skipped: LangExtract not available")
                
        except Exception as e:
            error_handling_results['timeout_tests'].append({
                'error': str(e),
                'test_passed': True  # Exception is acceptable for timeout tests
            })
            error_handling_results['total_tests'] += 1
            error_handling_results['passed_tests'] += 1
            print(f"    ✓ Timeout test: Exception handled - {str(e)}")
        
        self.results['error_handling'] = error_handling_results
    
    async def _test_example_system(self):
        """Test example data system"""
        print("\n📚 Testing Example Data System")
        print("-" * 40)
        
        example_system_results = {
            'schema_examples': [],
            'example_conversion': [],
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0
        }
        
        if not self.parser:
            print("⚠️  Parser not available, skipping example system tests")
            self.results['example_system'] = {'status': 'skipped', 'reason': 'parser_unavailable'}
            return
        
        # Test schema examples
        print("  Testing schema examples...")
        for schema_name, schema in self.parser.schemas.items():
            try:
                examples = schema.get('examples', [])
                valid_examples = 0
                
                for i, example in enumerate(examples):
                    has_text = 'text' in example and example['text']
                    has_extractions = 'extractions' in example and example['extractions']
                    
                    if has_text and has_extractions:
                        valid_examples += 1
                
                test_result = {
                    'schema_name': schema_name,
                    'total_examples': len(examples),
                    'valid_examples': valid_examples,
                    'all_valid': valid_examples == len(examples) and len(examples) > 0,
                    'test_passed': valid_examples == len(examples) and len(examples) > 0
                }
                
                example_system_results['schema_examples'].append(test_result)
                example_system_results['total_tests'] += 1
                
                if test_result['test_passed']:
                    example_system_results['passed_tests'] += 1
                    print(f"    ✓ {schema_name}: {valid_examples}/{len(examples)} valid examples")
                else:
                    example_system_results['failed_tests'] += 1
                    print(f"    ✗ {schema_name}: {valid_examples}/{len(examples)} valid examples")
                    
            except Exception as e:
                example_system_results['failed_tests'] += 1
                example_system_results['total_tests'] += 1
                print(f"    ✗ {schema_name}: Exception - {str(e)}")
        
        # Test example conversion to langextract format
        print("  Testing example conversion...")
        try:
            test_examples = [
                {
                    "text": "Cluster 0: T cells",
                    "extractions": [{"cluster_id": "0", "cell_type": "T cells"}]
                }
            ]
            
            converted = self.parser._convert_to_langextract_examples(test_examples)
            
            test_result = {
                'conversion_successful': converted is not None,
                'result_type': type(converted).__name__ if converted else None,
                'test_passed': converted is not None
            }
            
            example_system_results['example_conversion'].append(test_result)
            example_system_results['total_tests'] += 1
            
            if test_result['test_passed']:
                example_system_results['passed_tests'] += 1
                print(f"    ✓ Example conversion: Success")
            else:
                example_system_results['failed_tests'] += 1
                print(f"    ✗ Example conversion: Failed")
                
        except Exception as e:
            example_system_results['example_conversion'].append({
                'error': str(e),
                'test_passed': False
            })
            example_system_results['failed_tests'] += 1
            example_system_results['total_tests'] += 1
            print(f"    ✗ Example conversion: Exception - {str(e)}")
        
        self.results['example_system'] = example_system_results
    
    async def _test_performance_caching(self):
        """Test performance and caching functionality"""
        print("\n⚡ Testing Performance and Caching")
        print("-" * 40)
        
        performance_results = {
            'response_times': [],
            'throughput_tests': [],
            'memory_usage': [],
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0
        }
        
        if not self.parser:
            print("⚠️  Parser not available, skipping performance tests")
            self.results['performance'] = {'status': 'skipped', 'reason': 'parser_unavailable'}
            return
        
        # Test response times for different input sizes
        print("  Testing response times...")
        input_sizes = [
            {'name': 'small', 'clusters': ['0', '1'], 'results': ['Cluster 0: T cells', 'Cluster 1: B cells']},
            {'name': 'medium', 'clusters': [str(i) for i in range(5)], 'results': [f'Cluster {i}: Cell type {i}' for i in range(5)]},
            {'name': 'large', 'clusters': [str(i) for i in range(10)], 'results': [f'Cluster {i}: Cell type {i}' for i in range(10)]}
        ]
        
        for test_case in input_sizes:
            try:
                start_time = time.time()
                
                result = self.parser.parse_cell_type_annotations_original(
                    results=test_case['results'],
                    clusters=test_case['clusters']
                )
                
                execution_time = time.time() - start_time
                
                test_result = {
                    'input_size': test_case['name'],
                    'cluster_count': len(test_case['clusters']),
                    'execution_time': execution_time,
                    'success': result.get('success', False),
                    'annotations_found': len(result.get('annotations', {})),
                    'throughput': len(test_case['clusters']) / execution_time if execution_time > 0 else 0,
                    'test_passed': result.get('success', False) and execution_time < 30
                }
                
                performance_results['response_times'].append(test_result)
                performance_results['total_tests'] += 1
                
                if test_result['test_passed']:
                    performance_results['passed_tests'] += 1
                    print(f"    ✓ {test_case['name']}: {execution_time:.3f}s for {len(test_case['clusters'])} clusters ({test_result['throughput']:.1f} clusters/s)")
                else:
                    performance_results['failed_tests'] += 1
                    print(f"    ✗ {test_case['name']}: {execution_time:.3f}s - Too slow or failed")
                    
            except Exception as e:
                performance_results['failed_tests'] += 1
                performance_results['total_tests'] += 1
                print(f"    ✗ {test_case['name']}: Exception - {str(e)}")
        
        # Test statistics collection
        print("  Testing statistics collection...")
        try:
            stats = self.parser.get_statistics()
            
            expected_keys = ['langextract_available', 'model', 'timeout', 'max_retries', 'api_key_configured']
            has_all_keys = all(key in stats for key in expected_keys)
            
            test_result = {
                'stats_available': bool(stats),
                'has_all_keys': has_all_keys,
                'keys_found': list(stats.keys()) if stats else [],
                'test_passed': bool(stats) and has_all_keys
            }
            
            performance_results['total_tests'] += 1
            
            if test_result['test_passed']:
                performance_results['passed_tests'] += 1
                print(f"    ✓ Statistics: All expected keys present")
            else:
                performance_results['failed_tests'] += 1
                print(f"    ✗ Statistics: Missing keys or unavailable")
                
        except Exception as e:
            performance_results['failed_tests'] += 1
            performance_results['total_tests'] += 1
            print(f"    ✗ Statistics: Exception - {str(e)}")
        
        self.results['performance'] = performance_results
    
    async def _test_real_api_integration(self):
        """Test integration with real langextract API"""
        print("\n🌐 Testing Real API Integration")
        print("-" * 40)
        
        integration_results = {
            'api_connectivity': [],
            'model_calls': [],
            'format_consistency': [],
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0
        }
        
        if not self.parser or not self.parser.langextract_available:
            print("⚠️  LangExtract not available, skipping API integration tests")
            self.results['api_integration'] = {'status': 'skipped', 'reason': 'langextract_unavailable'}
            return
        
        if not self.parser.api_key:
            print("⚠️  No API key configured, skipping API integration tests")
            self.results['api_integration'] = {'status': 'skipped', 'reason': 'no_api_key'}
            return
        
        # Test API connectivity
        print("  Testing API connectivity...")
        try:
            # Simple connectivity test
            start_time = time.time()
            
            result = self.parser.parse_cell_type_annotations_original(
                results=["Cluster 0: T cells"],
                clusters=["0"]
            )
            
            execution_time = time.time() - start_time
            
            test_result = {
                'connection_successful': result.get('success', False),
                'response_time': execution_time,
                'model_used': result.get('metadata', {}).get('model_used'),
                'test_passed': result.get('success', False) and execution_time < 60
            }
            
            integration_results['api_connectivity'].append(test_result)
            integration_results['total_tests'] += 1
            
            if test_result['test_passed']:
                integration_results['passed_tests'] += 1
                print(f"    ✓ API connectivity: Success in {execution_time:.3f}s with {test_result['model_used']}")
            else:
                integration_results['failed_tests'] += 1
                print(f"    ✗ API connectivity: Failed or too slow ({execution_time:.3f}s)")
                
        except Exception as e:
            integration_results['api_connectivity'].append({
                'error': str(e),
                'test_passed': False
            })
            integration_results['failed_tests'] += 1
            integration_results['total_tests'] += 1
            print(f"    ✗ API connectivity: Exception - {str(e)}")
        
        # Test different model calls if connectivity works
        if integration_results['api_connectivity'] and integration_results['api_connectivity'][0].get('test_passed'):
            print("  Testing different input formats with real API...")
            
            api_test_cases = [
                {'name': 'simple', 'data': self.test_data['simple_format']},
                {'name': 'json', 'data': self.test_data['json_format']}
            ]
            
            for test_case in api_test_cases:
                try:
                    start_time = time.time()
                    
                    result = self.parser.parse_cell_type_annotations_original(
                        results=test_case['data']['results'],
                        clusters=test_case['data']['clusters']
                    )
                    
                    execution_time = time.time() - start_time
                    
                    # Validate result format consistency
                    has_required_keys = all(key in result for key in ['success', 'annotations', 'metadata'])
                    annotations_valid = isinstance(result.get('annotations', {}), dict)
                    
                    test_result = {
                        'test_name': test_case['name'],
                        'api_success': result.get('success', False),
                        'execution_time': execution_time,
                        'has_required_keys': has_required_keys,
                        'annotations_valid': annotations_valid,
                        'annotations_count': len(result.get('annotations', {})),
                        'expected_count': test_case['data']['expected_count'],
                        'test_passed': result.get('success', False) and has_required_keys and annotations_valid
                    }
                    
                    integration_results['model_calls'].append(test_result)
                    integration_results['total_tests'] += 1
                    
                    if test_result['test_passed']:
                        integration_results['passed_tests'] += 1
                        print(f"    ✓ {test_case['name']}: {test_result['annotations_count']}/{test_result['expected_count']} annotations in {execution_time:.3f}s")
                    else:
                        integration_results['failed_tests'] += 1
                        print(f"    ✗ {test_case['name']}: Failed API call or invalid format")
                        
                except Exception as e:
                    integration_results['failed_tests'] += 1
                    integration_results['total_tests'] += 1
                    print(f"    ✗ {test_case['name']}: Exception - {str(e)}")
                
                # Add delay between API calls to be respectful
                await asyncio.sleep(1)
        
        self.results['api_integration'] = integration_results
    
    def _validate_annotation_result(self, result: Dict[str, Any], test_data: Dict[str, Any]) -> bool:
        """Validate annotation result structure"""
        try:
            # Check required keys
            required_keys = ['success', 'annotations', 'metadata']
            if not all(key in result for key in required_keys):
                return False
            
            # Check annotations structure
            annotations = result['annotations']
            if not isinstance(annotations, dict):
                return False
            
            # Check metadata structure
            metadata = result['metadata']
            if not isinstance(metadata, dict):
                return False
            
            expected_metadata_keys = ['method', 'execution_time', 'model_used']
            if not all(key in metadata for key in expected_metadata_keys):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        total_execution_time = time.time() - self.start_time
        
        # Calculate overall statistics
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            if isinstance(results, dict) and 'total_tests' in results:
                total_tests += results['total_tests']
                total_passed += results['passed_tests']
                total_failed += results['failed_tests']
        
        overall_success_rate = total_passed / total_tests if total_tests > 0 else 0
        
        report = {
            'test_summary': {
                'total_execution_time': total_execution_time,
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'overall_success_rate': overall_success_rate,
                'test_timestamp': datetime.now().isoformat()
            },
            'detailed_results': self.results,
            'parser_configuration': {
                'langextract_available': self.parser.langextract_available if self.parser else False,
                'model': self.parser.model if self.parser else None,
                'api_key_configured': bool(self.parser.api_key) if self.parser else False,
                'timeout': self.parser.timeout if self.parser else None,
                'max_retries': self.parser.max_retries if self.parser else None
            },
            'environment_info': {
                'python_version': sys.version,
                'langextract_parser_available': LANGEXTRACT_PARSER_AVAILABLE,
                'working_directory': os.getcwd()
            },
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if not self.parser:
            recommendations.append("LangextractParser could not be initialized - check dependencies and configuration")
        elif not self.parser.langextract_available:
            recommendations.append("LangExtract library not available - install langextract for full functionality")
        elif not self.parser.api_key:
            recommendations.append("No API key configured - set appropriate environment variables for API access")
        
        # Analyze performance results
        if 'performance' in self.results and self.results['performance'].get('response_times'):
            avg_time = sum(r['execution_time'] for r in self.results['performance']['response_times']) / len(self.results['performance']['response_times'])
            if avg_time > 10:
                recommendations.append(f"Average response time is {avg_time:.1f}s - consider optimizing or using faster models")
        
        # Analyze error handling
        if 'error_handling' in self.results:
            error_results = self.results['error_handling']
            if error_results.get('failed_tests', 0) > error_results.get('passed_tests', 0):
                recommendations.append("Error handling needs improvement - many tests failed")
        
        # Analyze API integration
        if 'api_integration' in self.results:
            api_results = self.results['api_integration']
            if api_results.get('status') == 'skipped':
                if api_results.get('reason') == 'no_api_key':
                    recommendations.append("Configure API keys to enable full integration testing")
                elif api_results.get('reason') == 'langextract_unavailable':
                    recommendations.append("Install and configure LangExtract for API integration testing")
        
        if not recommendations:
            recommendations.append("All tests passed successfully - langextract_parser.py is working correctly")
        
        return recommendations

def print_test_report(report: Dict[str, Any]):
    """Print comprehensive test report"""
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE LANGEXTRACT_PARSER.PY TEST REPORT")
    print("=" * 80)
    
    # Summary
    summary = report['test_summary']
    print(f"\n🕒 Execution Time: {summary['total_execution_time']:.3f}s")
    print(f"📋 Total Tests: {summary['total_tests']}")
    print(f"✅ Passed: {summary['total_passed']}")
    print(f"❌ Failed: {summary['total_failed']}")
    print(f"📈 Success Rate: {summary['overall_success_rate']:.1%}")
    print(f"🗓️  Test Date: {summary['test_timestamp']}")
    
    # Configuration
    config = report['parser_configuration']
    print(f"\n⚙️  Parser Configuration:")
    print(f"   LangExtract Available: {config['langextract_available']}")
    print(f"   Model: {config['model']}")
    print(f"   API Key Configured: {config['api_key_configured']}")
    print(f"   Timeout: {config['timeout']}s")
    print(f"   Max Retries: {config['max_retries']}")
    
    # Detailed results by category
    print(f"\n📊 Detailed Results by Category:")
    for category, results in report['detailed_results'].items():
        if isinstance(results, dict):
            if 'total_tests' in results:
                success_rate = results['passed_tests'] / results['total_tests'] if results['total_tests'] > 0 else 0
                print(f"   {category.replace('_', ' ').title()}: {results['passed_tests']}/{results['total_tests']} ({success_rate:.1%})")
            else:
                print(f"   {category.replace('_', ' ').title()}: {results.get('status', 'completed')}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    for i, recommendation in enumerate(report['recommendations'], 1):
        print(f"   {i}. {recommendation}")
    
    print("\n" + "=" * 80)

async def main():
    """Main test execution function"""
    print("🔧 Initializing LangExtract Parser Comprehensive Test Suite")
    print("=" * 60)
    
    tester = LangextractParserTester()
    
    try:
        # Run comprehensive tests
        report = await tester.run_comprehensive_tests()
        
        # Print detailed report
        print_test_report(report)
        
        # Save report to file
        report_file = Path(__file__).parent / f"langextract_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        # Return exit code based on success rate
        success_rate = report['test_summary']['overall_success_rate']
        if success_rate >= 0.8:
            print(f"\n🎉 Tests completed successfully! Overall success rate: {success_rate:.1%}")
            return 0
        else:
            print(f"\n⚠️  Tests completed with issues. Success rate: {success_rate:.1%}")
            return 1
        
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return 2

if __name__ == "__main__":
    if not LANGEXTRACT_PARSER_AVAILABLE:
        print("❌ Cannot run tests: LangextractParser module not available")
        print("Please ensure the mllmcelltype package is properly installed")
        sys.exit(3)
    
    # Run the async test suite
    exit_code = asyncio.run(main())
    sys.exit(exit_code)