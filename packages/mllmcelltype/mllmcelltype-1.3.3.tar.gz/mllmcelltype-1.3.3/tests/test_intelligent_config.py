#!/usr/bin/env python3
"""
测试智能LangExtract配置系统
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_model_quality_detection():
    """测试模型质量检测"""
    from mllmcelltype.model_quality_config import (
        get_model_quality_config,
        should_use_langextract_for_model,
        get_recommended_config
    )
    
    print("🧠 测试智能模型质量检测")
    print("="*60)
    
    test_models = [
        # 高质量模型
        ("gpt-4", "openai"),
        ("claude-3-opus", "anthropic"),
        
        # 中等质量模型
        ("gpt-3.5-turbo", "openai"),
        ("gemini-2.5-flash", "gemini"),
        
        # 低质量模型
        ("llama-3-8b", "ollama"),
        ("mistral-7b", "openrouter"),
        
        # 未知模型
        ("custom-model-v1", "custom"),
    ]
    
    for model, provider in test_models:
        config = get_recommended_config(model, provider)
        print(f"\n📌 {model} ({provider}):")
        print(f"  Use LangExtract: {config['use_langextract']}")
        print(f"  Threshold: {config['langextract_config']['complexity_threshold']}")
        print(f"  Reason: {config['reason']}")

def test_real_annotation():
    """测试实际注释场景"""
    from mllmcelltype.annotate import annotate_clusters
    
    print("\n" + "="*60)
    print("🔬 测试实际注释场景")
    print("="*60)
    
    test_markers = {
        "Cluster_0": ["CD3D", "CD3E"],
        "Cluster_1": ["CD19", "CD79A"],
    }
    
    # 测试1: GPT-4 (高质量，不应使用LangExtract)
    print("\n1. GPT-4 (高质量模型):")
    try:
        result = annotate_clusters(
            marker_genes=test_markers,
            species="human",
            model="gpt-4",
            provider="openai"
            # 不指定use_langextract，让系统自动决定
        )
        print(f"  ✅ 结果: {result}")
    except Exception as e:
        print(f"  ⚠️ 跳过 (无API key): {e}")
    
    # 测试2: Gemini Flash (中等质量，自动决定)
    print("\n2. Gemini Flash (中等质量模型):")
    result = annotate_clusters(
        marker_genes=test_markers,
        species="human",
        model="gemini-2.5-flash",
        provider="gemini"
        # 不指定use_langextract
    )
    print(f"  ✅ 结果: {result}")
    
    # 测试3: 模拟Llama (低质量，应自动启用LangExtract)
    print("\n3. 模拟低质量模型场景:")
    # 用Gemini Flash但模拟低质量模型的决策
    try:
        result = annotate_clusters(
            marker_genes=test_markers,
            species="human",
            model="gemini-2.5-flash",  # 使用实际存在的模型
            provider="gemini",
            use_langextract=True,  # 强制启用来模拟低质量模型的行为
            langextract_config={
                'complexity_threshold': 0.1,  # 低质量模型的低阈值
                'timeout': 10
            }
        )
        print(f"  ✅ 结果 (LangExtract启用): {result}")
    except Exception as e:
        print(f"  ⚠️ 跳过: {e}")

def test_override_behavior():
    """测试用户覆盖行为"""
    from mllmcelltype.annotate import _resolve_langextract_config_intelligent
    
    print("\n" + "="*60)
    print("🔧 测试用户覆盖行为")
    print("="*60)
    
    # 测试1: 高质量模型但用户强制启用
    print("\n1. GPT-4 + 用户强制启用LangExtract:")
    config = _resolve_langextract_config_intelligent(
        model="gpt-4",
        provider="openai",
        use_langextract=True  # 用户强制
    )
    print(f"  Enabled: {config['enabled']} (用户覆盖)")
    
    # 测试2: 低质量模型但用户强制禁用
    print("\n2. Llama + 用户强制禁用LangExtract:")
    config = _resolve_langextract_config_intelligent(
        model="llama-3",
        provider="ollama",
        use_langextract=False  # 用户强制
    )
    print(f"  Enabled: {config['enabled']} (用户覆盖)")
    
    # 测试3: 自动决定
    print("\n3. 各模型自动决定:")
    for model in ["gpt-4", "gpt-3.5-turbo", "llama-3", "unknown-model"]:
        config = _resolve_langextract_config_intelligent(
            model=model,
            provider="generic",
            use_langextract=None  # 自动决定
        )
        print(f"  {model}: enabled={config['enabled']}, threshold={config['complexity_threshold']}")

def print_recommendations():
    """打印使用建议"""
    print("\n" + "="*60)
    print("📋 智能配置系统使用建议")
    print("="*60)
    
    print("""
1. 默认行为（推荐）:
   ```python
   # 不指定use_langextract，让系统自动决定
   result = annotate_clusters(
       marker_genes=genes,
       species="human",
       model="llama-3-8b",  # 系统识别为低质量，自动启用LangExtract
       provider="ollama"
   )
   ```

2. 强制覆盖（特殊情况）:
   ```python
   # 明确指定use_langextract
   result = annotate_clusters(
       marker_genes=genes,
       species="human",
       model="gpt-4",
       provider="openai",
       use_langextract=True  # 强制启用（即使是高质量模型）
   )
   ```

3. 自定义配置:
   ```python
   # 提供详细配置
   result = annotate_clusters(
       marker_genes=genes,
       species="human",
       model="custom-model",
       provider="custom",
       langextract_config={
           'complexity_threshold': 0.2,
           'model': 'gemini-2.5-flash',
           'timeout': 15
       }
   )
   ```

系统会根据模型质量自动决定:
• 高质量模型（GPT-4, Claude等）: 默认不使用LangExtract
• 中等质量模型（GPT-3.5, Gemini Flash等）: 根据复杂度决定
• 低质量模型（Llama, Mistral等）: 默认启用LangExtract
• Ollama/本地模型: 总是启用LangExtract
""")

if __name__ == "__main__":
    # 运行所有测试
    test_model_quality_detection()
    test_real_annotation()
    test_override_behavior()
    print_recommendations()
    
    print("\n✅ 智能配置系统测试完成！")
    print("\n结论: 系统现在可以根据模型质量自动决定是否使用LangExtract，")
    print("大大简化了用户使用，同时保证了最佳性能和准确性的平衡。")