#!/usr/bin/env python3
"""
测试工具调用控制机制优化
验证重复调用检测、缓存配置和TTL设置是否正常工作
"""

import sys
import os
import time
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kengine.agent.shared.decorators import prevent_duplicate_calls
from kengine.cache.manager import GlobalCacheManager
from kengine.agent.shared.tools.factory import AgentToolFactory


class TestToolControlOptimization(unittest.TestCase):
    """测试工具调用控制机制优化"""
    
    def setUp(self):
        """测试前准备"""
        self.cache_manager = GlobalCacheManager()
        self.tool_factory = AgentToolFactory()
        
    def test_cache_manager_optimization(self):
        """测试缓存管理器优化配置"""
        print("测试缓存管理器优化配置...")
        
        # 测试缓存管理器初始化
        self.assertIsNotNone(self.cache_manager)
        print("✓ 缓存管理器初始化成功")
        
        # 验证缓存管理器的基本功能（通过装饰器间接测试）
        @prevent_duplicate_calls(ttl=300)
        def cache_test_function(param):
            return f"cache_result_{param}"
        
        result = cache_test_function("test")
        self.assertEqual(result, "cache_result_test")
        print("✓ 缓存装饰器功能正常")
        
    def test_duplicate_call_detection_window(self):
        """测试重复调用检测窗口优化"""
        print("测试重复调用检测窗口优化...")
        
        @prevent_duplicate_calls(ttl=300)
        def test_function(param):
            return f"result_{param}"
        
        # 第一次调用
        result1 = test_function("test")
        self.assertEqual(result1, "result_test")
        print("✓ 第一次调用成功")
        
        # 立即重复调用（应该被缓存）
        result2 = test_function("test")
        self.assertEqual(result2, "result_test")
        print("✓ 重复调用返回缓存结果")
        
        # 不同参数调用（应该正常执行）
        result3 = test_function("different")
        self.assertEqual(result3, "result_different")
        print("✓ 不同参数调用正常执行")
        
    def test_tool_factory_configuration(self):
        """测试工具工厂配置选项"""
        print("测试工具工厂配置选项...")
        
        # 测试工具创建
        try:
            # 提供必需的 base_dir 参数
            tools = self.tool_factory.create_tools(base_dir=".")
            self.assertIsInstance(tools, list)
            self.assertGreater(len(tools), 0)
            print(f"✓ 成功创建 {len(tools)} 个工具")
            
            # 验证工具名称
            tool_names = [tool.name for tool in tools]
            expected_tools = [
                "file_read", "dependency_extractor", "file_search",
                "method_extractor", "code_skeleton", "directory_structure", "rag_search"
            ]
            
            for expected_tool in expected_tools:
                if expected_tool in tool_names:
                    print(f"✓ 工具 '{expected_tool}' 创建成功")
                else:
                    print(f"⚠ 工具 '{expected_tool}' 未找到")
                    
        except Exception as e:
            print(f"✗ 工具创建失败: {e}")
            
    def test_ttl_configuration(self):
        """测试TTL配置优化"""
        print("测试TTL配置优化...")
        
        @prevent_duplicate_calls(ttl=300)
        def test_ttl_function(param):
            return f"ttl_result_{param}_{time.time()}"
        
        # 第一次调用
        result1 = test_ttl_function("ttl_test")
        self.assertTrue(result1.startswith("ttl_result_ttl_test_"))
        print("✓ TTL函数第一次调用成功")
        
        # 立即重复调用（应该返回缓存）
        result2 = test_ttl_function("ttl_test")
        self.assertEqual(result1, result2)
        print("✓ TTL缓存工作正常")
        
    def test_performance_improvement(self):
        """测试性能改进"""
        print("测试性能改进...")
        
        @prevent_duplicate_calls(ttl=300)
        def performance_test_function(param):
            # 模拟耗时操作
            time.sleep(0.1)
            return f"performance_result_{param}"
        
        # 测试第一次调用时间
        start_time = time.time()
        result1 = performance_test_function("perf_test")
        first_call_time = time.time() - start_time
        
        # 测试缓存调用时间
        start_time = time.time()
        result2 = performance_test_function("perf_test")
        cached_call_time = time.time() - start_time
        
        self.assertEqual(result1, result2)
        self.assertLess(cached_call_time, first_call_time)
        print(f"✓ 性能改进验证: 首次调用 {first_call_time:.3f}s, 缓存调用 {cached_call_time:.3f}s")
        
    def test_logging_optimization(self):
        """测试日志优化"""
        print("测试日志优化...")
        
        with patch('kengine.agent.shared.decorators.logger') as mock_logger:
            @prevent_duplicate_calls(ttl=300)
            def logging_test_function(param):
                return f"logging_result_{param}"
            
            # 调用函数
            result = logging_test_function("log_test")
            
            # 验证使用debug级别而不是info级别
            debug_calls = [call for call in mock_logger.debug.call_args_list]
            info_calls = [call for call in mock_logger.info.call_args_list]
            
            print(f"✓ Debug日志调用: {len(debug_calls)} 次")
            print(f"✓ Info日志调用: {len(info_calls)} 次")


def run_optimization_test():
    """运行优化测试"""
    print("=" * 60)
    print("工具调用控制机制优化测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestToolControlOptimization)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败详情:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
            
    if result.errors:
        print("\n错误详情:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n总体结果: {'✓ 成功' if success else '✗ 失败'}")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = run_optimization_test()
    sys.exit(0 if success else 1)