"""
基于 tree-sitter 的 Java 方法引用分析器

提供精确的 Java 方法引用查找功能，通过 AST 分析找到指定方法的所有调用位置。
"""

import logging
from typing import List, Dict, Optional, Set
from pathlib import Path
import os

from .ast_parser import JavaASTParser
from .models import MethodReferenceResult, VariableInfo, MethodCallInfo

logger = logging.getLogger(__name__)


class TreeSitterJavaMethodAnalyzer:
    """基于 tree-sitter 的 Java 方法引用分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.ast_parser = JavaASTParser()
    
    def find_all_method_calls(self, file_path: str, method_name: str) -> MethodReferenceResult:
        """
        查找文件中所有指定方法名的调用（不限制变量类型）
        
        Args:
            file_path: 要分析的 Java 文件路径
            method_name: 方法名（如 "findById"）
            
        Returns:
            MethodReferenceResult: 方法引用结果
        """
        try:
            logger.info(f"开始分析文件: {file_path}")
            logger.info(f"查找所有对方法 {method_name} 的调用")
            
            # 验证文件存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return MethodReferenceResult(
                    success=False,
                    target_class="*",
                    target_method=method_name,
                    file_path=file_path,
                    variables=[],
                    method_calls=[],
                    error_message=f"文件不存在: {file_path}"
                )
            
            # 解析文件
            tree = self.ast_parser.parse_file(file_path)
            if not tree:
                error_msg = f"无法解析文件: {file_path}"
                logger.error(error_msg)
                return MethodReferenceResult(
                    success=False,
                    target_class="*",
                    target_method=method_name,
                    file_path=file_path,
                    variables=[],
                    method_calls=[],
                    error_message=error_msg
                )
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 查找所有方法调用（不限制变量类型）
            method_calls = self.ast_parser.find_all_method_calls_by_name(
                tree, code_content, method_name
            )
            logger.info(f"找到 {len(method_calls)} 个方法调用")
            
            return MethodReferenceResult(
                success=True,
                target_class="*",
                target_method=method_name,
                file_path=file_path,
                variables=[],
                method_calls=method_calls
            )
            
        except Exception as e:
            error_msg = f"分析文件时发生错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return MethodReferenceResult(
                success=False,
                target_class="*",
                target_method=method_name,
                file_path=file_path,
                variables=[],
                method_calls=[],
                error_message=error_msg
            )

    def find_method_references(self, 
                             file_path: str, 
                             variable_type: str, 
                             method_name: str,
                             search_paths: Optional[List[str]] = None) -> MethodReferenceResult:
        """
        查找指定类型变量的方法引用
        
        Args:
            file_path: 要分析的 Java 文件路径
            variable_type: 变量类型名（如 "UserService"）
            method_name: 方法名（如 "findById"）
            search_paths: 搜索路径列表，如果为 None 则只搜索当前文件
            
        Returns:
            MethodReferenceResult: 方法引用结果
        """
        try:
            logger.info(f"开始分析文件: {file_path}")
            logger.info(f"查找类型: {variable_type}, 方法: {method_name}")
            
            # 验证文件存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return MethodReferenceResult(
                    file_path=file_path,
                    variable_type=variable_type,
                    method_name=method_name,
                    variables=[],
                    method_calls=[],
                    success=False,
                    error_message=f"文件不存在: {file_path}"
                )
            
            # 解析文件
            tree = self.ast_parser.parse_file(file_path)
            if not tree:
                error_msg = f"无法解析文件: {file_path}"
                logger.error(error_msg)
                return MethodReferenceResult(
                    file_path=file_path,
                    variable_type=variable_type,
                    method_name=method_name,
                    variables=[],
                    method_calls=[],
                    success=False,
                    error_message=error_msg
                )
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 查找指定类型的变量
            variables = self.ast_parser.find_variables_by_type(tree, code_content, variable_type)
            logger.info(f"找到 {len(variables)} 个 {variable_type} 类型的变量")
            
            # 提取变量名集合
            variable_names = {var.name for var in variables}
            
            # 查找方法调用
            method_calls = []
            if variable_names:
                method_calls = self.ast_parser.find_method_calls(
                    tree, code_content, variable_names, method_name
                )
                logger.info(f"找到 {len(method_calls)} 个方法调用")
            
            # 如果指定了搜索路径，扩展搜索范围
            if search_paths and variable_names:
                additional_calls = self._search_in_paths(
                    search_paths, variable_names, method_name, file_path
                )
                method_calls.extend(additional_calls)
            
            return MethodReferenceResult(
                file_path=file_path,
                variable_type=variable_type,
                method_name=method_name,
                variables=variables,
                method_calls=method_calls,
                success=True
            )
            
        except Exception as e:
            error_msg = f"分析文件时发生错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return MethodReferenceResult(
                file_path=file_path,
                variable_type=variable_type,
                method_name=method_name,
                variables=[],
                method_calls=[],
                success=False,
                error_message=error_msg
            )
    
    def find_method_references_in_directory(self, 
                                          directory_path: str,
                                          variable_type: str,
                                          method_name: str,
                                          file_extensions: Optional[List[str]] = None) -> List[MethodReferenceResult]:
        """
        在目录中查找方法引用
        
        Args:
            directory_path: 目录路径
            variable_type: 变量类型名
            method_name: 方法名
            file_extensions: 文件扩展名列表，默认为 ['.java']
            
        Returns:
            List[MethodReferenceResult]: 方法引用结果列表
        """
        if file_extensions is None:
            file_extensions = ['.java']
        
        results = []
        
        try:
            # 递归查找 Java 文件
            java_files = self._find_java_files(directory_path, file_extensions)
            logger.info(f"在目录 {directory_path} 中找到 {len(java_files)} 个 Java 文件")
            
            # 分析每个文件
            for java_file in java_files:
                result = self.find_method_references(java_file, variable_type, method_name)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"在目录中查找方法引用时发生错误: {e}", exc_info=True)
            return results
    
    def find_method_references_batch(self, 
                                   file_paths: List[str],
                                   variable_type: str,
                                   method_name: str) -> List[MethodReferenceResult]:
        """
        批量查找方法引用
        
        Args:
            file_paths: 文件路径列表
            variable_type: 变量类型名
            method_name: 方法名
            
        Returns:
            List[MethodReferenceResult]: 方法引用结果列表
        """
        results = []
        
        for file_path in file_paths:
            result = self.find_method_references(file_path, variable_type, method_name)
            results.append(result)
        
        return results
    
    def _search_in_paths(self, 
                        search_paths: List[str], 
                        variable_names: Set[str], 
                        method_name: str,
                        exclude_file: str) -> List[MethodCallInfo]:
        """
        在指定路径中搜索方法调用
        
        Args:
            search_paths: 搜索路径列表
            variable_names: 变量名集合
            method_name: 方法名
            exclude_file: 要排除的文件路径
            
        Returns:
            List[MethodCallInfo]: 方法调用信息列表
        """
        method_calls = []
        
        try:
            for search_path in search_paths:
                if not os.path.exists(search_path):
                    logger.warning(f"搜索路径不存在: {search_path}")
                    continue
                
                # 查找 Java 文件
                java_files = self._find_java_files(search_path, ['.java'])
                
                for java_file in java_files:
                    # 跳过排除的文件
                    if os.path.abspath(java_file) == os.path.abspath(exclude_file):
                        continue
                    
                    # 解析文件
                    tree = self.ast_parser.parse_file(java_file)
                    if not tree:
                        continue
                    
                    # 读取文件内容
                    with open(java_file, 'r', encoding='utf-8') as f:
                        code_content = f.read()
                    
                    # 查找方法调用
                    calls = self.ast_parser.find_method_calls(
                        tree, code_content, variable_names, method_name
                    )
                    
                    # 更新文件路径信息
                    for call in calls:
                        call.file_path = java_file
                    
                    method_calls.extend(calls)
            
        except Exception as e:
            logger.error(f"在路径中搜索时发生错误: {e}", exc_info=True)
        
        return method_calls
    
    def _find_java_files(self, directory_path: str, extensions: List[str]) -> List[str]:
        """
        递归查找 Java 文件
        
        Args:
            directory_path: 目录路径
            extensions: 文件扩展名列表
            
        Returns:
            List[str]: Java 文件路径列表
        """
        java_files = []
        
        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, file)
                        java_files.append(file_path)
        
        except Exception as e:
            logger.error(f"查找 Java 文件时发生错误: {e}")
        
        return java_files
    
    def get_analysis_summary(self, results: List[MethodReferenceResult]) -> Dict:
        """
        获取分析结果摘要
        
        Args:
            results: 方法引用结果列表
            
        Returns:
            Dict: 分析摘要
        """
        total_files = len(results)
        successful_files = sum(1 for r in results if r.success)
        failed_files = total_files - successful_files
        
        total_variables = sum(len(r.variables) for r in results if r.success)
        total_method_calls = sum(len(r.method_calls) for r in results if r.success)
        
        # 按文件统计方法调用
        files_with_calls = []
        for result in results:
            if result.success and result.method_calls:
                files_with_calls.append({
                    'file_path': result.file_path,
                    'variable_count': len(result.variables),
                    'call_count': len(result.method_calls)
                })
        
        # 错误信息
        errors = []
        for result in results:
            if not result.success:
                errors.append({
                    'file_path': result.file_path,
                    'error_message': result.error_message
                })
        
        return {
            'total_files': total_files,
            'successful_files': successful_files,
            'failed_files': failed_files,
            'total_variables': total_variables,
            'total_method_calls': total_method_calls,
            'files_with_calls': files_with_calls,
            'errors': errors
        }
    
    def format_results(self, results: List[MethodReferenceResult], detailed: bool = True) -> str:
        """
        格式化分析结果
        
        Args:
            results: 方法引用结果列表
            detailed: 是否显示详细信息
            
        Returns:
            str: 格式化的结果字符串
        """
        lines = []
        
        # 添加摘要
        summary = self.get_analysis_summary(results)
        lines.append("=== 分析结果摘要 ===")
        lines.append(f"总文件数: {summary['total_files']}")
        lines.append(f"成功分析: {summary['successful_files']}")
        lines.append(f"分析失败: {summary['failed_files']}")
        lines.append(f"总变量数: {summary['total_variables']}")
        lines.append(f"总方法调用: {summary['total_method_calls']}")
        lines.append("")
        
        # 显示有方法调用的文件
        if summary['files_with_calls']:
            lines.append("=== 包含方法调用的文件 ===")
            for file_info in summary['files_with_calls']:
                lines.append(f"文件: {file_info['file_path']}")
                lines.append(f"  变量数: {file_info['variable_count']}")
                lines.append(f"  调用数: {file_info['call_count']}")
                lines.append("")
        
        # 显示详细信息
        if detailed:
            for result in results:
                if result.success and result.method_calls:
                    lines.append(f"=== 文件: {result.file_path} ===")
                    
                    # 显示变量信息
                    if result.variables:
                        lines.append("变量声明:")
                        for var in result.variables:
                            lines.append(f"  - {var.name} ({var.type_name}) 在第 {var.declaration_line} 行")
                        lines.append("")
                    
                    # 显示方法调用
                    if result.method_calls:
                        lines.append("方法调用:")
                        for call in result.method_calls:
                            lines.append(f"  - 第 {call.call_line} 行: {call.variable_name}.{call.method_name}()")
                            if call.caller_method_name != "unknown":
                                lines.append(f"    在方法 {call.caller_method_name} 中")
                            if call.arguments:
                                lines.append(f"    参数: {', '.join(call.arguments)}")
                        lines.append("")
        
        # 显示错误信息
        if summary['errors']:
            lines.append("=== 错误信息 ===")
            for error in summary['errors']:
                lines.append(f"文件: {error['file_path']}")
                lines.append(f"错误: {error['error_message']}")
                lines.append("")
        
        return '\n'.join(lines)