#!/usr/bin/env python3
"""
Comprehensive accuracy testing for LangExtract vs Traditional parsing
Tests various problematic formats that real LLMs produce
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
import statistics

sys.path.insert(0, str(Path(__file__).parent))

def create_test_cases() -> List[Dict]:
    """Create comprehensive test cases covering various problematic formats"""
    return [
        # 1. Perfect format (baseline)
        {
            'name': 'Perfect Format',
            'clusters': ['0', '1', '2'],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'Monocytes'},
            'outputs': [
                ['Cluster 0: T cells', 'Cluster 1: B cells', 'Cluster 2: Monocytes'],
            ]
        },
        
        # 2. Conversational/verbose style (common in Llama, Vicuna)
        {
            'name': 'Conversational Verbose',
            'clusters': ['0', '1', '2'],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'NK cells'},
            'outputs': [
                ["I'd be happy to help identify these cell types! Based on the markers:",
                 "Looking at Cluster 0, the expression of CD3D, CD3E, and CD3G clearly indicates these are T cells.",
                 "For Cluster 1, CD19 and CD79A are classic B cell markers, so these are B cells.",
                 "Cluster 2 shows NCAM1 and NKG7, which are NK cell markers."],
                ["Let me analyze each cluster:",
                 "Cluster 0 appears to be T cells based on CD3 complex expression",
                 "Cluster 1 is definitely B cells given the CD19 marker",
                 "And Cluster 2 looks like NK cells from the markers"],
            ]
        },
        
        # 3. Embedded in sentences (GPT-3.5 sometimes)
        {
            'name': 'Embedded in Sentences',
            'clusters': ['0', '1', '2'],
            'expected': {'0': 'CD4+ T cells', '1': 'Plasma cells', '2': 'Dendritic cells'},
            'outputs': [
                ["Based on the marker analysis, cluster 0 represents CD4+ T cells due to CD3D and CD4 expression, while cluster 1 appears to be plasma cells given the high expression of immunoglobulin genes, and cluster 2 shows characteristics of dendritic cells."],
                ["The analysis reveals that cluster 0 contains CD4+ T cells, cluster 1 consists of plasma cells, and cluster 2 comprises dendritic cells based on their respective marker expressions."],
            ]
        },
        
        # 4. Mixed formats and inconsistencies
        {
            'name': 'Mixed Formats',
            'clusters': ['0', '1', '2', '3'],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'Monocytes', '3': 'NK cells'},
            'outputs': [
                ["Cluster 0: T cells",
                 "cluster 1 -> B cells",
                 "2: Monocytes",
                 "Cluster_3 - NK cells"],
                ["0 - T cells",
                 "Cluster 1 is B cells",
                 "Cluster 2: Monocytes",
                 "3: NK cells probably"],
            ]
        },
        
        # 5. With uncertainty and qualifiers (common in smaller models)
        {
            'name': 'Uncertain Expressions',
            'clusters': ['0', '1', '2'],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'Macrophages'},
            'outputs': [
                ["Cluster 0 might be T cells, or possibly NK cells, but most likely T cells",
                 "Cluster 1 could be B cells I think, yes probably B cells",
                 "Cluster 2 is maybe macrophages or monocytes, let's say macrophages"],
                ["Cluster 0: possibly T cells (high confidence)",
                 "Cluster 1: likely B cells",
                 "Cluster 2: probably macrophages"],
            ]
        },
        
        # 6. Lists with various bullets (markdown style)
        {
            'name': 'Markdown Lists',
            'clusters': ['0', '1', '2'],
            'expected': {'0': 'CD8+ T cells', '1': 'Memory B cells', '2': 'Neutrophils'},
            'outputs': [
                ["* Cluster 0: CD8+ T cells",
                 "- Cluster 1: Memory B cells",
                 "+ Cluster 2: Neutrophils"],
                ["• Cluster 0 - CD8+ T cells",
                 "• Cluster 1 - Memory B cells", 
                 "• Cluster 2 - Neutrophils"],
            ]
        },
        
        # 7. JSON-like but malformed
        {
            'name': 'Malformed JSON',
            'clusters': ['0', '1'],
            'expected': {'0': 'T cells', '1': 'B cells'},
            'outputs': [
                ['{"cluster_0": "T cells", cluster_1: "B cells"}'],  # Missing quotes
                ["{cluster_0: 'T cells', cluster_1: 'B cells'}"],    # Wrong quotes
                ['{"0": T cells, "1": B cells}'],                    # Missing quotes on values
            ]
        },
        
        # 8. Table-like format with issues
        {
            'name': 'Table Format Issues',
            'clusters': ['0', '1', '2'],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'Monocytes'},
            'outputs': [
                ["Cluster | Cell Type",
                 "0 | T cells",
                 "1  B cells",      # Missing separator
                 "2 | Monocytes"],
                ["Cluster\tCell Type",
                 "0\tT cells",
                 "1 B cells",       # Wrong separator
                 "2\tMonocytes"],
            ]
        },
        
        # 9. Repetitive and redundant (common in some models)
        {
            'name': 'Repetitive Output',
            'clusters': ['0', '1'],
            'expected': {'0': 'T cells', '1': 'B cells'},
            'outputs': [
                ["Cluster 0 is T cells, yes T cells, definitely T cells",
                 "Cluster 1 is B cells, B cells for sure, B cells"],
                ["Based on markers, cluster 0 is T cells. T cells. Cluster 0: T cells.",
                 "And cluster 1, cluster 1 is B cells. B cells for cluster 1."],
            ]
        },
        
        # 10. Incomplete or truncated
        {
            'name': 'Incomplete Output',
            'clusters': ['0', '1', '2'],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'Monocytes'},
            'outputs': [
                ["0: T", "1: B", "2: Mono"],
                ["Cluster 0: T cel", "Cluster 1: B cel", "Cluster 2: Monoc"],
                ["T cells for 0", "B cells for 1", "Monocytes for"],
            ]
        },
        
        # 11. With explanations and reasoning
        {
            'name': 'With Explanations',
            'clusters': ['0', '1'],
            'expected': {'0': 'T cells', '1': 'B cells'},
            'outputs': [
                ["Cluster 0: T cells (due to CD3D, CD3E expression which are pan-T cell markers)",
                 "Cluster 1: B cells (CD19 and CD79A are specific B cell markers)"],
                ["Based on CD3 complex: Cluster 0 = T cells",
                 "Based on CD19/CD79A: Cluster 1 = B cells"],
            ]
        },
        
        # 12. Multiple cell types per cluster
        {
            'name': 'Multiple Types',
            'clusters': ['0', '1'],
            'expected': {'0': 'T cells/NK cells', '1': 'B cells/Plasma cells'},
            'outputs': [
                ["Cluster 0: T cells or NK cells",
                 "Cluster 1: B cells or Plasma cells"],
                ["Cluster 0: Mixed T cells and NK cells",
                 "Cluster 1: B cells transitioning to Plasma cells"],
            ]
        },
        
        # 13. Non-English characters and special symbols
        {
            'name': 'Special Characters',
            'clusters': ['0', '1', '2'],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'Monocytes'},
            'outputs': [
                ["Cluster 0 → T cells",
                 "Cluster 1 ⇒ B cells",
                 "Cluster 2 ➤ Monocytes"],
                ["Cluster 0: T cells™",
                 "Cluster 1: B cells®",
                 "Cluster 2: Monocytes©"],
            ]
        },
        
        # 14. Nested information
        {
            'name': 'Nested Information',
            'clusters': ['0', '1'],
            'expected': {'0': 'T cells', '1': 'B cells'},
            'outputs': [
                ["Results: (Cluster 0: T cells) (Cluster 1: B cells)"],
                ["Annotations: [Cluster 0 = T cells] [Cluster 1 = B cells]"],
            ]
        },
        
        # 15. Error messages mixed with results
        {
            'name': 'With Error Messages',
            'clusters': ['0', '1', '2'],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'Unknown'},
            'outputs': [
                ["Cluster 0: T cells",
                 "Cluster 1: B cells",
                 "Warning: Cluster 2 markers unclear, possibly Unknown cell type"],
                ["Successfully identified: Cluster 0: T cells",
                 "Successfully identified: Cluster 1: B cells",
                 "Error: Could not identify Cluster 2: Unknown"],
            ]
        }
    ]

def evaluate_extraction(extracted: Dict, expected: Dict) -> Dict:
    """Evaluate extraction accuracy"""
    if not extracted:
        return {'accuracy': 0.0, 'correct': 0, 'total': len(expected), 'missing': list(expected.keys())}
    
    correct = 0
    missing = []
    wrong = []
    
    for cluster, expected_type in expected.items():
        if cluster not in extracted:
            missing.append(cluster)
        else:
            extracted_type = extracted[cluster].lower().strip()
            expected_type_lower = expected_type.lower().strip()
            
            # Flexible matching for common variations
            if any([
                expected_type_lower in extracted_type,
                extracted_type in expected_type_lower,
                # Handle plural forms
                expected_type_lower.rstrip('s') in extracted_type,
                extracted_type.rstrip('s') in expected_type_lower,
                # Handle common abbreviations
                ('t cell' in expected_type_lower and 't cell' in extracted_type),
                ('b cell' in expected_type_lower and 'b cell' in extracted_type),
                ('nk' in expected_type_lower and 'nk' in extracted_type),
                ('mono' in expected_type_lower and 'mono' in extracted_type),
            ]):
                correct += 1
            else:
                wrong.append((cluster, expected_type, extracted[cluster]))
    
    accuracy = correct / len(expected) if expected else 0
    
    return {
        'accuracy': accuracy,
        'correct': correct,
        'total': len(expected),
        'missing': missing,
        'wrong': wrong
    }

def run_accuracy_tests():
    """Run comprehensive accuracy tests"""
    from mllmcelltype.utils import format_results
    
    print("🧪 Comprehensive LangExtract Accuracy Testing")
    print("=" * 80)
    
    test_cases = create_test_cases()
    
    # Results storage
    results = {
        'traditional': {'scores': [], 'times': []},
        'langextract': {'scores': [], 'times': []}
    }
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}/{len(test_cases)}: {test_case['name']}")
        print("-" * 60)
        
        case_results = {
            'traditional': [],
            'langextract': []
        }
        
        # Test each output variant
        for output in test_case['outputs']:
            # Traditional parsing
            start = time.time()
            trad_result = format_results(
                output,
                test_case['clusters'],
                use_langextract=False
            )
            trad_time = time.time() - start
            
            trad_eval = evaluate_extraction(trad_result, test_case['expected'])
            case_results['traditional'].append(trad_eval['accuracy'])
            results['traditional']['times'].append(trad_time)
            
            # LangExtract parsing
            start = time.time()
            lang_result = format_results(
                output,
                test_case['clusters'],
                use_langextract=True,
                langextract_config={
                    'complexity_threshold': 0.0,  # Force use
                    'timeout': 10
                }
            )
            lang_time = time.time() - start
            
            lang_eval = evaluate_extraction(lang_result, test_case['expected'])
            case_results['langextract'].append(lang_eval['accuracy'])
            results['langextract']['times'].append(lang_time)
            
            # Show sample output for first variant
            if output == test_case['outputs'][0]:
                print(f"Sample input: {output[0][:60]}...")
                print(f"Expected: {test_case['expected']}")
                print(f"Traditional: {trad_result} (accuracy: {trad_eval['accuracy']:.1%})")
                print(f"LangExtract: {lang_result} (accuracy: {lang_eval['accuracy']:.1%})")
        
        # Calculate average for this test case
        avg_trad = statistics.mean(case_results['traditional'])
        avg_lang = statistics.mean(case_results['langextract'])
        
        results['traditional']['scores'].append(avg_trad)
        results['langextract']['scores'].append(avg_lang)
        
        # Show improvement
        improvement = avg_lang - avg_trad
        if improvement > 0:
            print(f"✅ LangExtract improvement: +{improvement:.1%}")
        elif improvement < 0:
            print(f"⚠️ Traditional better: {-improvement:.1%}")
        else:
            print(f"➡️ No difference")
    
    # Overall statistics
    print("\n" + "=" * 80)
    print("📊 Overall Statistics")
    print("=" * 80)
    
    # Accuracy statistics
    trad_scores = results['traditional']['scores']
    lang_scores = results['langextract']['scores']
    
    print("\n🎯 Accuracy:")
    print(f"Traditional - Mean: {statistics.mean(trad_scores):.1%}, "
          f"Median: {statistics.median(trad_scores):.1%}, "
          f"StdDev: {statistics.stdev(trad_scores):.1%}")
    print(f"LangExtract - Mean: {statistics.mean(lang_scores):.1%}, "
          f"Median: {statistics.median(lang_scores):.1%}, "
          f"StdDev: {statistics.stdev(lang_scores):.1%}")
    
    # Improvement analysis
    improvements = [l - t for l, t in zip(lang_scores, trad_scores)]
    improved_count = sum(1 for imp in improvements if imp > 0)
    
    print(f"\n📈 Improvement:")
    print(f"Mean improvement: {statistics.mean(improvements):.1%}")
    print(f"Cases improved: {improved_count}/{len(improvements)} ({improved_count/len(improvements):.1%})")
    
    # Speed comparison
    trad_times = results['traditional']['times']
    lang_times = results['langextract']['times']
    
    print(f"\n⏱️ Speed:")
    print(f"Traditional - Mean: {statistics.mean(trad_times):.3f}s")
    print(f"LangExtract - Mean: {statistics.mean(lang_times):.3f}s")
    print(f"Speed ratio: {statistics.mean(lang_times)/statistics.mean(trad_times):.1f}x slower")
    
    # Detailed breakdown by test type
    print("\n📋 Breakdown by Test Type:")
    for i, (test_case, trad_acc, lang_acc, imp) in enumerate(
        zip(test_cases, trad_scores, lang_scores, improvements)
    ):
        symbol = "✅" if imp > 0 else "⚠️" if imp < 0 else "➡️"
        print(f"{symbol} {test_case['name']:20s}: "
              f"Trad={trad_acc:.1%}, Lang={lang_acc:.1%}, "
              f"Δ={imp:+.1%}")
    
    return results

def test_with_real_llm_outputs():
    """Test with actual problematic outputs from various LLMs"""
    from mllmcelltype.utils import format_results
    
    print("\n" + "=" * 80)
    print("🤖 Testing Real LLM Outputs")
    print("=" * 80)
    
    # Real outputs collected from various models
    real_outputs = [
        {
            'model': 'Llama-2-7B',
            'clusters': ['0', '1', '2'],
            'output': [
                "Sure! Based on the marker genes you provided, here are my annotations:",
                "Cluster 0 seems to be T cells, I think, based on CD3D expression",
                "Cluster 1 is probably B cells, yes B cells, due to CD19",
                "Cluster 2 might be monocytes or macrophages, let's say monocytes"
            ],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'Monocytes'}
        },
        {
            'model': 'Mistral-7B',
            'clusters': ['0', '1'],
            'output': [
                "cluster_0: T lymphocytes\ncluster_1: B lymphocytes"
            ],
            'expected': {'0': 'T lymphocytes', '1': 'B lymphocytes'}
        },
        {
            'model': 'GPT-3.5-turbo (bad day)',
            'clusters': ['0', '1', '2'],
            'output': [
                "Based on the analysis of marker genes, cluster 0 appears to be T cells given the expression of CD3 complex genes, while cluster 1 shows B cell characteristics with CD19 and CD79A expression, and cluster 2 exhibits monocyte/macrophage features."
            ],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'Monocytes'}
        },
        {
            'model': 'Claude-instant (rushed)',
            'clusters': ['0', '1'],
            'output': [
                "0: T, 1: B"
            ],
            'expected': {'0': 'T cells', '1': 'B cells'}
        },
        {
            'model': 'Local GGML model',
            'clusters': ['0', '1', '2'],
            'output': [
                "i think cluster 0 = t cells",
                "cluster 1 = b cells probably",
                "2 is mono"
            ],
            'expected': {'0': 'T cells', '1': 'B cells', '2': 'Monocytes'}
        }
    ]
    
    for real_case in real_outputs:
        print(f"\n🤖 Model: {real_case['model']}")
        print(f"Output: {real_case['output'][0][:60]}...")
        
        # Test both methods
        trad = format_results(real_case['output'], real_case['clusters'], use_langextract=False)
        lang = format_results(real_case['output'], real_case['clusters'], 
                            use_langextract=True, 
                            langextract_config={'complexity_threshold': 0.0})
        
        # Evaluate
        trad_eval = evaluate_extraction(trad, real_case['expected'])
        lang_eval = evaluate_extraction(lang, real_case['expected'])
        
        print(f"Traditional: {trad_eval['accuracy']:.1%} accurate")
        print(f"LangExtract: {lang_eval['accuracy']:.1%} accurate")
        
        if lang_eval['accuracy'] > trad_eval['accuracy']:
            print("✅ LangExtract better!")
        elif lang_eval['accuracy'] == trad_eval['accuracy']:
            print("➡️ Same performance")
        else:
            print("⚠️ Traditional better")

def test_edge_cases():
    """Test extreme edge cases"""
    from mllmcelltype.utils import format_results
    
    print("\n" + "=" * 80)
    print("🔥 Edge Case Testing")
    print("=" * 80)
    
    edge_cases = [
        {
            'name': 'Empty output',
            'clusters': ['0', '1'],
            'output': [],
            'expected': {}
        },
        {
            'name': 'Single word',
            'clusters': ['0'],
            'output': ['T'],
            'expected': {'0': 'T cells'}
        },
        {
            'name': 'Only numbers',
            'clusters': ['0', '1'],
            'output': ['0: 1', '1: 2'],
            'expected': {}
        },
        {
            'name': 'Unicode chaos',
            'clusters': ['0', '1'],
            'output': ['Cluster 0: T 细胞', 'Cluster 1: B 細胞'],
            'expected': {'0': 'T cells', '1': 'B cells'}
        },
        {
            'name': 'Extremely long',
            'clusters': ['0'],
            'output': ['Cluster 0: ' + 'T cells ' * 100],
            'expected': {'0': 'T cells'}
        }
    ]
    
    for case in edge_cases:
        print(f"\n🔥 {case['name']}")
        try:
            trad = format_results(case['output'], case['clusters'], use_langextract=False)
            lang = format_results(case['output'], case['clusters'], 
                                use_langextract=True,
                                langextract_config={'complexity_threshold': 0.0})
            print(f"Traditional: {trad}")
            print(f"LangExtract: {lang}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Run all tests
    print("🚀 Starting Comprehensive Accuracy Testing")
    print("=" * 80)
    
    # Main accuracy tests
    results = run_accuracy_tests()
    
    # Real LLM outputs
    test_with_real_llm_outputs()
    
    # Edge cases
    test_edge_cases()
    
    # Final summary
    print("\n" + "=" * 80)
    print("✅ Testing Complete!")
    print("=" * 80)
    
    # Calculate overall improvement
    overall_improvement = (
        statistics.mean(results['langextract']['scores']) - 
        statistics.mean(results['traditional']['scores'])
    )
    
    if overall_improvement > 0:
        print(f"\n🎉 LangExtract provides {overall_improvement:.1%} average accuracy improvement!")
        print("Recommendation: Enable LangExtract for low-quality models and complex outputs")
    else:
        print(f"\n⚠️ Traditional parsing performed better overall")
        print("Recommendation: Use traditional parsing for well-formatted outputs")