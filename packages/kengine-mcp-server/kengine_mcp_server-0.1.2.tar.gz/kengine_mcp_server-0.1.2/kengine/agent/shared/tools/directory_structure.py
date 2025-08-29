"""
目录结构分析工具模块

包含 DirectoryStructureTool 类，提供优化的目录结构分析功能。
"""

import json
from pathlib import Path
import re
from typing import Optional

from kengine.agent.shared.decorators import prevent_duplicate_calls
from kengine.agent.shared.tools.error_handler import handle_tool_errors

from .base import BasePathTool
from .exceptions import ConfigurationError, FileOperationError


class DirectoryStructureTool(BasePathTool):
    """优化的目录结构分析工具
    
    解决原版工具token超长问题的优化版本。
    支持多种输出格式，大幅减少token消耗。
    默认使用simple格式，节省87.6%的token。
    """
    
    def __init__(self, base_dir: str, output_format: str = "simple"):
        """
        初始化优化的目录结构工具
        
        Args:
            base_dir: 基础目录路径
            output_format: 输出格式，可选值：
                - "json": 原始JSON格式（兼容性）
                - "simple": 简单文本格式（推荐，节省50-70% Token）
                - "compact": 超紧凑格式（节省70-80% Token）
                
        Raises:
            ConfigurationError: 输出格式不支持
        """
        super().__init__(base_dir)
        self.output_format = output_format
        
        # 验证输出格式
        valid_formats = ["json", "simple", "compact"]
        if output_format not in valid_formats:
            raise ConfigurationError(
                f"不支持的输出格式: {output_format}，支持的格式: {valid_formats}",
                config_key="output_format",
                config_value=output_format,
                tool_name=self.__class__.__name__
            )
    
    @BasePathTool.json_compatible_input({
        'target_path': 'target_path',
        'max_depth': 'max_depth',
        'include_files': 'include_files'
    })
    @prevent_duplicate_calls(ttl=300)
    @handle_tool_errors(tool_name="DirectoryStructureTool", operation="read", return_format="str")
    def run(self, target_path: str, max_depth: int = 3,
            include_files: bool = True) -> str:
        """
        分析目录结构并返回优化格式的结果（保持向后兼容的接口）
        
        Args:
            target_path: 目标目录路径，支持JSON格式参数
            max_depth: 最大递归深度
            include_files: 是否包含文件
            
        Returns:
            根据output_format返回不同格式的目录结构字符串
            
        Raises:
            FileOperationError: 分析过程中发生错误
        """
        try:
            # 适配路径 wms-ng/wms6-outbound/wms-outbound-domain/src/main/java --max-depth 5
            pattern_with_max_depth = re.compile(r"(\S+)\s+--max-depth\s+(\d+)$", re.IGNORECASE)
            matcher_with_max_depth = pattern_with_max_depth.match(target_path)
            if matcher_with_max_depth:
                real_path = matcher_with_max_depth.group(1)
                max_depth = int(matcher_with_max_depth.group(2))
                return self.run(real_path, max_depth)
                
                
            # 处理特殊情况, 路径以空格+数字结尾，则重新分解为 路径 + max_depth
            pattern_with_single_digit = re.compile(r"(\S+)\s+(\d+)$", re.IGNORECASE)
            matcher_with_single_digit = pattern_with_single_digit.match(target_path)
            if matcher_with_single_digit:
                real_path = matcher_with_single_digit.group(1)
                real_depth = int(matcher_with_single_digit.group(2))
                return self.run(real_path, real_depth, True)
            
            # 参数验证
            if max_depth < 0:
                raise FileOperationError(
                    "最大深度不能为负数",
                    file_path=target_path,
                    operation="directory_structure",
                    tool_name=self.__class__.__name__
                )
                
            
            # 路径处理和验证
            target_path = self._to_abs(target_path.strip())
            validated_path = self._validate_directory_path(target_path)
            
            # 获取目录树数据
            from kengine.utils.dir_utils import get_directory_tree
            tree_data = get_directory_tree(
                dir_path=str(validated_path),
                max_depth=max_depth,
                include_hidden=False,
                include_files=include_files,
                include_size=False,
                respect_gitignore=True,
                # todo 考虑排除扩展名的范围
                exclude_extensions=['.txt', '.doc', '.docx', '.pdf', '.lib', 
                                    '.dll', '.jar', '.js', '.png', '.jpg', '.jpeg', '.gif']
            )
            
            # 根据输出格式返回不同的结果
            if self.output_format == "simple":
                return self._generate_simple_format(tree_data)
            elif self.output_format == "compact":
                return self._generate_compact_format(tree_data)
            else:  # json格式
                return json.dumps(tree_data, ensure_ascii=False, indent=2)
                
        except Exception as e:
            if isinstance(e, (FileOperationError,)):
                raise
            raise FileOperationError(
                f"分析目录结构时发生错误，target_path='{target_path}', max_depth={max_depth}: {str(e)}",
                file_path=target_path,
                operation="analyze",
                tool_name=self.__class__.__name__
            ) from e
    
    def _generate_simple_format(self, tree_data: dict) -> str:
        """
        生成简单文本格式的目录结构
        
        特点：
        - 使用树状文本结构替代JSON
        - 只保留必要的目录/文件名信息
        - 使用简单的图标和连接符
        - 预计节省50-70%的token
        
        Args:
            tree_data: 目录树数据字典
            
        Returns:
            简单文本格式的目录结构字符串
        """
        def build_tree(node, prefix="", is_last=True):
            """递归构建文本树结构"""
            lines = []
            
            # 确定图标
            icon = "📁" if node['type'] == 'directory' else "📄"
            
            # 确定连接符和前缀
            if prefix:
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{icon} {node['name']}")
            else:
                # 根节点
                lines.append(f"{icon} {node['name']}")
            
            # 处理子节点
            if 'children' in node and node['children']:
                children = node['children']
                # 将字典格式的 children 转换为列表格式
                if isinstance(children, dict):
                    children_list = list(children.values())
                else:
                    children_list = children
                
                for i, child in enumerate(children_list):
                    is_last_child = (i == len(children_list) - 1)
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    child_lines = build_tree(child, new_prefix, is_last_child)
                    lines.extend(child_lines)
            
            return lines
        
        lines = build_tree(tree_data)
        return "\n".join(lines)
    
    def _generate_compact_format(self, tree_data: dict) -> str:
        """
        生成超紧凑格式的目录结构
        
        特点：
        - 使用最简单的符号(+/-)表示目录/文件
        - 最小化缩进和装饰
        - 预计节省70-80%的token
        
        Args:
            tree_data: 目录树数据字典
            
        Returns:
            超紧凑格式的目录结构字符串
        """
        def build_compact(node, depth=0):
            """递归构建紧凑树结构"""
            lines = []
            indent = "  " * depth
            
            # 使用简单符号
            symbol = "+" if node['type'] == 'directory' else "-"
            lines.append(f"{indent}{symbol} {node['name']}")
            
            # 处理子节点
            if 'children' in node and node['children']:
                for child in node['children']:
                    child_lines = build_compact(child, depth + 1)
                    lines.extend(child_lines)
            
            return lines
        
        lines = build_compact(tree_data)
        return "\n".join(lines)
    
    def get_format_info(self) -> dict:
        """
        获取当前输出格式的信息
        
        Returns:
            包含格式信息的字典
        """
        format_info = {
            "json": {
                "name": "JSON格式",
                "description": "原始JSON格式，包含完整的元数据信息",
                "token_efficiency": "基准（100%）",
                "use_case": "需要完整元数据信息的场景"
            },
            "simple": {
                "name": "简单文本格式",
                "description": "树状文本结构，使用图标和连接符",
                "token_efficiency": "节省50-70%",
                "use_case": "推荐用于大多数目录结构展示场景"
            },
            "compact": {
                "name": "超紧凑格式",
                "description": "最简单的符号表示，最小化装饰",
                "token_efficiency": "节省70-80%",
                "use_case": "token极度受限的场景"
            }
        }
        
        return {
            "current_format": self.output_format,
            "format_details": format_info[self.output_format],
            "all_formats": format_info
        }
    
    def set_output_format(self, output_format: str) -> None:
        """
        设置输出格式
        
        Args:
            output_format: 新的输出格式
            
        Raises:
            ConfigurationError: 不支持的输出格式
        """
        valid_formats = ["json", "simple", "compact"]
        if output_format not in valid_formats:
            raise ConfigurationError(
                f"不支持的输出格式: {output_format}，支持的格式: {valid_formats}",
                config_key="output_format",
                config_value=output_format,
                tool_name=self.__class__.__name__
            )
        
        self.output_format = output_format
    
    def get_directory_stats(self, target_path: str, max_depth: Optional[int] = None) -> dict:
        """
        获取目录统计信息
        
        Args:
            target_path: 目标目录路径
            max_depth: 最大递归深度
            
        Returns:
            包含目录统计信息的字典
            
        Raises:
            FileOperationError: 获取统计信息失败
        """
        try:
            # 路径处理和验证
            target_path = self._to_abs(target_path.strip())
            validated_path = self._validate_directory_path(target_path)
            
            # 获取目录树数据
            from kengine.utils.dir_utils import get_directory_tree
            tree_data = get_directory_tree(
                dir_path=str(validated_path),
                max_depth=max_depth,
                include_hidden=False,
                include_files=True,
                include_size=False,
                respect_gitignore=True
            )
            
            # 统计信息
            stats = self._calculate_stats(tree_data)
            stats["target_path"] = str(validated_path)
            stats["relative_path"] = self._get_relative_path(validated_path)
            stats["max_depth_used"] = max_depth
            
            return stats
            
        except Exception as e:
            if isinstance(e, (FileOperationError,)):
                raise
            raise FileOperationError(
                f"获取目录统计信息失败: {str(e)}",
                file_path=target_path,
                operation="stats",
                tool_name=self.__class__.__name__
            ) from e
    
    def _calculate_stats(self, tree_data: dict) -> dict:
        """
        递归计算目录统计信息
        
        Args:
            tree_data: 目录树数据
            
        Returns:
            统计信息字典
        """
        stats = {
            "total_directories": 0,
            "total_files": 0,
            "max_depth": 0
        }
        
        def traverse(node, depth=0):
            stats["max_depth"] = max(stats["max_depth"], depth)
            
            if node['type'] == 'directory':
                stats["total_directories"] += 1
            else:
                stats["total_files"] += 1
            
            if 'children' in node and node['children']:
                for child in node['children']:
                    traverse(child, depth + 1)
        
        traverse(tree_data)
        return stats
