#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown语法修复工具

该模块提供了修复Markdown文件中常见语法错误的功能。
主要解决的问题：
1. 删除文件开头错误的```markdown标记
2. 其他常见的Markdown语法问题

重构历史：
- 2025-01-05: 重构为符合KEngine项目架构规范的版本
- 添加了统一的错误处理和结构化响应格式
- 使用@safe_file_operation装饰器进行文件操作保护

作者: KEngine团队
创建时间: 2025-01-05
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..utils.safe_file import safe_file_operation

logger = logging.getLogger(__name__)


@dataclass
class MarkdownFixResult:
    """Markdown修复结果数据类"""
    file_path: str
    success: bool
    message: str
    original_first_line: Optional[str] = None
    backup_created: bool = False


class MarkdownSyntaxFixerRefactored:
    """
    Markdown语法修复器（重构版本）
    
    该类负责修复Markdown文件中的常见语法错误。
    提供统一的错误处理、结构化响应格式和完整的日志记录。
    
    主要功能：
    1. 删除文件开头错误的```markdown标记
    2. 支持批量处理目录中的所有Markdown文件
    3. 自动创建备份文件
    
    使用方法：
        fixer = MarkdownSyntaxFixerRefactored()
        result = fixer.run("./docs")
        if result["success"]:
            print(f"修复完成: {result['message']}")
        else:
            print(f"修复失败: {result['message']}")
    """
    
    def __init__(self):
        """初始化修复器"""
        self.results: List[MarkdownFixResult] = []
        logger.info("Markdown语法修复器初始化完成")
    
    def run(self, target_directory: str, create_backup: bool = True) -> Dict[str, Any]:
        """
        运行修复工具的主入口方法
        
        Args:
            target_directory: 目标目录路径
            create_backup: 是否创建备份文件
            
        Returns:
            统一格式的响应：{"success": bool, "data": any, "message": str}
        """
        try:
            target_path = Path(target_directory)
            if not target_path.exists():
                return {
                    "success": False,
                    "data": None,
                    "message": f"目标目录不存在: {target_directory}"
                }
            
            # 查找问题文件
            problematic_files = self._find_problematic_files(target_path)
            
            if not problematic_files:
                return {
                    "success": True,
                    "data": {"files_processed": 0, "files_fixed": 0},
                    "message": "没有发现需要修复的文件"
                }
            
            # 修复所有问题文件
            self.results = []
            for file_path in problematic_files:
                result = self._fix_single_file(file_path, create_backup)
                self.results.append(result)
            
            # 统计结果
            total_files = len(self.results)
            successful_fixes = sum(1 for r in self.results if r.success)
            
            return {
                "success": successful_fixes == total_files,
                "data": {
                    "files_processed": total_files,
                    "files_fixed": successful_fixes,
                    "fix_results": self.results
                },
                "message": f"修复完成: {successful_fixes}/{total_files}个文件修复成功"
            }
            
        except Exception as e:
            error_msg = f"修复过程中发生错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "data": None,
                "message": error_msg
            }
    
    def _find_problematic_files(self, target_directory: Path) -> List[Path]:
        """
        查找有问题的Markdown文件
        
        Args:
            target_directory: 目标目录路径
            
        Returns:
            包含```markdown开头的文件列表
        """
        problematic_files = []
        
        for md_file in target_directory.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line == "```markdown":
                        problematic_files.append(md_file)
                        logger.info(f"发现问题文件: {md_file.name}")
            except Exception as e:
                logger.error(f"读取文件 {md_file} 时出错: {e}")
        
        logger.info(f"共发现 {len(problematic_files)} 个问题文件")
        return problematic_files
    
    @safe_file_operation("修复Markdown文件")
    def _fix_single_file(self, file_path: Path, create_backup: bool) -> MarkdownFixResult:
        """
        修复单个文件
        
        Args:
            file_path: 文件路径
            create_backup: 是否创建备份
            
        Returns:
            修复结果
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return MarkdownFixResult(
                    file_path=str(file_path),
                    success=False,
                    message="文件为空"
                )
            
            first_line = lines[0].strip()
            
            # 检查是否需要修复
            if first_line != "```markdown":
                return MarkdownFixResult(
                    file_path=str(file_path),
                    success=False,
                    message="文件不需要修复",
                    original_first_line=first_line
                )
            
            # 创建备份
            backup_created = False
            if create_backup:
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
                backup_created = True
                logger.info(f"已创建备份文件: {backup_path}")
            
            # 删除第一行并写回文件
            fixed_content = ''.join(lines[1:])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            logger.info(f"成功修复文件: {file_path.name}")
            return MarkdownFixResult(
                file_path=str(file_path),
                success=True,
                message="文件修复成功",
                original_first_line=first_line,
                backup_created=backup_created
            )
            
        except Exception as e:
            error_msg = f"修复文件失败: {str(e)}"
            logger.error(error_msg)
            return MarkdownFixResult(
                file_path=str(file_path),
                success=False,
                message=error_msg
            )
    
    def get_results(self) -> List[MarkdownFixResult]:
        """获取修复结果列表"""
        return self.results.copy()
    
    def generate_summary(self) -> str:
        """
        生成修复摘要报告
        
        Returns:
            修复摘要字符串
        """
        if not self.results:
            return "没有执行任何修复操作"
        
        summary = "\n=== Markdown修复结果摘要 ===\n"
        for result in self.results:
            status = "✅ 成功" if result.success else "❌ 失败"
            file_name = Path(result.file_path).name
            summary += f"{status} {file_name}: {result.message}\n"
            if result.backup_created:
                summary += f"   📁 已创建备份文件\n"
        
        return summary