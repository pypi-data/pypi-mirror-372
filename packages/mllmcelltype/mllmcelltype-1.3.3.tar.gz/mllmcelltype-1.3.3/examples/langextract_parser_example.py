#!/usr/bin/env python3
"""
LangExtract Parser Usage Examples

This script demonstrates how to use the LangextractParser module for various
cell type annotation tasks including basic parsing, batch processing, 
consensus analysis, and discussion text analysis.
"""

import asyncio
import os
import time
from typing import List

# Import mLLMCelltype with langextract support
try:
    from mllmcelltype import (
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
    print("✅ LangExtract parser module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LangExtract parser: {e}")
    print("Please install required dependencies: pip install langextract>=1.0.8 pydantic>=1.8.0")
    exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def example_1_basic_cell_type_parsing():
    """Example 1: Basic cell type annotation parsing"""
    print("\n" + "="*60)
    print("📋 Example 1: Basic Cell Type Annotation Parsing")
    print("="*60)
    
    # Test cases with different complexity levels
    test_cases = [
        {
            "name": "Simple Format",
            "text": "Cluster 0: T cells\nCluster 1: B cells\nCluster 2: NK cells",
            "expected": 3
        },
        {
            "name": "JSON Format", 
            "text": '''```json
{
  "annotations": [
    {"cluster": "0", "cell_type": "CD4+ T cells", "confidence": "high"},
    {"cluster": "1", "cell_type": "B cells", "confidence": "medium"},
    {"cluster": "2", "cell_type": "Monocytes", "confidence": "high"}
  ]
}```''',
            "expected": 3
        },
        {
            "name": "Natural Language",
            "text": "Based on CD3 expression, the first cluster represents T cells. The second cluster shows CD19+ markers indicating B cells. The third population exhibits CD14+ suggesting monocytes.",
            "expected": 3
        }
    ]
    
    # Create parser with custom configuration
    config = ParsingConfig(
        model_id="gemini-2.0-flash-thinking-exp",
        max_retries=2,
        retry_delay=1.0,
        use_caching=True
    )
    parser = LangextractParser(config)
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        # Show sample text
        sample = test_case['text'][:100] + "..." if len(test_case['text']) > 100 else test_case['text']
        print(f"Input: {sample}")
        
        try:
            start_time = time.time()
            annotations = parser.parse_cell_type_annotations(test_case['text'])
            parse_time = time.time() - start_time
            
            print(f"✅ Success - Found {len(annotations)} annotations in {parse_time:.2f}s")
            
            for j, annotation in enumerate(annotations):
                print(f"  {j+1}. Cluster {annotation.cluster}: {annotation.cell_type}")
                if annotation.confidence:
                    print(f"     Confidence: {annotation.confidence}")
            
            results.append({
                "name": test_case['name'],
                "success": True,
                "found": len(annotations),
                "expected": test_case['expected'],
                "time": parse_time
            })
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            results.append({
                "name": test_case['name'],
                "success": False,
                "found": 0,
                "expected": test_case['expected'],
                "time": 0
            })
    
    # Print summary
    print(f"\n📊 Summary:")
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    avg_time = sum(r['time'] for r in results if r['success']) / max(successful, 1)
    
    print(f"Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"Average Time: {avg_time:.2f}s")
    
    return results

def example_2_batch_processing():
    """Example 2: Batch processing multiple texts"""
    print("\n" + "="*60)
    print("📦 Example 2: Batch Processing")
    print("="*60)
    
    # Multiple texts to process
    texts = [
        "Cluster 0: T cells\nCluster 1: B cells",
        "The first group appears to be monocytes based on CD14 expression.",
        '{"cluster": 2, "type": "NK cells", "markers": ["CD56", "CD16"]}',
        "Cluster 3: Dendritic cells\nCluster 4: Neutrophils",
        "Based on the analysis, cluster 5 represents regulatory T cells."
    ]
    
    print(f"Processing {len(texts)} texts in batch...")
    
    # Create parser
    parser = create_parser()
    
    try:
        start_time = time.time()
        result = parser.parse_batch_annotations(texts)
        total_time = time.time() - start_time
        
        print(f"✅ Batch processing completed in {total_time:.2f}s")
        print(f"Total Clusters: {result.total_clusters}")
        print(f"Successful: {result.successful_annotations}")
        print(f"Failed: {result.failed_annotations}")
        print(f"Success Rate: {result.success_rate:.1%}")
        print(f"Processing Time: {result.processing_time:.2f}s")
        
        print("\nFound Annotations:")
        for i, annotation in enumerate(result.annotations[:10], 1):  # Show first 10
            print(f"  {i}. Cluster {annotation.cluster}: {annotation.cell_type}")
        
        if len(result.annotations) > 10:
            print(f"  ... and {len(result.annotations) - 10} more")
            
        return result
        
    except Exception as e:
        print(f"❌ Batch processing failed: {str(e)}")
        return None

def example_3_consensus_analysis():
    """Example 3: Consensus metrics analysis"""
    print("\n" + "="*60)
    print("🤝 Example 3: Consensus Analysis")
    print("="*60)
    
    # Text containing consensus information
    consensus_text = """
    Consensus Analysis Results:
    - 85% of models agreed on T cells for cluster 0
    - Entropy value: 0.42 (low uncertainty)
    - High confidence prediction
    - Minority opinion: 15% suggested NK cells
    - Overall consensus reached with strong agreement
    """
    
    print("Analyzing consensus metrics from text...")
    print(f"Input: {consensus_text[:100]}...")
    
    try:
        # Use convenience function
        metrics = analyze_consensus(consensus_text)
        
        print("✅ Consensus analysis completed")
        print(f"Consensus Reached: {metrics.consensus_reached}")
        print(f"Agreement Proportion: {metrics.consensus_proportion:.2%}")
        print(f"Entropy: {metrics.entropy:.3f}")
        print(f"Majority Cell Type: {metrics.majority_cell_type}")
        
        if metrics.minority_opinions:
            print(f"Minority Opinions: {', '.join(metrics.minority_opinions)}")
            
        if metrics.confidence_score:
            print(f"Confidence Score: {metrics.confidence_score:.2f}")
            
        return metrics
        
    except Exception as e:
        print(f"❌ Consensus analysis failed: {str(e)}")
        return None

def example_4_discussion_analysis():
    """Example 4: Discussion text analysis"""
    print("\n" + "="*60)
    print("💬 Example 4: Discussion Text Analysis")
    print("="*60)
    
    discussion_text = """
    The cluster analysis reveals interesting patterns. Based on CD3+ expression, 
    the first cluster clearly represents T cells with high confidence. However, 
    there's some debate about the second cluster - while CD19+ markers suggest 
    B cells, the expression levels are moderate. The team agrees that the third 
    cluster shows strong CD14+ expression indicating monocytes. Some researchers 
    argue that cluster 4 might be dendritic cells, but others think it could be 
    activated monocytes. We need more markers to confirm this hypothesis.
    """
    
    print("Analyzing discussion text for key insights...")
    print(f"Input: {discussion_text[:150]}...")
    
    config = ParsingConfig(model_id="gemini-2.0-flash-thinking-exp")
    parser = LangextractParser(config)
    
    try:
        analysis = parser.parse_discussion_text(discussion_text)
        
        print("✅ Discussion analysis completed")
        print(f"Summary: {analysis.summary}")
        
        if analysis.key_points:
            print(f"\n🔍 Key Points ({len(analysis.key_points)}):")
            for i, point in enumerate(analysis.key_points[:5], 1):
                print(f"  {i}. {point}")
        
        if analysis.suggested_cell_types:
            print(f"\n🧬 Suggested Cell Types:")
            for cell_type in analysis.suggested_cell_types:
                print(f"  - {cell_type}")
        
        if analysis.controversies:
            print(f"\n⚡ Controversies:")
            for controversy in analysis.controversies:
                print(f"  - {controversy}")
                
        if analysis.agreements:
            print(f"\n✅ Agreements:")
            for agreement in analysis.agreements:
                print(f"  - {agreement}")
                
        return analysis
        
    except Exception as e:
        print(f"❌ Discussion analysis failed: {str(e)}")
        return None

async def example_5_async_processing():
    """Example 5: Asynchronous processing"""
    print("\n" + "="*60)
    print("⚡ Example 5: Asynchronous Processing")
    print("="*60)
    
    texts = [
        "Cluster 0: T cells with high CD3 expression",
        "Cluster 1: B cells showing CD19+ markers",
        "Cluster 2: Monocytes with CD14+ phenotype",
        "Cluster 3: NK cells expressing CD56 and CD16"
    ]
    
    print(f"Processing {len(texts)} texts asynchronously...")
    
    parser = create_parser()
    
    try:
        start_time = time.time()
        result = await parser.parse_batch_annotations_async(texts)
        total_time = time.time() - start_time
        
        print(f"✅ Async processing completed in {total_time:.2f}s")
        print(f"Found {result.successful_annotations} annotations")
        print(f"Success Rate: {result.success_rate:.1%}")
        
        for annotation in result.annotations:
            print(f"  Cluster {annotation.cluster}: {annotation.cell_type}")
            
        return result
        
    except Exception as e:
        print(f"❌ Async processing failed: {str(e)}")
        return None

def example_6_performance_monitoring():
    """Example 6: Performance monitoring and stats"""
    print("\n" + "="*60)
    print("📈 Example 6: Performance Monitoring")
    print("="*60)
    
    # Create parser and run some operations
    parser = create_parser()
    
    test_texts = [
        "Cluster 0: T cells",
        "Cluster 1: B cells", 
        "Cluster 2: NK cells"
    ]
    
    print("Running operations to collect performance data...")
    
    # Run multiple operations
    for text in test_texts:
        try:
            parser.parse_cell_type_annotations(text)
        except:
            pass
    
    # Get performance stats
    stats = parser.get_performance_stats()
    
    print("📊 Performance Statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    return stats

def main():
    """Main function to run all examples"""
    print("🚀 LangExtract Parser Examples")
    print("=" * 60)
    
    # Check if LangExtract is available
    if not LANGEXTRACT_AVAILABLE:
        print("❌ LangExtract is not available. Please install required dependencies.")
        return
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  Warning: No Google/Gemini API key found.")
        print("Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        print("Some examples may fail without proper API credentials.")
    else:
        print("✅ API key configured")
    
    try:
        # Run examples
        print("\n🎯 Running Examples...")
        
        # 1. Basic parsing
        example_1_basic_cell_type_parsing()
        
        # 2. Batch processing
        example_2_batch_processing()
        
        # 3. Consensus analysis
        example_3_consensus_analysis()
        
        # 4. Discussion analysis
        example_4_discussion_analysis()
        
        # 5. Async processing
        print("\n⚡ Running async example...")
        asyncio.run(example_5_async_processing())
        
        # 6. Performance monitoring
        example_6_performance_monitoring()
        
        print(f"\n🎉 All examples completed successfully!")
        print("The LangextractParser provides powerful text extraction capabilities")
        print("for cell type annotation tasks with robust error handling and optimization.")
        
    except Exception as e:
        print(f"\n❌ Example execution failed: {str(e)}")
        print("This might be due to missing API keys or network issues.")

if __name__ == "__main__":
    main()