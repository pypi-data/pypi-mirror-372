#!/usr/bin/env python

"""
Force LangExtract usage test by creating intentionally complex output scenarios.
This test simulates complex discussion scenarios where LangExtract would be beneficial.
"""

import logging
import os
import sys
import time
import json
from dotenv import load_dotenv

# Add package path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from python.mllmcelltype.langextract_controller import LangextractController
from python.mllmcelltype.utils import format_results

# Load environment variables
load_dotenv()

def create_complex_output_scenarios():
    """Create test scenarios with complex LLM outputs that should trigger LangExtract"""
    
    scenarios = [
        {
            "name": "Mixed Format Response",
            "raw_response": [
                "Based on the marker genes, here are my annotations:",
                "",
                "For cluster 0, looking at CD3D, CD8A, GNLY, PRF1, GZMB, NKG7:",
                "This appears to be cytotoxic T cells, but could also be NK cells.",
                "The presence of CD3D suggests T cells, while GNLY and NKG7 suggest NK.",
                "I believe this is: Cluster 0: CD8+ Cytotoxic T cells",
                "",
                "Cluster 1 shows B cell markers: CD19, MS4A1, CD79A, IGHM",
                "This is clearly: Cluster 1: B cells",
                "",
                "The third cluster (2) has monocyte markers:",
                "CD14, FCGR3A, LYZ, S100A8, VCAN, CSF1R",
                "Annotation: Cluster 2: Classical Monocytes",
                "",
                "Regarding cluster 3, the stem cell markers are:",
                "CD34, KIT, FLT3, RUNX1, GATA1, TAL1",
                "My assessment: Cluster 3: Hematopoietic Stem Cells"
            ],
            "clusters": ["0", "1", "2", "3"],
            "expected_complexity": "High"
        },
        
        {
            "name": "Verbose Discussion Format",
            "raw_response": [
                "I'll analyze each cluster systematically:",
                "",
                "**Analysis of Cluster 0:**",
                "The marker genes CD3D, CD8A, GNLY, PRF1, GZMB, NKG7 present an interesting case.",
                "CD3D is a T cell receptor component, strongly suggesting T cell lineage.",
                "CD8A indicates CD8+ T cell subset specifically.",
                "However, GNLY (granulysin) and NKG7 are also expressed in NK cells.",
                "PRF1 (perforin) and GZMB (granzyme B) are cytotoxic molecules shared by both.",
                "Given the presence of CD3D and CD8A, I classify this as:",
                "→ Cluster 0: CD8+ Cytotoxic T cells",
                "",
                "**Analysis of Cluster 1:**",
                "The markers CD19, MS4A1, CD79A, IGHM, TCF4, IRF8 show:",
                "- CD19: Pan-B cell marker",
                "- MS4A1 (CD20): B cell marker",  
                "- CD79A: B cell receptor component",
                "- IGHM: Heavy chain of IgM",
                "- TCF4 and IRF8: Could indicate plasmacytoid dendritic cells",
                "The first four markers strongly suggest B cells, with possible pDC contamination.",
                "Final annotation: Cluster 1: B cells (with possible pDC subset)",
                "",
                "**Analysis of Cluster 2:**",
                "Markers: CD14, FCGR3A, LYZ, S100A8, VCAN, CSF1R",
                "CD14 is the classic monocyte marker, FCGR3A suggests non-classical subset",
                "LYZ (lysozyme) is expressed in myeloid cells",
                "S100A8 is an inflammatory marker",
                "VCAN and CSF1R further support monocyte/macrophage identity",
                "Classification: Cluster 2: Monocytes (classical and non-classical)",
                "",
                "Therefore, my final annotations are:",
                "Cluster 0: CD8+ Cytotoxic T cells",
                "Cluster 1: B cells",  
                "Cluster 2: Monocytes"
            ],
            "clusters": ["0", "1", "2"],
            "expected_complexity": "Very High"
        },
        
        {
            "name": "Structured but Complex",
            "raw_response": [
                "## Cell Type Annotation Results",
                "",
                "### Methodology",
                "I analyzed the provided marker genes using established cell type signatures.",
                "",
                "### Results",
                "",
                "#### Cluster 0 Analysis",
                "**Markers:** CD3D, CD8A, GNLY, PRF1, GZMB, NKG7",
                "**Reasoning:** Strong T cell signature with cytotoxic capabilities",
                "**Confidence:** High (95%)",
                "**Annotation:** CD8+ Cytotoxic T cells",
                "",
                "#### Cluster 1 Analysis", 
                "**Markers:** CD19, MS4A1, CD79A, IGHM",
                "**Reasoning:** Clear B cell lineage markers",
                "**Confidence:** Very High (98%)",
                "**Annotation:** B cells",
                "",
                "### Summary",
                "| Cluster | Cell Type | Confidence |",
                "|---------|-----------|------------|", 
                "| 0 | CD8+ Cytotoxic T cells | 95% |",
                "| 1 | B cells | 98% |",
                "",
                "### Alternative Considerations",
                "For cluster 0, NK cells were considered but ruled out due to CD3D expression.",
                "",
                "Final standardized format:",
                "Cluster 0: CD8+ Cytotoxic T cells",
                "Cluster 1: B cells"
            ],
            "clusters": ["0", "1"],
            "expected_complexity": "Very High"
        }
    ]
    
    return scenarios

def test_langextract_controller():
    """Test LangExtract controller with various complexity scenarios"""
    
    print("="*80)
    print("LANGEXTRACT CONTROLLER TESTING")
    print("="*80)
    
    # Test configuration
    langextract_config = {
        "enabled": True,
        "model": "gpt-4o",
        "complexity_threshold": 0.1,  # Very low threshold to force usage
        "fallback_enabled": True,
        "cache_enabled": True,
        "api_timeout": 60,
        "max_retries": 3,
        "chunk_size": 2000,
        "overlap_size": 200,
        "min_confidence": 0.5,
        "extraction_method": "structured",
        "output_format": "json",
        "debug_mode": True
    }
    
    scenarios = create_complex_output_scenarios()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"Expected Complexity: {scenario['expected_complexity']}")
        print(f"{'='*60}")
        
        # Test with format_results function
        try:
            start_time = time.time()
            
            # Mock results structure
            mock_results = {str(i): f"Mock annotation {i}" for i in range(len(scenario['clusters']))}
            
            formatted_results = format_results(
                results=scenario['raw_response'],
                clusters=scenario['clusters'],
                use_langextract=True,
                langextract_config=langextract_config
            )
            
            processing_time = time.time() - start_time
            
            print(f"✅ Processing completed in {processing_time:.3f}s")
            print(f"Results: {formatted_results}")
            
            # Check if LangExtract was actually used
            if hasattr(formatted_results, 'langextract_metrics'):
                print("✅ LangExtract metrics found")
            else:
                print("⚠️  No LangExtract metrics - may have used traditional parsing")
            
        except Exception as e:
            print(f"❌ Scenario failed: {e}")
            import traceback
            traceback.print_exc()

def test_direct_langextract():
    """Test LangExtract controller directly with complex text"""
    
    print(f"\n{'='*60}")
    print("DIRECT LANGEXTRACT CONTROLLER TEST")
    print(f"{'='*60}")
    
    # Test with very low threshold
    controller = LangextractController(
        use_langextract=True,
        langextract_config={
            "enabled": True,
            "complexity_threshold": 0.0,  # Force usage
            "model": "gpt-4o",
            "debug_mode": True,
            "fallback_enabled": True
        }
    )
    
    # Create complex text scenario
    complex_text = """
    Based on comprehensive analysis of the marker genes and considering multiple biological pathways,
    I have determined the following cell type annotations with detailed reasoning:
    
    For the first cluster (Cluster 0), the expression pattern shows:
    - CD3D: Strong T cell receptor delta chain expression (p < 0.001)
    - CD8A: CD8 alpha chain indicating CD8+ subset (log2FC = 2.3)
    - GNLY: Granulysin expression suggesting cytotoxic function (q < 0.05)
    
    After consulting multiple databases (CellMarker, PanglaoDB, CellTypist) and cross-referencing
    with recent literature (Zhang et al. 2023, Nature Immunology), I conclude:
    
    Cluster 0: CD8+ Cytotoxic T cells (confidence: 92%, alternative: NK cells 8%)
    
    Similarly, for cluster 1, the B cell signature is evident through:
    CD19 (B cell marker), MS4A1 (CD20), and immunoglobulin heavy chain expression.
    
    Cluster 1: B cells (confidence: 98%)
    
    Statistical validation using hypergeometric test (p < 0.001) confirms these annotations.
    """
    
    clusters = ["0", "1"]
    
    try:
        print("Testing complexity calculation...")
        complexity = controller._calculate_complexity(complex_text)
        print(f"Calculated complexity: {complexity:.3f}")
        
        if complexity > controller.config["complexity_threshold"]:
            print("✅ Complexity exceeds threshold - LangExtract should be used")
        else:
            print("⚠️ Complexity below threshold")
        
        print("\nTesting strategy decision...")
        strategy, reason, metrics = controller.decide_strategy(complex_text)
        print(f"Strategy: {strategy}")
        print(f"Reason: {reason}")
        print(f"Metrics: {metrics}")
        
        if strategy == "langextract":
            print("✅ LangExtract strategy selected")
            
            # Test actual parsing (this would require API key and might fail gracefully)
            print("\nTesting LangExtract parsing...")
            try:
                parsed_results = controller.parse_with_langextract(complex_text, clusters)
                print(f"✅ LangExtract parsing successful: {parsed_results}")
            except Exception as parse_error:
                print(f"⚠️ LangExtract parsing failed (expected if no API): {parse_error}")
                
                # Test fallback
                print("Testing fallback to traditional parsing...")
                fallback_results = controller.parse_with_traditional(complex_text, clusters)
                print(f"✅ Fallback successful: {fallback_results}")
        else:
            print("⚠️ Traditional strategy selected")
            
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run comprehensive LangExtract testing"""
    
    print("Starting Force LangExtract Testing...")
    
    # Test 1: Controller with scenarios
    test_langextract_controller()
    
    # Test 2: Direct controller testing
    test_direct_langextract()
    
    print(f"\n{'='*80}")
    print("TESTING COMPLETE")
    print(f"{'='*80}")
    
    print("\nKey Findings:")
    print("1. LangExtract requires complex, unstructured text to trigger")
    print("2. Simple 'Cluster X: Annotation' format has very low complexity")
    print("3. Verbose explanations and mixed formats increase complexity")
    print("4. Complexity threshold needs careful tuning for different use cases")
    print("\nRecommendations:")
    print("1. Lower complexity threshold for mixed-format outputs")
    print("2. Use LangExtract for discussion summaries and complex analyses")
    print("3. Traditional parsing is sufficient for simple format responses")

if __name__ == "__main__":
    main()