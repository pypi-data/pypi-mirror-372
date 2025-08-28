"""
Model quality configuration for intelligent LangExtract usage.
根据模型质量自动决定是否使用LangExtract
"""

# 模型质量分级配置
MODEL_QUALITY_MAP = {
    # 高质量模型 - 不需要LangExtract
    'high_quality': {
        'models': [
            'gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-4.1',
            'claude-3-opus', 'claude-3-sonnet', 'claude-3.5',
            'gemini-pro', 'gemini-ultra', 'gemini-2.0',
        ],
        'use_langextract': False,
        'complexity_threshold': 0.7  # 只在极复杂情况下使用
    },
    
    # 中等质量模型 - 可选LangExtract
    'medium_quality': {
        'models': [
            'gpt-3.5-turbo', 'gpt-4-mini',
            'claude-3-haiku', 'claude-instant',
            'gemini-flash', 'gemini-2.5-flash',
            'qwen-max', 'qwen-plus',
            'deepseek-chat', 'deepseek-coder',
        ],
        'use_langextract': None,  # 自动决定
        'complexity_threshold': 0.4  # 标准阈值
    },
    
    # 低质量模型 - 推荐LangExtract
    'low_quality': {
        'models': [
            'llama', 'llama-2', 'llama-3', 'llama-3.1', 'llama-3.2',
            'mistral', 'mixtral', 'falcon',
            'vicuna', 'alpaca', 'wizardlm',
            'phi', 'orca', 'zephyr',
        ],
        'use_langextract': True,  # 默认启用
        'complexity_threshold': 0.1  # 低阈值，容易触发
    }
}

def get_model_quality_config(model: str) -> dict:
    """
    根据模型名称获取质量配置
    
    Args:
        model: 模型名称
        
    Returns:
        dict: 包含use_langextract和complexity_threshold的配置
    """
    model_lower = model.lower()
    
    # 检查每个质量级别
    for quality_level, config in MODEL_QUALITY_MAP.items():
        for model_pattern in config['models']:
            if model_pattern in model_lower:
                return {
                    'quality_level': quality_level,
                    'use_langextract': config['use_langextract'],
                    'complexity_threshold': config['complexity_threshold']
                }
    
    # 默认配置 - 对未知模型保守处理
    return {
        'quality_level': 'unknown',
        'use_langextract': None,  # 自动决定
        'complexity_threshold': 0.3  # 较低阈值
    }

def should_use_langextract_for_model(model: str, override: bool = None) -> tuple[bool, dict]:
    """
    决定是否为特定模型使用LangExtract
    
    Args:
        model: 模型名称
        override: 用户强制设置（如果提供）
        
    Returns:
        tuple: (是否使用LangExtract, 配置字典)
    """
    # 如果用户明确指定，使用用户设置
    if override is not None:
        return override, {'source': 'user_override'}
    
    # 获取模型质量配置
    config = get_model_quality_config(model)
    
    # 根据配置决定
    use_langextract = config['use_langextract']
    
    # 如果是None（自动决定），默认不使用
    if use_langextract is None:
        use_langextract = False
        config['source'] = 'auto_decision'
    else:
        config['source'] = 'model_quality_config'
    
    return use_langextract, config

# 特殊处理规则
SPECIAL_CASES = {
    # OpenRouter上的免费模型通常质量较低
    'openrouter': {
        'free_models': True,  # 免费模型默认使用LangExtract
        'complexity_threshold': 0.2
    },
    
    # 本地模型（Ollama）通常需要LangExtract
    'ollama': {
        'use_langextract': True,
        'complexity_threshold': 0.15
    },
    
    # API限制较严的提供商
    'rate_limited_providers': ['openrouter', 'together', 'replicate'],
}

def get_provider_config(provider: str) -> dict:
    """
    获取特定provider的配置建议
    
    Args:
        provider: 提供商名称
        
    Returns:
        dict: Provider特定配置
    """
    provider_lower = provider.lower()
    
    if provider_lower == 'ollama':
        return SPECIAL_CASES['ollama']
    elif provider_lower == 'openrouter':
        return SPECIAL_CASES['openrouter']
    elif provider_lower in SPECIAL_CASES['rate_limited_providers']:
        return {
            'use_langextract': True,
            'complexity_threshold': 0.2,
            'note': 'Rate-limited provider, using LangExtract for better accuracy'
        }
    
    return {}

def get_recommended_config(model: str, provider: str = None) -> dict:
    """
    获取推荐的完整配置
    
    Args:
        model: 模型名称
        provider: 提供商名称（可选）
        
    Returns:
        dict: 完整的推荐配置
    """
    # 获取模型配置
    use_langextract, model_config = should_use_langextract_for_model(model)
    
    # 获取provider配置
    provider_config = get_provider_config(provider) if provider else {}
    
    # 合并配置（provider配置优先级更高）
    final_config = {
        'use_langextract': provider_config.get('use_langextract', use_langextract),
        'langextract_config': {
            'complexity_threshold': provider_config.get(
                'complexity_threshold', 
                model_config.get('complexity_threshold', 0.3)
            ),
            'model': 'gemini-2.5-flash',  # 默认使用Gemini来清理
            'timeout': 10
        },
        'reason': f"Model: {model_config.get('quality_level', 'unknown')} quality"
    }
    
    # 添加provider说明
    if provider_config:
        final_config['reason'] += f", Provider: {provider}"
    
    return final_config

# 导出函数
__all__ = [
    'get_model_quality_config',
    'should_use_langextract_for_model',
    'get_provider_config',
    'get_recommended_config',
    'MODEL_QUALITY_MAP'
]