#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mermaid图表中文标签修复工具

该模块提供了检测和修复Markdown文档中Mermaid代码块里中文标签未加双引号问题的功能。
主要解决的问题：
1. erDiagram关系标签中文未加双引号：ENTITY ||--o{ OTHER : 中文标签
2. 流程图箭头标签中文未加双引号：A -->|中文标签| B  
3. 流程图节点标签中文未加双引号：A[中文标签]

重构历史：
- 2025-01-05: 重构为符合KEngine项目架构规范的版本
- 添加了统一的错误处理和结构化响应格式
- 使用@safe_file_operation装饰器进行文件操作保护

作者: KEngine团队
创建时间: 2025-01-05
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from ..utils.safe_file import safe_file_operation

logger = logging.getLogger(__name__)


@dataclass
class MermaidError:
    """Mermaid错误信息数据类"""
    file_path: str
    line_number: int
    line_content: str
    error_type: str
    chinese_text: str
    suggested_fix: str
    
    def get_error_summary(self) -> str:
        """获取错误摘要信息"""
        return f"第{self.line_number}行: {self.error_type} - '{self.chinese_text}'"


@dataclass 
class FixResult:
    """修复结果数据类"""
    file_path: str
    success: bool
    message: str
    errors_found: int = 0
    errors_fixed: int = 0
    backup_created: bool = False
    
    def get_success_rate(self) -> float:
        """获取修复成功率"""
        if self.errors_found == 0:
            return 1.0
        return self.errors_fixed / self.errors_found


class MermaidChineseLabelFixerRefactored:
    """
    Mermaid中文标签修复器（重构版本）
    
    该类负责检测和修复Markdown文档中Mermaid代码块里中文标签未加双引号的问题。
    提供统一的错误处理、结构化响应格式和完整的日志记录。
    
    主要功能：
    1. 检测各种类型的Mermaid中文标签错误
    2. 自动修复这些错误
    3. 生成详细的修复报告
    4. 支持批量处理目录中的所有Markdown文件
    
    使用方法：
        fixer = MermaidChineseLabelFixerRefactored()
        result = fixer.run("./docs")
        if result["success"]:
            print(f"修复完成: {result['message']}")
        else:
            print(f"修复失败: {result['message']}")
    """
    
    def __init__(self):
        """初始化修复器"""
        self.errors: List[MermaidError] = []
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        
        # 定义各种Mermaid语法模式
        self.relationship_patterns = [
            # erDiagram关系模式：ENTITY ||--o{ OTHER : 中文标签
            re.compile(r'(\w+)\s*(\|\|--o\{|\|\|--\|\||\}o--\|\||\}o--o\{)\s*(\w+)\s*:\s*([^"\n]+[\u4e00-\u9fff][^"\n]*)\s*$'),
            # flowchart/graph箭头标签模式：A -->|中文标签| B
            re.compile(r'(\w+)\s*(-->|->|==>|==>\|)\s*\|([^|]*[\u4e00-\u9fff][^|]*)\|\s*(\w+)'),
            # 节点标签模式：A[中文标签]
            re.compile(r'(\w+)\[([^"\]]*[\u4e00-\u9fff][^"\]]*)\]'),
        ]
        
        logger.info("Mermaid中文标签修复器初始化完成")
    
    def run(self, directory_path: str, create_backup: bool = True) -> Dict[str, Any]:
        """
        运行修复工具的主入口方法
        
        Args:
            directory_path: 目标目录路径
            create_backup: 是否创建备份文件
            
        Returns:
            统一格式的响应：{"success": bool, "data": any, "message": str}
        """
        try:
            # 检测所有错误
            all_errors = self.detect_errors_in_directory(directory_path)
            
            if not all_errors:
                return {
                    "success": True,
                    "data": {"errors_found": 0, "files_processed": 0},
                    "message": "未发现任何Mermaid中文标签错误"
                }
            
            # 执行修复
            fix_results = self._fix_all_files(all_errors, create_backup)
            
            # 统计结果
            total_files = len(fix_results)
            successful_fixes = sum(1 for r in fix_results if r.success)
            total_errors_found = sum(r.errors_found for r in fix_results)
            total_errors_fixed = sum(r.errors_fixed for r in fix_results)
            
            success = successful_fixes == total_files
            
            return {
                "success": success,
                "data": {
                    "total_files": total_files,
                    "successful_fixes": successful_fixes,
                    "total_errors_found": total_errors_found,
                    "total_errors_fixed": total_errors_fixed,
                    "fix_results": fix_results
                },
                "message": f"处理完成: {successful_fixes}/{total_files}个文件修复成功，共修复{total_errors_fixed}/{total_errors_found}个错误"
            }
            
        except Exception as e:
            error_msg = f"修复过程中发生错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "data": None,
                "message": error_msg
            }
    
    @safe_file_operation("检测Mermaid错误")
    def detect_errors_in_file(self, file_path: str) -> List[MermaidError]:
        """
        检测单个文件中的Mermaid中文标签错误
        
        Args:
            file_path: 文件路径
            
        Returns:
            错误列表
        """
        errors = []
        file_path_obj = Path(file_path)
        
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        in_mermaid_block = False
        mermaid_type = None
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # 检测mermaid代码块开始
            if line_stripped.startswith('```mermaid'):
                in_mermaid_block = True
                mermaid_type = None
                continue
            
            # 检测mermaid代码块结束
            if line_stripped == '```' and in_mermaid_block:
                in_mermaid_block = False
                mermaid_type = None
                continue
            
            # 在mermaid代码块内检测错误
            if in_mermaid_block:
                # 确定mermaid图表类型
                if mermaid_type is None:
                    if any(keyword in line_stripped for keyword in ['erDiagram', 'graph', 'flowchart', 'sequenceDiagram']):
                        mermaid_type = line_stripped.split()[0] if line_stripped.split() else 'unknown'
                    continue
                
                # 检测各种模式的中文标签错误
                detected_error = self._detect_line_errors(line, line_num, file_path, mermaid_type)
                if detected_error:
                    errors.append(detected_error)
        
        if errors:
            logger.info(f"在文件 {file_path} 中发现 {len(errors)} 个Mermaid中文标签错误")
        
        return errors
    
    def detect_errors_in_directory(self, directory_path: str) -> List[MermaidError]:
        """
        检测目录中所有Markdown文件的Mermaid中文标签错误
        
        Args:
            directory_path: 目录路径
            
        Returns:
            所有错误列表
        """
        all_errors = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        # 递归查找所有.md文件
        md_files = list(directory.rglob("*.md"))
        logger.info(f"在目录 {directory_path} 中找到 {len(md_files)} 个Markdown文件")
        
        for md_file in md_files:
            try:
                file_errors = self.detect_errors_in_file(str(md_file))
                all_errors.extend(file_errors)
            except Exception as e:
                logger.error(f"处理文件 {md_file} 时发生错误: {str(e)}")
        
        self.errors = all_errors
        logger.info(f"总共发现 {len(all_errors)} 个Mermaid中文标签错误")
        return all_errors
    
    def _detect_line_errors(self, line: str, line_num: int, file_path: str, mermaid_type: Optional[str]) -> Optional[MermaidError]:
        """
        检测单行中的错误
        
        Args:
            line: 代码行内容
            line_num: 行号
            file_path: 文件路径
            mermaid_type: Mermaid图表类型
            
        Returns:
            检测到的错误，如果没有错误则返回None
        """
        for pattern in self.relationship_patterns:
            match = pattern.search(line)
            if match:
                chinese_text = None
                error_type = None
                suggested_fix = line
                
                if mermaid_type and 'erDiagram' in mermaid_type:
                    # erDiagram关系标签
                    if len(match.groups()) >= 4:
                        chinese_text = match.group(4).strip()
                        if self._needs_quotes(chinese_text):
                            error_type = "erDiagram关系标签未加双引号"
                            suggested_fix = line.replace(f': {chinese_text}', f': "{chinese_text}"')
                
                elif mermaid_type and any(graph_type in mermaid_type for graph_type in ['graph', 'flowchart']):
                    # 流程图箭头标签或节点标签
                    if '|' in line and len(match.groups()) >= 3:
                        chinese_text = match.group(3).strip()
                        if self._needs_quotes(chinese_text):
                            error_type = "流程图箭头标签未加双引号"
                            suggested_fix = line.replace(f'|{chinese_text}|', f'|"{chinese_text}"|')
                    elif '[' in line and len(match.groups()) >= 2:
                        chinese_text = match.group(2).strip()
                        if self._needs_quotes(chinese_text):
                            error_type = "流程图节点标签未加双引号"
                            suggested_fix = line.replace(f'[{chinese_text}]', f'["{chinese_text}"]')
                
                if chinese_text and error_type:
                    return MermaidError(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.rstrip(),
                        error_type=error_type,
                        chinese_text=chinese_text,
                        suggested_fix=suggested_fix.rstrip()
                    )
        
        return None
    
    def _needs_quotes(self, text: str) -> bool:
        """
        判断文本是否需要添加双引号
        
        Args:
            text: 要检查的文本
            
        Returns:
            如果包含中文且未加双引号则返回True
        """
        return (self.chinese_pattern.search(text) is not None and 
                not (text.startswith('"') and text.endswith('"')))
    
    def _fix_all_files(self, all_errors: List[MermaidError], create_backup: bool) -> List[FixResult]:
        """
        修复所有包含错误的文件
        
        Args:
            all_errors: 所有错误列表
            create_backup: 是否创建备份
            
        Returns:
            修复结果列表
        """
        # 按文件分组错误
        files_errors = {}
        for error in all_errors:
            if error.file_path not in files_errors:
                files_errors[error.file_path] = []
            files_errors[error.file_path].append(error)
        
        fix_results = []
        for file_path, file_errors in files_errors.items():
            result = self._fix_single_file(file_path, file_errors, create_backup)
            fix_results.append(result)
        
        return fix_results
    
    @safe_file_operation("修复Mermaid文件")
    def _fix_single_file(self, file_path: str, file_errors: List[MermaidError], create_backup: bool) -> FixResult:
        """
        修复单个文件
        
        Args:
            file_path: 文件路径
            file_errors: 该文件的错误列表
            create_backup: 是否创建备份
            
        Returns:
            修复结果
        """
        file_path_obj = Path(file_path)
        
        try:
            # 创建备份
            backup_created = False
            if create_backup:
                backup_path = file_path_obj.with_suffix(f"{file_path_obj.suffix}.backup")
                backup_path.write_text(file_path_obj.read_text(encoding='utf-8'), encoding='utf-8')
                backup_created = True
                logger.info(f"已创建备份文件: {backup_path}")
            
            # 读取原文件
            content = file_path_obj.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 按行号倒序排列，避免修复时行号变化
            file_errors.sort(key=lambda x: x.line_number, reverse=True)
            
            fixed_count = 0
            for error in file_errors:
                line_index = error.line_number - 1
                if 0 <= line_index < len(lines):
                    old_line = lines[line_index]
                    if old_line.strip() == error.line_content.strip():
                        lines[line_index] = error.suggested_fix
                        fixed_count += 1
                        logger.debug(f"已修复第 {error.line_number} 行: {error.chinese_text}")
            
            # 写回文件
            if fixed_count > 0:
                file_path_obj.write_text('\n'.join(lines), encoding='utf-8')
                logger.info(f"文件 {file_path} 修复完成，共修复 {fixed_count} 个错误")
            
            return FixResult(
                file_path=file_path,
                success=True,
                message=f"修复成功，共修复 {fixed_count}/{len(file_errors)} 个错误",
                errors_found=len(file_errors),
                errors_fixed=fixed_count,
                backup_created=backup_created
            )
            
        except Exception as e:
            error_msg = f"修复文件失败: {str(e)}"
            logger.error(error_msg)
            return FixResult(
                file_path=file_path,
                success=False,
                message=error_msg,
                errors_found=len(file_errors),
                errors_fixed=0,
                backup_created=False
            )
    
    def generate_report(self) -> str:
        """
        生成错误报告
        
        Returns:
            错误报告字符串
        """
        if not self.errors:
            return "✅ 未发现Mermaid中文标签错误！"
        
        report = f"🔍 Mermaid中文标签错误检测报告\n"
        report += f"=" * 50 + "\n"
        report += f"总计发现 {len(self.errors)} 个错误\n\n"
        
        # 按文件分组
        files_errors = {}
        for error in self.errors:
            if error.file_path not in files_errors:
                files_errors[error.file_path] = []
            files_errors[error.file_path].append(error)
        
        for file_path, file_errors in files_errors.items():
            report += f"📁 文件: {Path(file_path).name}\n"
            report += f"   路径: {file_path}\n"
            report += f"   错误数量: {len(file_errors)}\n"
            
            for error in file_errors:
                report += f"   ❌ {error.get_error_summary()}\n"
                report += f"      原始行: {error.line_content.strip()}\n"
                report += f"      建议修复: {error.suggested_fix.strip()}\n"
                report += f"   {'-' * 40}\n"
            report += "\n"
        
        return report
    
    def get_errors(self) -> List[MermaidError]:
        """获取检测到的错误列表"""
        return self.errors.copy()