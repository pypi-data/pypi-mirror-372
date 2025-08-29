"""
文本搜索工具模块

包含 TextGrepTool 类，提供基于关键字的文本块搜索功能，使用统一的错误处理机制。
"""

import json
import os
import re
from pathlib import Path
import sys
from typing import List, Dict, Any, Union, Optional, Tuple

sys.path.append('.')

from kengine.agent.shared.tools.base import BasePathTool
from kengine.agent.shared.tools.exceptions import SearchError, FileOperationError
from kengine.agent.shared.tools.error_handler import ErrorHandler, handle_tool_errors, safe_execute
from kengine.agent.shared.decorators import prevent_duplicate_calls


class TextGrepTool(BasePathTool):
    """文本搜索工具
    
    根据关键字搜索对应的文本块，智能提取完整的代码块。
    功能类似于bash的grep命令的增强版本。
    
    功能特性：
    - 支持多种编程语言文件的文本搜索
    - 智能提取完整的方法、函数或字段定义（包含注释）
    - 如果在方法中，返回整个方法内容
    - 如果是属性字段，返回字段行及其注释行
    - 压缩文本，去掉空行但保留注释
    - 按特定顺序排序和过滤结果
    - 优先返回controller、AppService、service等文件
    - 返回前10个结果
    - 支持Java、Python、JavaScript、TypeScript、C++、Go等语言
    - 英文搜索时自动忽略大小写
    """
    
    def __init__(self, base_dir: str):
        """
        初始化文本搜索工具
        
        Args:
            base_dir: 基础目录路径
        """
        super().__init__(base_dir)
        self.error_handler = ErrorHandler()
        self.max_results = 10
        self.context_lines = 10  # 关键字前后10行
        self.priority_patterns = [
            r'.*Controller\.java$',
            r'.*\.AppService.*\.java$',
            r'.*service.*\.java$'
        ]
        # 默认搜索的文件模式
        self.default_file_patterns = [
            "**/*.java", "**/*.py", "**/*.js", "**/*.ts", 
            "**/*.cpp", "**/*.cc", "**/*.cxx", "**/*.c",
            "**/*.cs", "**/*.go", "**/*.php", "**/*.rb"
        ]
    
    def search_text_blocks(self, keyword: str) -> Dict[str, Any]:
        """
        搜索文本块（新的推荐接口）- 返回结构化响应
        
        Args:
            keyword: 搜索关键字
            
        Returns:
            包含搜索结果或错误信息的字典
        """
        return safe_execute(
            self._search_text_blocks_internal,
            tool_name="TextGrepTool",
            operation="search_text_blocks",
            keyword=keyword
        )
    
    def _search_text_blocks_internal(self, keyword: str) -> List[Dict[str, Any]]:
        """
        内部文本块搜索实现
        
        Args:
            keyword: 搜索关键字
            
        Returns:
            包含搜索结果的字典列表
            
        Raises:
            SearchError: 搜索失败
        """
        if not keyword or not keyword.strip():
            raise SearchError(
                "搜索关键字不能为空",
                pattern=keyword,
                tool_name=self.__class__.__name__
            )
        
        keyword = keyword.strip()
        
        # 获取要搜索的文件列表
        files_to_search = self._get_files_to_search()
        
        # 执行搜索
        search_results = []
        for file_path in files_to_search:
            try:
                file_results = self._search_in_file(file_path, keyword)
                search_results.extend(file_results)
            except Exception as e:
                # 记录错误但继续搜索其他文件
                self.error_handler.logger.warning(f"搜索文件 {file_path} 时出错: {str(e)}")
                continue
        
        # 按优先级排序和过滤结果
        sorted_results = self._sort_and_filter_results(search_results)
        
        # 限制结果数量
        return sorted_results[:self.max_results]
    
    def _get_files_to_search(self) -> List[Path]:
        """
        获取要搜索的文件列表
        
        Returns:
            文件路径列表
        """
        files = []
        
        for pattern in self.default_file_patterns:
            try:
                # 构建完整的搜索模式
                full_pattern = str(self.base_dir / pattern)
                matching_files = list(Path(self.base_dir).glob(pattern))
                
                for file_path in matching_files:
                    if file_path.is_file() and self._is_readable_file(file_path):
                        files.append(file_path)
            except Exception as e:
                self.error_handler.logger.warning(f"处理文件模式 {pattern} 时出错: {str(e)}")
                continue
        
        return files
    
    def _is_readable_file(self, file_path: Path) -> bool:
        """
        检查文件是否可读
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否可读
        """
        try:
            # 检查文件大小（避免读取过大的文件）
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                return False
            
            # 检查文件扩展名
            supported_extensions = {
                '.java', '.py', '.js', '.ts', '.cpp', '.cc', '.cxx', 
                '.c', '.cs', '.go', '.php', '.rb', '.xml', '.yml', 
                '.yaml', '.json', '.md', '.txt'
            }
            
            return file_path.suffix.lower() in supported_extensions
        except Exception:
            return False
    
    def _search_in_file(self, file_path: Path, keyword: str) -> List[Dict[str, Any]]:
        """
        在单个文件中搜索关键字
        
        Args:
            file_path: 文件路径
            keyword: 搜索关键字
            
        Returns:
            搜索结果列表
        """
        results = []
        
        try:
            # 读取文件内容
            content = self._read_file_content(file_path)
            if not content:
                return results
            
            lines = content.splitlines()
            
            # 判断是否为英文搜索（包含英文字母）
            is_english_search = bool(re.search(r'[a-zA-Z]', keyword))
            
            # 搜索包含关键字的行
            for line_num, line in enumerate(lines, 1):
                # 英文搜索时忽略大小写，中文搜索时保持原样
                if is_english_search:
                    if keyword.lower() in line.lower():
                        # 提取代码块
                        code_block = self._extract_code_block(lines, line_num, file_path)
                        
                        if code_block:
                            result = {
                                "file_path": str(file_path),
                                "relative_path": self._get_relative_path(file_path),
                                "keyword": keyword,
                                "matched_line": line_num,
                                "start_line": code_block["start_line"],
                                "end_line": code_block["end_line"],
                                "code_block": code_block["content"],
                                "priority_score": self._calculate_priority_score(file_path),
                                "case_insensitive": True
                            }
                            results.append(result)
                else:
                    # 中文搜索保持原样
                    if keyword in line:
                        # 提取代码块
                        code_block = self._extract_code_block(lines, line_num, file_path)
                        
                        if code_block:
                            result = {
                                "file_path": str(file_path),
                                "relative_path": self._get_relative_path(file_path),
                                "keyword": keyword,
                                "matched_line": line_num,
                                "start_line": code_block["start_line"],
                                "end_line": code_block["end_line"],
                                "code_block": code_block["content"],
                                "priority_score": self._calculate_priority_score(file_path),
                                "case_insensitive": False
                            }
                            results.append(result)
            
        except Exception as e:
            self.error_handler.logger.warning(f"搜索文件 {file_path} 时出错: {str(e)}")
        
        return results
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容或None
        """
        try:
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    return file_path.read_text(encoding=encoding)
                except UnicodeDecodeError:
                    continue
            
            return None
        except Exception:
            return None
    
    def _extract_code_block(self, lines: List[str], matched_line: int, file_path: Path = None) -> Optional[Dict[str, Any]]:
        """
        智能提取代码块
        
        根据关键字所在位置智能提取完整的代码块：
        - 如果在方法中，返回整个方法内容（包含注释）
        - 如果是属性字段，返回字段行及其注释行
        - 压缩文本，去掉空行
        
        Args:
            lines: 文件的所有行
            matched_line: 匹配行的行号
            file_path: 文件路径，用于确定文件类型
            
        Returns:
            代码块信息或None
        """
        try:
            # 确定文件类型
            file_ext = file_path.suffix.lower() if file_path else ""
            
            # 尝试智能提取代码块
            smart_block = self._extract_smart_code_block(lines, matched_line, file_ext)
            if smart_block:
                return smart_block
            
            # 如果智能提取失败，回退到原来的简单提取
            return self._extract_simple_code_block(lines, matched_line)
            
        except Exception:
            return self._extract_simple_code_block(lines, matched_line)
    
    def _extract_smart_code_block(self, lines: List[str], matched_line: int, file_ext: str) -> Optional[Dict[str, Any]]:
        """
        智能提取代码块
        
        Args:
            lines: 文件的所有行
            matched_line: 匹配行的行号
            file_ext: 文件扩展名
            
        Returns:
            代码块信息或None
        """
        if file_ext in ['.java', '.cs']:
            return self._extract_java_csharp_block(lines, matched_line)
        elif file_ext in ['.py']:
            return self._extract_python_block(lines, matched_line)
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            return self._extract_javascript_block(lines, matched_line)
        elif file_ext in ['.cpp', '.cc', '.cxx', '.c', '.h', '.hpp']:
            return self._extract_cpp_block(lines, matched_line)
        elif file_ext in ['.go']:
            return self._extract_go_block(lines, matched_line)
        else:
            return None
    
    def _extract_java_csharp_block(self, lines: List[str], matched_line: int) -> Optional[Dict[str, Any]]:
        """
        提取Java/C#代码块
        
        Args:
            lines: 文件的所有行
            matched_line: 匹配行的行号
            
        Returns:
            代码块信息或None
        """
        # 向前查找方法开始或字段定义
        start_line = matched_line
        end_line = matched_line
        
        # 向前查找方法开始或字段定义
        for i in range(matched_line - 1, 0, -1):
            line = lines[i - 1].strip()
            
            # 跳过空行和注释
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                continue
            
            # 检查是否是方法开始
            if (re.match(r'^\s*(public|private|protected|static|\s)*\s*\w+\s+\w+\s*\([^)]*\)\s*{?$', line) or
                re.match(r'^\s*(public|private|protected|static|\s)*\s*void\s+\w+\s*\([^)]*\)\s*{?$', line) or
                re.match(r'^\s*(public|private|protected|static|\s)*\s*<.*>\s*\w+\s+\w+\s*\([^)]*\)\s*{?$', line) or
                re.match(r'^\s*(public|private|protected|static|\s)*\s*\w+\s+\w+\s*\([^)]*\)\s*throws\s+\w+\s*{?$', line)):
                start_line = i
                break
            
            # 检查是否是字段定义
            if re.match(r'^\s*(public|private|protected|static|final|\s)*\s*\w+\s+\w+\s*[;=]', line):
                start_line = i
                break
            
            # 检查是否是类定义
            if re.match(r'^\s*(public|private|protected|\s)*\s*class\s+\w+', line):
                start_line = i
                break
        
        # 向后查找方法结束
        brace_count = 0
        in_method = False
        found_opening_brace = False
        
        for i in range(start_line, len(lines) + 1):
            line = lines[i - 1].strip()
            
            # 检查是否进入方法体
            if '{' in line:
                found_opening_brace = True
                in_method = True
            
            # 计算大括号
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
            
            # 如果在方法中且大括号平衡，找到方法结束
            if in_method and found_opening_brace and brace_count == 0:
                end_line = i
                break
            
            # 如果是字段定义，找到分号结束
            if not in_method and line.endswith(';'):
                end_line = i
                break
        
        # 如果没找到结束，使用默认范围
        if end_line == matched_line:
            end_line = min(len(lines), matched_line + 20)
        
        # 提取代码块并压缩
        code_lines = lines[start_line - 1:end_line]
        compressed_lines = self._compress_code_lines(code_lines)
        
        return {
            "start_line": start_line,
            "end_line": end_line,
            "content": "\n".join(compressed_lines)
        }
    
    def _extract_python_block(self, lines: List[str], matched_line: int) -> Optional[Dict[str, Any]]:
        """
        提取Python代码块
        
        Args:
            lines: 文件的所有行
            matched_line: 匹配行的行号
            
        Returns:
            代码块信息或None
        """
        # 向前查找函数或类定义
        start_line = matched_line
        end_line = matched_line
        
        # 向前查找函数或类开始
        for i in range(matched_line - 1, 0, -1):
            line = lines[i - 1].strip()
            
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue
            
            # 检查是否是函数定义
            if re.match(r'^\s*def\s+\w+\s*\(', line):
                start_line = i
                break
            
            # 检查是否是类定义
            if re.match(r'^\s*class\s+\w+', line):
                start_line = i
                break
            
            # 检查是否是变量赋值
            if re.match(r'^\s*\w+\s*=', line):
                start_line = i
                break
        
        # 向后查找函数或类结束
        indent_level = None
        base_indent = None
        
        for i in range(start_line, len(lines) + 1):
            line = lines[i - 1]
            
            # 获取当前行的缩进级别
            current_indent = len(line) - len(line.lstrip())
            
            # 设置基准缩进级别（第一行非空行的缩进）
            if base_indent is None and line.strip():
                base_indent = current_indent
            
            # 如果缩进级别小于等于基准且不是空行，说明函数或类结束
            if (base_indent is not None and line.strip() and 
                current_indent <= base_indent and i > start_line):
                end_line = i - 1
                break
        
        # 如果没找到结束，使用默认范围
        if end_line == matched_line:
            end_line = min(len(lines), matched_line + 20)
        
        # 提取代码块并压缩
        code_lines = lines[start_line - 1:end_line]
        compressed_lines = self._compress_code_lines(code_lines)
        
        return {
            "start_line": start_line,
            "end_line": end_line,
            "content": "\n".join(compressed_lines)
        }
    
    def _extract_javascript_block(self, lines: List[str], matched_line: int) -> Optional[Dict[str, Any]]:
        """
        提取JavaScript/TypeScript代码块
        
        Args:
            lines: 文件的所有行
            matched_line: 匹配行的行号
            
        Returns:
            代码块信息或None
        """
        # 向前查找函数或方法定义
        start_line = matched_line
        end_line = matched_line
        
        # 向前查找函数或方法开始
        for i in range(matched_line - 1, 0, -1):
            line = lines[i - 1].strip()
            
            # 跳过空行和注释
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                continue
            
            # 检查是否是函数定义
            if (re.match(r'^\s*(export\s+)?(function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\(|var\s+\w+\s*=\s*\()', line) or
                re.match(r'^\s*\w+\s*\([^)]*\)\s*{', line) or
                re.match(r'^\s*\w+\s*:\s*function\s*\(', line)):
                start_line = i
                break
            
            # 检查是否是类定义
            if re.match(r'^\s*(export\s+)?class\s+\w+', line):
                start_line = i
                break
            
            # 检查是否是变量定义
            if re.match(r'^\s*(const|let|var)\s+\w+', line):
                start_line = i
                break
        
        # 向后查找函数或方法结束
        brace_count = 0
        in_function = False
        
        for i in range(start_line, len(lines) + 1):
            line = lines[i - 1].strip()
            
            # 检查是否进入函数体
            if i == start_line and '{' in line:
                in_function = True
            
            # 计算大括号
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
            
            # 如果在函数中且大括号平衡，找到函数结束
            if in_function and brace_count == 0:
                end_line = i
                break
            
            # 如果是变量定义，找到分号结束
            if not in_function and line.endswith(';'):
                end_line = i
                break
        
        # 如果没找到结束，使用默认范围
        if end_line == matched_line:
            end_line = min(len(lines), matched_line + 20)
        
        # 提取代码块并压缩
        code_lines = lines[start_line - 1:end_line]
        compressed_lines = self._compress_code_lines(code_lines)
        
        return {
            "start_line": start_line,
            "end_line": end_line,
            "content": "\n".join(compressed_lines)
        }
    
    def _extract_cpp_block(self, lines: List[str], matched_line: int) -> Optional[Dict[str, Any]]:
        """
        提取C++代码块
        
        Args:
            lines: 文件的所有行
            matched_line: 匹配行的行号
            
        Returns:
            代码块信息或None
        """
        # 向前查找函数或方法定义
        start_line = matched_line
        end_line = matched_line
        
        # 向前查找函数或方法开始
        for i in range(matched_line - 1, 0, -1):
            line = lines[i - 1].strip()
            
            # 跳过空行和注释
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                continue
            
            # 检查是否是函数定义
            if re.match(r'^\s*\w+\s+\w+\s*\([^)]*\)\s*{?$', line) or re.match(r'^\s*\w+\s+\w+::\w+\s*\([^)]*\)\s*{?$', line):
                start_line = i
                break
            
            # 检查是否是类定义
            if re.match(r'^\s*class\s+\w+', line):
                start_line = i
                break
            
            # 检查是否是变量定义
            if re.match(r'^\s*\w+\s+\w+\s*[;=]', line):
                start_line = i
                break
        
        # 向后查找函数或方法结束
        brace_count = 0
        in_function = False
        
        for i in range(start_line, len(lines) + 1):
            line = lines[i - 1].strip()
            
            # 检查是否进入函数体
            if i == start_line and '{' in line:
                in_function = True
            
            # 计算大括号
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
            
            # 如果在函数中且大括号平衡，找到函数结束
            if in_function and brace_count == 0:
                end_line = i
                break
            
            # 如果是变量定义，找到分号结束
            if not in_function and line.endswith(';'):
                end_line = i
                break
        
        # 如果没找到结束，使用默认范围
        if end_line == matched_line:
            end_line = min(len(lines), matched_line + 20)
        
        # 提取代码块并压缩
        code_lines = lines[start_line - 1:end_line]
        compressed_lines = self._compress_code_lines(code_lines)
        
        return {
            "start_line": start_line,
            "end_line": end_line,
            "content": "\n".join(compressed_lines)
        }
    
    def _extract_go_block(self, lines: List[str], matched_line: int) -> Optional[Dict[str, Any]]:
        """
        提取Go代码块
        
        Args:
            lines: 文件的所有行
            matched_line: 匹配行的行号
            
        Returns:
            代码块信息或None
        """
        # 向前查找函数或方法定义
        start_line = matched_line
        end_line = matched_line
        
        # 向前查找函数或方法开始
        for i in range(matched_line - 1, 0, -1):
            line = lines[i - 1].strip()
            
            # 跳过空行和注释
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                continue
            
            # 检查是否是函数定义
            if re.match(r'^\s*func\s+\w+', line):
                start_line = i
                break
            
            # 检查是否是结构体定义
            if re.match(r'^\s*type\s+\w+\s+struct', line):
                start_line = i
                break
            
            # 检查是否是变量定义
            if re.match(r'^\s*var\s+\w+', line):
                start_line = i
                break
        
        # 向后查找函数或方法结束
        brace_count = 0
        in_function = False
        
        for i in range(start_line, len(lines) + 1):
            line = lines[i - 1].strip()
            
            # 检查是否进入函数体
            if i == start_line and '{' in line:
                in_function = True
            
            # 计算大括号
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
            
            # 如果在函数中且大括号平衡，找到函数结束
            if in_function and brace_count == 0:
                end_line = i
                break
            
            # 如果是变量定义，找到结束
            if not in_function and (line.endswith('}') or line.endswith(')')):
                end_line = i
                break
        
        # 如果没找到结束，使用默认范围
        if end_line == matched_line:
            end_line = min(len(lines), matched_line + 20)
        
        # 提取代码块并压缩
        code_lines = lines[start_line - 1:end_line]
        compressed_lines = self._compress_code_lines(code_lines)
        
        return {
            "start_line": start_line,
            "end_line": end_line,
            "content": "\n".join(compressed_lines)
        }
    
    def _extract_simple_code_block(self, lines: List[str], matched_line: int) -> Optional[Dict[str, Any]]:
        """
        简单提取代码块（原来的逻辑）
        
        Args:
            lines: 文件的所有行
            matched_line: 匹配行的行号
            
        Returns:
            代码块信息或None
        """
        try:
            # 计算起始和结束行号
            start_line = max(1, matched_line - self.context_lines)
            end_line = min(len(lines), matched_line + self.context_lines)
            
            # 提取代码块内容
            code_lines = lines[start_line - 1:end_line]
            
            # 压缩代码行
            compressed_lines = self._compress_code_lines(code_lines)
            
            if not compressed_lines:
                return None
            
            return {
                "start_line": start_line,
                "end_line": end_line,
                "content": "\n".join(compressed_lines)
            }
            
        except Exception:
            return None
    
    def _compress_code_lines(self, lines: List[str]) -> List[str]:
        """
        压缩代码行，去除空行但保留注释
        
        Args:
            lines: 原始代码行列表
            
        Returns:
            压缩后的代码行列表
        """
        compressed = []
        for line in lines:
            stripped = line.rstrip()
            # 保留非空行和注释行
            if stripped or any(stripped.startswith(comment) for comment in ['//', '/*', '*', '#', '<!--']):
                compressed.append(stripped)
        
        return compressed
    
    def _calculate_priority_score(self, file_path: Path) -> int:
        """
        计算文件优先级分数
        
        Args:
            file_path: 文件路径
            
        Returns:
            优先级分数（越高越优先）
        """
        file_name = str(file_path).lower()
        
        # 检查优先级模式
        for i, pattern in enumerate(self.priority_patterns):
            if re.match(pattern, file_name):
                return len(self.priority_patterns) - i  # 越靠前的模式分数越高
        
        return 0
    
    def _sort_and_filter_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        排序和过滤搜索结果
        
        Args:
            results: 原始搜索结果
            
        Returns:
            排序后的结果
        """
        # 按优先级分数降序排序
        sorted_results = sorted(results, key=lambda x: x.get("priority_score", 0), reverse=True)
        
        # 去重（基于文件路径和行号）
        seen = set()
        unique_results = []
        
        for result in sorted_results:
            key = (result["file_path"], result["matched_line"])
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results
    
    @prevent_duplicate_calls(ttl=300)
    @handle_tool_errors(tool_name="TextGrepTool", operation="search", return_format="json")
    def run(self, keyword: str) -> Union[str, Dict[str, Any]]:
        """
        搜索文本块（保持向后兼容的接口）- 可返回JSON格式错误
        
        Args:
            keyword: 搜索关键字，支持JSON格式参数
            
        Returns:
            JSON字符串格式的搜索结果或错误信息
        """
        # 处理JSON格式参数
        if isinstance(keyword, str):
            keyword = keyword.strip()
            if keyword.startswith('{') and keyword.endswith('}'):
                try:
                    params = json.loads(keyword)
                    real_keyword = params.get('keyword', None)
                    
                    if not real_keyword:
                        raise SearchError(
                            "JSON参数中缺少keyword字段",
                            pattern=keyword,
                            tool_name=self.__class__.__name__
                        )
                    
                    return self.run(real_keyword)
                    
                except json.JSONDecodeError as e:
                    raise SearchError(
                        f"JSON参数解析失败: {str(e)}",
                        pattern=keyword,
                        tool_name=self.__class__.__name__
                    ) from e
        
        # 执行搜索
        results = self._search_text_blocks_internal(keyword)
        
        # 返回JSON格式
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    def set_search_parameters(self, max_results: Optional[int] = None, 
                            context_lines: Optional[int] = None) -> Dict[str, Any]:
        """
        设置搜索参数 - 返回结构化响应
        
        Args:
            max_results: 最大结果数量
            context_lines: 上下文行数
            
        Returns:
            操作结果字典
        """
        try:
            old_params = {
                "max_results": self.max_results,
                "context_lines": self.context_lines
            }
            
            changes = []
            
            if max_results is not None and max_results > 0:
                self.max_results = max_results
                changes.append(f"max_results: {old_params['max_results']} -> {max_results}")
            
            if context_lines is not None and context_lines >= 0:
                self.context_lines = context_lines
                changes.append(f"context_lines: {old_params['context_lines']} -> {context_lines}")
            
            new_params = {
                "max_results": self.max_results,
                "context_lines": self.context_lines
            }
            
            return self.error_handler.format_success_response(
                data={
                    "old_parameters": old_params,
                    "new_parameters": new_params,
                    "changes": changes
                },
                message=f"搜索参数已更新，共 {len(changes)} 项变更",
                tool_name="TextGrepTool",
                operation="set_search_parameters"
            )
        except Exception as e:
            return self.error_handler.format_error_response(
                e,
                tool_name="TextGrepTool",
                operation="set_search_parameters"
            )
    
    def get_search_statistics(self, keyword: str) -> Dict[str, Any]:
        """
        获取搜索统计信息 - 返回结构化响应
        
        Args:
            keyword: 搜索关键字
            
        Returns:
            包含搜索统计信息的字典
        """
        return safe_execute(
            self._get_search_statistics_internal,
            tool_name="TextGrepTool",
            operation="get_statistics",
            keyword=keyword
        )
    
    def _get_search_statistics_internal(self, keyword: str) -> Dict[str, Any]:
        """
        内部获取搜索统计信息方法
        
        Args:
            keyword: 搜索关键字
            
        Returns:
            包含搜索统计信息的字典
        """
        if not keyword or not keyword.strip():
            raise SearchError(
                "搜索关键字不能为空",
                pattern=keyword,
                tool_name=self.__class__.__name__
            )
        
        # 获取要搜索的文件列表
        files_to_search = self._get_files_to_search()
        
        # 统计信息
        total_files = len(files_to_search)
        total_matches = 0
        file_matches = 0
        
        # 判断是否为英文搜索
        is_english_search = bool(re.search(r'[a-zA-Z]', keyword))
        
        # 执行搜索统计
        for file_path in files_to_search:
            try:
                content = self._read_file_content(file_path)
                if content:
                    lines = content.splitlines()
                    if is_english_search:
                        file_match_count = sum(1 for line in lines if keyword.lower() in line.lower())
                    else:
                        file_match_count = sum(1 for line in lines if keyword in line)
                    if file_match_count > 0:
                        file_matches += 1
                        total_matches += file_match_count
            except Exception:
                continue
        
        return {
            "keyword": keyword,
            "total_files_searched": total_files,
            "files_with_matches": file_matches,
            "total_matches": total_matches,
            "max_results_limit": self.max_results,
            "context_lines": self.context_lines,
            "priority_patterns": self.priority_patterns,
            "case_insensitive": is_english_search
        }
