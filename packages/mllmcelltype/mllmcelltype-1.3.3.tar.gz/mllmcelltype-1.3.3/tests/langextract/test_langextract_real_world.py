#!/usr/bin/env python3
"""
真实场景下的LangExtract测试
测试各种复杂的LLM输出格式和边缘情况
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add the mllmcelltype package to the Python path
sys.path.insert(0, str(Path(__file__).parent))

class RealWorldTester:
    """真实场景测试器"""
    
    def __init__(self):
        self.test_cases = self._create_test_cases()
        self.results = {
            'traditional': {'success': 0, 'failed': 0, 'partial': 0},
            'langextract': {'success': 0, 'failed': 0, 'partial': 0}
        }
        
    def _create_test_cases(self) -> List[Dict]:
        """创建各种真实场景的测试用例"""
        return [
            {
                'name': '标准格式',
                'clusters': ['0', '1', '2'],
                'llm_output': [
                    'Cluster 0: T cells',
                    'Cluster 1: B cells', 
                    'Cluster 2: NK cells'
                ],
                'expected': {'0': 'T cells', '1': 'B cells', '2': 'NK cells'}
            },
            {
                'name': '详细解释格式',
                'clusters': ['0', '1', '2'],
                'llm_output': [
                    'Based on the expression of CD3D, CD3E, and CD3G markers, Cluster 0 is identified as T cells with high confidence.',
                    'The presence of CD19 and MS4A1 markers strongly indicates that Cluster 1 contains B cells.',
                    'Cluster 2 shows high expression of NCAM1 and NKG7, characteristic of NK cells.'
                ],
                'expected': {'0': 'T cells', '1': 'B cells', '2': 'NK cells'}
            },
            {
                'name': 'JSON嵌套格式',
                'clusters': ['0', '1', '2'],
                'llm_output': [
                    '```json',
                    '{',
                    '  "annotations": {',
                    '    "Cluster 0": {"cell_type": "CD4+ T cells", "confidence": "high", "markers": ["CD3D", "CD4"]},',
                    '    "Cluster 1": {"cell_type": "B cells", "confidence": "high", "markers": ["CD19", "CD20"]},',
                    '    "Cluster 2": {"cell_type": "Monocytes", "confidence": "medium", "markers": ["CD14", "LYZ"]}',
                    '  }',
                    '}',
                    '```'
                ],
                'expected': {'0': 'CD4+ T cells', '1': 'B cells', '2': 'Monocytes'}
            },
            {
                'name': '混合格式（文字+列表）',
                'clusters': ['0', '1', '2', '3'],
                'llm_output': [
                    'Based on the marker analysis, here are the cell type annotations:',
                    '',
                    '- Cluster 0: Memory T cells (CD3+, CD45RO+)',
                    '- Cluster 1: Naive B cells (CD19+, IgD+)',
                    '- Cluster 2: Classical monocytes (CD14++, CD16-)',
                    '- Cluster 3: Plasma cells (CD138+, CD38++)',
                    '',
                    'Note: Confidence is high for all annotations.'
                ],
                'expected': {'0': 'Memory T cells', '1': 'Naive B cells', '2': 'Classical monocytes', '3': 'Plasma cells'}
            },
            {
                'name': '表格格式',
                'clusters': ['0', '1', '2'],
                'llm_output': [
                    '| Cluster | Cell Type | Key Markers |',
                    '|---------|-----------|-------------|',
                    '| Cluster 0 | CD8+ T cells | CD3D, CD8A, GZMB |',
                    '| Cluster 1 | Regulatory T cells | CD3D, CD4, FOXP3 |',
                    '| Cluster 2 | Dendritic cells | ITGAX, CD86, HLA-DRA |'
                ],
                'expected': {'0': 'CD8+ T cells', '1': 'Regulatory T cells', '2': 'Dendritic cells'}
            },
            {
                'name': '编号列表格式',
                'clusters': ['0', '1', '2', '3', '4'],
                'llm_output': [
                    '1. Cluster 0: Effector T cells',
                    '2. Cluster 1: Memory B cells',
                    '3. Cluster 2: M1 macrophages',
                    '4. Cluster 3: Neutrophils',
                    '5. Cluster 4: Eosinophils'
                ],
                'expected': {'0': 'Effector T cells', '1': 'Memory B cells', '2': 'M1 macrophages', '3': 'Neutrophils', '4': 'Eosinophils'}
            },
            {
                'name': '不规则格式（带解释）',
                'clusters': ['0', '1', '2'],
                'llm_output': [
                    'Looking at Cluster 0, the high expression of T cell markers suggests these are T cells, specifically CD4+ helper T cells.',
                    'For Cluster 1, we see B cell markers, indicating B lymphocytes.',
                    'Cluster 2 appears to be myeloid cells, most likely dendritic cells based on the marker profile.'
                ],
                'expected': {'0': 'CD4+ helper T cells', '1': 'B lymphocytes', '2': 'dendritic cells'}
            },
            {
                'name': '部分缺失格式',
                'clusters': ['0', '1', '2', '3'],
                'llm_output': [
                    'Cluster 0: T cells',
                    'Cluster 1: B cells',
                    'Cluster 2 is difficult to identify with certainty',
                    'Cluster 3: NK cells'
                ],
                'expected': {'0': 'T cells', '1': 'B cells', '2': 'Unknown', '3': 'NK cells'}
            },
            {
                'name': '复杂嵌套JSON',
                'clusters': ['0', '1'],
                'llm_output': [
                    '{"results": {"cluster_annotations": [',
                    '  {"id": "0", "annotation": {"primary": "T cells", "subtype": "CD4+", "confidence": 0.95}},',
                    '  {"id": "1", "annotation": {"primary": "B cells", "subtype": "Memory", "confidence": 0.88}}',
                    ']}}'
                ],
                'expected': {'0': 'T cells', '1': 'B cells'}
            },
            {
                'name': '自然语言描述',
                'clusters': ['0', '1', '2'],
                'llm_output': [
                    'The first cluster (Cluster 0) consists primarily of T lymphocytes. ',
                    'The second one (Cluster 1) contains B lymphocytes. ',
                    'Finally, Cluster 2 represents natural killer cells.'
                ],
                'expected': {'0': 'T lymphocytes', '1': 'B lymphocytes', '2': 'natural killer cells'}
            }
        ]
    
    def test_parsing_methods(self, test_case: Dict) -> Tuple[Dict, Dict]:
        """测试两种解析方法"""
        from mllmcelltype.utils import format_results
        
        clusters = test_case['clusters']
        llm_output = test_case['llm_output']
        
        # 测试Traditional解析
        traditional_result = format_results(
            results=llm_output,
            clusters=clusters,
            use_langextract=False
        )
        
        # 测试LangExtract解析
        langextract_result = format_results(
            results=llm_output,
            clusters=clusters,
            use_langextract=True,
            langextract_config={'complexity_threshold': 0.0}  # 强制触发
        )
        
        return traditional_result, langextract_result
    
    def evaluate_result(self, result: Dict, expected: Dict) -> str:
        """评估解析结果"""
        if not result:
            return 'failed'
        
        correct = 0
        total = len(expected)
        
        for cluster_id, expected_type in expected.items():
            if cluster_id in result:
                actual = result[cluster_id].lower()
                expected_lower = expected_type.lower()
                
                # 模糊匹配 - 如果主要词汇存在就算对
                key_words = expected_lower.split()
                if any(word in actual for word in key_words if len(word) > 3):
                    correct += 1
                elif expected_lower in actual or actual in expected_lower:
                    correct += 1
        
        if correct == total:
            return 'success'
        elif correct > 0:
            return 'partial'
        else:
            return 'failed'
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始真实场景测试")
        print("="*80)
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n📝 测试用例 {i}/{len(self.test_cases)}: {test_case['name']}")
            print("-"*60)
            
            # 显示输入
            print("输入格式预览:")
            for line in test_case['llm_output'][:3]:
                print(f"  {line[:60]}..." if len(line) > 60 else f"  {line}")
            if len(test_case['llm_output']) > 3:
                print(f"  ... ({len(test_case['llm_output'])-3} more lines)")
            
            # 运行测试
            try:
                start_time = time.time()
                traditional, langextract = self.test_parsing_methods(test_case)
                elapsed = time.time() - start_time
                
                # 评估结果
                trad_eval = self.evaluate_result(traditional, test_case['expected'])
                lang_eval = self.evaluate_result(langextract, test_case['expected'])
                
                # 更新统计
                self.results['traditional'][trad_eval] += 1
                self.results['langextract'][lang_eval] += 1
                
                # 显示结果
                print(f"\n期望结果: {test_case['expected']}")
                print(f"\nTraditional解析:")
                print(f"  结果: {traditional}")
                print(f"  评估: {self._get_emoji(trad_eval)} {trad_eval.upper()}")
                
                print(f"\nLangExtract解析:")
                print(f"  结果: {langextract}")
                print(f"  评估: {self._get_emoji(lang_eval)} {lang_eval.upper()}")
                
                print(f"\n⏱️  处理时间: {elapsed:.2f}秒")
                
                # 如果LangExtract表现更好，特别标注
                if lang_eval == 'success' and trad_eval != 'success':
                    print("✨ LangExtract表现更好！")
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                self.results['traditional']['failed'] += 1
                self.results['langextract']['failed'] += 1
    
    def _get_emoji(self, status: str) -> str:
        """获取状态对应的emoji"""
        return {'success': '✅', 'partial': '⚠️', 'failed': '❌'}.get(status, '❓')
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*80)
        print("📊 测试总结")
        print("="*80)
        
        total = len(self.test_cases)
        
        print("\n传统解析 (Traditional Parsing):")
        trad = self.results['traditional']
        print(f"  ✅ 成功: {trad['success']}/{total} ({trad['success']/total*100:.1f}%)")
        print(f"  ⚠️  部分: {trad['partial']}/{total} ({trad['partial']/total*100:.1f}%)")
        print(f"  ❌ 失败: {trad['failed']}/{total} ({trad['failed']/total*100:.1f}%)")
        
        print("\nLangExtract解析:")
        lang = self.results['langextract']
        print(f"  ✅ 成功: {lang['success']}/{total} ({lang['success']/total*100:.1f}%)")
        print(f"  ⚠️  部分: {lang['partial']}/{total} ({lang['partial']/total*100:.1f}%)")
        print(f"  ❌ 失败: {lang['failed']}/{total} ({lang['failed']/total*100:.1f}%)")
        
        # 计算改进
        improvement = lang['success'] - trad['success']
        if improvement > 0:
            print(f"\n🎯 LangExtract相比Traditional:")
            print(f"   提升了 {improvement} 个成功案例 (+{improvement/total*100:.1f}%)")
        elif improvement < 0:
            print(f"\n⚠️  LangExtract表现不如Traditional")
        else:
            print(f"\n➡️  两种方法表现相同")

def test_edge_cases():
    """测试边缘情况"""
    print("\n" + "="*80)
    print("🔍 边缘情况测试")
    print("="*80)
    
    from mllmcelltype.utils import format_results
    
    edge_cases = [
        {
            'name': '空输出',
            'clusters': ['0', '1'],
            'output': [],
        },
        {
            'name': '单行输出',
            'clusters': ['0', '1'],
            'output': ['Cluster 0: T cells, Cluster 1: B cells'],
        },
        {
            'name': '错误JSON',
            'clusters': ['0', '1'],
            'output': ['{"cluster": "0", "type": "T cells"', 'ERROR: JSON parse failed'],
        },
        {
            'name': '混合语言',
            'clusters': ['0', '1'],
            'output': ['Cluster 0: T细胞 (T cells)', 'Cluster 1: B细胞 (B cells)'],
        },
        {
            'name': '特殊字符',
            'clusters': ['0', '1'],
            'output': ['Cluster 0: T-cells/lymphocytes', 'Cluster 1: B-cells (CD19+/CD20+)'],
        }
    ]
    
    for case in edge_cases:
        print(f"\n测试: {case['name']}")
        print(f"输入: {case['output']}")
        
        try:
            # Traditional
            trad_result = format_results(case['output'], case['clusters'], use_langextract=False)
            print(f"Traditional: {trad_result}")
            
            # LangExtract
            lang_result = format_results(case['output'], case['clusters'], use_langextract=True,
                                        langextract_config={'complexity_threshold': 0.0})
            print(f"LangExtract: {lang_result}")
            
        except Exception as e:
            print(f"错误: {e}")

def test_performance():
    """性能测试"""
    print("\n" + "="*80)
    print("⚡ 性能测试")
    print("="*80)
    
    from mllmcelltype.utils import format_results
    import statistics
    
    # 准备测试数据
    test_sizes = [5, 10, 20, 50]
    
    for size in test_sizes:
        clusters = [str(i) for i in range(size)]
        simple_output = [f"Cluster {i}: Cell type {i}" for i in range(size)]
        complex_output = [
            f"Based on extensive analysis, Cluster {i} appears to be Cell type {i} with high confidence"
            for i in range(size)
        ]
        
        # 测试Traditional
        trad_times = []
        for _ in range(5):
            start = time.time()
            format_results(simple_output, clusters, use_langextract=False)
            trad_times.append(time.time() - start)
        
        # 测试LangExtract
        lang_times = []
        for _ in range(5):
            start = time.time()
            format_results(complex_output, clusters, use_langextract=True,
                         langextract_config={'complexity_threshold': 0.0})
            lang_times.append(time.time() - start)
        
        print(f"\n{size} clusters:")
        print(f"  Traditional: {statistics.mean(trad_times)*1000:.1f}ms (±{statistics.stdev(trad_times)*1000:.1f}ms)")
        print(f"  LangExtract: {statistics.mean(lang_times)*1000:.1f}ms (±{statistics.stdev(lang_times)*1000:.1f}ms)")

if __name__ == "__main__":
    print("🚀 LangExtract真实场景测试")
    print("="*80)
    
    # 运行主要测试
    tester = RealWorldTester()
    tester.run_all_tests()
    tester.print_summary()
    
    # 边缘情况测试
    test_edge_cases()
    
    # 性能测试
    test_performance()
    
    print("\n" + "="*80)
    print("✅ 所有测试完成！")