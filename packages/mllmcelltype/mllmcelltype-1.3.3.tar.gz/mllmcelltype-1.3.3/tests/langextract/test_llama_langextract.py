#!/usr/bin/env python3
"""
测试LangExtract处理Llama等低质量模型输出的能力
这些模型经常产生不规范、混乱的格式
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, List

# Add the mllmcelltype package to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# 设置OpenRouter API key用于Llama
os.environ['OPENROUTER_API_KEY'] = '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'

def test_llama_models():
    """测试不同的Llama模型变体"""
    from mllmcelltype.annotate import annotate_clusters
    
    print("🦙 测试Llama模型的不规范输出处理")
    print("="*80)
    
    # 测试数据
    test_markers = {
        "Cluster_0": ["CD3D", "CD3E", "CD3G", "CD4"],
        "Cluster_1": ["CD19", "CD79A", "MS4A1"],
        "Cluster_2": ["CD14", "LYZ", "CD68"]
    }
    
    # Llama模型列表（通过OpenRouter）
    llama_models = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "meta-llama/llama-3-8b-instruct:free",
    ]
    
    results_comparison = []
    
    for model in llama_models:
        print(f"\n📝 测试模型: {model}")
        print("-"*60)
        
        try:
            # 1. 测试Traditional解析
            print("\n1️⃣ Traditional解析:")
            start = time.time()
            trad_result = annotate_clusters(
                marker_genes=test_markers,
                species="human",
                model=model,
                provider="openrouter",
                api_key=os.environ['OPENROUTER_API_KEY'],
                use_langextract=False
            )
            trad_time = time.time() - start
            
            print(f"  时间: {trad_time:.2f}秒")
            print(f"  结果:")
            for cluster, cell_type in trad_result.items():
                print(f"    {cluster}: {cell_type[:50]}..." if len(cell_type) > 50 else f"    {cluster}: {cell_type}")
            
            # 评估Traditional结果质量
            trad_quality = evaluate_result_quality(trad_result)
            print(f"  质量评分: {trad_quality}/3")
            
            # 2. 测试LangExtract解析
            print("\n2️⃣ LangExtract解析:")
            start = time.time()
            lang_result = annotate_clusters(
                marker_genes=test_markers,
                species="human",
                model=model,
                provider="openrouter",
                api_key=os.environ['OPENROUTER_API_KEY'],
                use_langextract=True,
                langextract_config={
                    'complexity_threshold': 0.1,  # 低阈值，更容易触发
                    'model': 'gemini-2.5-flash'  # 用Gemini来解析Llama的输出
                }
            )
            lang_time = time.time() - start
            
            print(f"  时间: {lang_time:.2f}秒")
            print(f"  结果:")
            for cluster, cell_type in lang_result.items():
                print(f"    {cluster}: {cell_type[:50]}..." if len(cell_type) > 50 else f"    {cluster}: {cell_type}")
            
            # 评估LangExtract结果质量
            lang_quality = evaluate_result_quality(lang_result)
            print(f"  质量评分: {lang_quality}/3")
            
            # 3. 比较结果
            print("\n3️⃣ 结果比较:")
            improvement = lang_quality - trad_quality
            if improvement > 0:
                print(f"  ✨ LangExtract提升了{improvement}分！")
            elif improvement == 0:
                print(f"  ➡️ 两种方法效果相同")
            else:
                print(f"  ⚠️ Traditional表现更好")
            
            # 记录结果
            results_comparison.append({
                'model': model,
                'trad_quality': trad_quality,
                'lang_quality': lang_quality,
                'improvement': improvement
            })
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            results_comparison.append({
                'model': model,
                'trad_quality': 0,
                'lang_quality': 0,
                'improvement': 0
            })
    
    return results_comparison

def test_llama_edge_cases():
    """测试Llama常见的问题输出格式"""
    from mllmcelltype.utils import format_results
    
    print("\n" + "="*80)
    print("🔍 测试Llama常见的问题输出")
    print("="*80)
    
    # Llama经常产生的问题格式
    edge_cases = [
        {
            'name': '冗长解释',
            'clusters': ['0', '1', '2'],
            'output': [
                "Let me analyze the marker genes for each cluster:",
                "Looking at Cluster 0, I can see CD3D, CD3E, CD3G, and CD4 are expressed. These are classic markers for T cells, specifically CD4+ T helper cells.",
                "For Cluster 1, the presence of CD19, CD79A, and MS4A1 clearly indicates these are B cells.",
                "Cluster 2 shows CD14, LYZ, and CD68 expression, which are typical markers for monocytes or macrophages.",
                "In summary, Cluster 0 appears to be CD4+ T cells, Cluster 1 is B cells, and Cluster 2 is monocytes/macrophages."
            ]
        },
        {
            'name': '重复和啰嗦',
            'clusters': ['0', '1'],
            'output': [
                "Based on the markers, based on what I can see, Cluster 0 is, I believe, T cells, yes T cells.",
                "And then Cluster 1, looking at the markers, the markers suggest, they suggest B cells, definitely B cells."
            ]
        },
        {
            'name': '不完整句子',
            'clusters': ['0', '1', '2'],
            'output': [
                "Cluster 0... T cells",
                "Cluster 1 -> B cells probably",
                "2: mono"
            ]
        },
        {
            'name': '混合格式和错误',
            'clusters': ['0', '1', '2'],
            'output': [
                "Here are the annotations:\n\nCluster 0: T cells\nCluster 1 B cells (missing colon)\nCluster 2:monocytes",
                "Note: These are my best guesses based on the markers provided."
            ]
        },
        {
            'name': '嵌入式答案',
            'clusters': ['0', '1'],
            'output': [
                "I think that given the expression of CD3D and other T cell markers, cluster 0 most likely represents T cells, while cluster 1 with CD19 expression is probably B cells."
            ]
        },
        {
            'name': '列表但格式混乱',
            'clusters': ['0', '1', '2'],
            'output': [
                "* cluster 0 - T cells",
                "- Cluster 1: B cells", 
                "cluster 2 -- monocytes"
            ]
        }
    ]
    
    print("\n测试各种问题格式：")
    
    for case in edge_cases:
        print(f"\n📋 {case['name']}:")
        print(f"输入示例: {case['output'][0][:60]}...")
        
        # Traditional解析
        trad_result = format_results(
            case['output'],
            case['clusters'],
            use_langextract=False
        )
        
        # LangExtract解析
        lang_result = format_results(
            case['output'],
            case['clusters'],
            use_langextract=True,
            langextract_config={'complexity_threshold': 0.0}  # 强制使用
        )
        
        print(f"Traditional: {trad_result}")
        print(f"LangExtract: {lang_result}")
        
        # 评估
        trad_valid = sum(1 for k, v in trad_result.items() if v and 'cell' in v.lower())
        lang_valid = sum(1 for k, v in lang_result.items() if v and 'cell' in v.lower())
        
        if lang_valid > trad_valid:
            print("✨ LangExtract更好！")
        elif lang_valid == trad_valid:
            print("➡️ 效果相同")
        else:
            print("⚠️ Traditional更好")

def evaluate_result_quality(result: Dict[str, str]) -> int:
    """评估结果质量（0-3分）"""
    score = 0
    
    for cluster_id, cell_type in result.items():
        if cell_type and isinstance(cell_type, str):
            # 检查是否包含细胞类型关键词
            cell_keywords = ['cell', 'lymphocyte', 'monocyte', 'macrophage', 'neutrophil', 'nk', 'plasma']
            if any(keyword in cell_type.lower() for keyword in cell_keywords):
                score += 1
            # 惩罚过长的输出（可能是未解析的原始文本）
            if len(cell_type) > 100:
                score -= 0.5
    
    return max(0, min(3, score))

def simulate_llama_outputs():
    """模拟Llama的各种问题输出并测试"""
    from mllmcelltype.utils import format_results
    
    print("\n" + "="*80)
    print("🎭 模拟Llama典型输出并测试")
    print("="*80)
    
    # 模拟Llama的典型输出模式
    simulated_outputs = [
        {
            'name': 'Llama风格1: 对话式',
            'output': [
                "Sure! I'd be happy to help you identify these cell types.",
                "Looking at the markers you provided:",
                "Cluster 0 seems to be T cells based on CD3 expression",
                "Cluster 1 is likely B cells given the CD19 marker",
                "Cluster 2 appears to be monocytes due to CD14",
                "Hope this helps with your analysis!"
            ]
        },
        {
            'name': 'Llama风格2: 不确定性',
            'output': [
                "Cluster 0 might be T cells, or possibly NK cells, but probably T cells",
                "Cluster 1 could be B cells I think",
                "Cluster 2 is maybe monocytes or macrophages, hard to say for sure"
            ]
        },
        {
            'name': 'Llama风格3: 格式错误',
            'output': [
                "cluster0:T cells\ncluster1:B cells\ncluster2:monocytes"
            ]
        }
    ]
    
    clusters = ['0', '1', '2']
    
    for sim in simulated_outputs:
        print(f"\n{sim['name']}")
        print("-"*40)
        
        # 测试两种方法
        trad = format_results(sim['output'], clusters, use_langextract=False)
        lang = format_results(sim['output'], clusters, use_langextract=True,
                             langextract_config={'complexity_threshold': 0.0})
        
        print(f"Traditional结果: {trad}")
        print(f"LangExtract结果: {lang}")
        
        # 简单评估
        trad_ok = all(c in trad and trad[c] for c in clusters)
        lang_ok = all(c in lang and lang[c] for c in clusters)
        
        if lang_ok and not trad_ok:
            print("✅ LangExtract成功处理了Traditional无法处理的格式！")
        elif trad_ok and lang_ok:
            print("✅ 两种方法都成功")
        elif not trad_ok and not lang_ok:
            print("❌ 两种方法都失败")

def main():
    """主测试函数"""
    print("🚀 开始测试LangExtract处理Llama输出")
    print("="*80)
    
    # 1. 测试真实Llama模型
    print("\n第1部分: 真实Llama模型测试")
    results = test_llama_models()
    
    # 2. 测试边缘情况
    test_llama_edge_cases()
    
    # 3. 模拟测试
    simulate_llama_outputs()
    
    # 总结
    print("\n" + "="*80)
    print("📊 测试总结")
    print("="*80)
    
    if results:
        total_improvement = sum(r['improvement'] for r in results)
        avg_improvement = total_improvement / len(results) if results else 0
        
        print(f"\n测试了 {len(results)} 个Llama模型:")
        for r in results:
            print(f"  {r['model']}: Traditional={r['trad_quality']}/3, LangExtract={r['lang_quality']}/3")
        
        if avg_improvement > 0:
            print(f"\n✨ LangExtract平均提升: {avg_improvement:.1f}分")
            print("结论: LangExtract对处理Llama的低质量输出有明显帮助！")
        else:
            print(f"\n➡️ 平均改进: {avg_improvement:.1f}分")
            print("结论: 效果因模型而异")
    
    print("\n💡 建议:")
    print("• 对Llama等容易产生不规范输出的模型，建议启用LangExtract")
    print("• 设置较低的complexity_threshold (0.1-0.2)")
    print("• 使用更强的模型(如Gemini)来解析低质量输出")

if __name__ == "__main__":
    main()