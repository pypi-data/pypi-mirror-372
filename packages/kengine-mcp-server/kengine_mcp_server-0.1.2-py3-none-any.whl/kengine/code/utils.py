"""
代码骨架提取通用工具函数
只包含真正通用的工具函数，语言特定逻辑已移到各语言处理器中
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from tree_sitter import Query, QueryCursor
except ImportError:
    Query = None
    QueryCursor = None


def read_file_content(file_path: Path) -> str:
    """读取文件内容，支持多种编码"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()


def format_type_annotation(text: str) -> str:
    """格式化类型注解，确保符合PEP 8规范"""
    import re
    
    # 修复Python类型注解格式：确保冒号后有空格
    # 处理参数类型注解：param: type
    text = re.sub(r':\s*([^,):\s]+)', r': \1', text)
    # 处理返回类型注解：) -> type:
    text = re.sub(r'\)\s*->\s*([^:]+)\s*:', r') -> \1:', text)
    
    return text


def clean_whitespace(text: str) -> str:
    """清理多余的空白字符"""
    import re
    
    # 清理多余的空格，但保持基本结构
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*\(\s*', '(', text)
    text = re.sub(r'\s*\)\s*', ')', text)
    text = re.sub(r'\s*,\s*', ', ', text)
    
    return text.strip()


def extract_node_text(node, encoding='utf-8') -> str:
    """提取AST节点的文本内容"""
    try:
        if hasattr(node, 'text'):
            if hasattr(node.text, 'decode'):
                return node.text.decode(encoding)
            else:
                return str(node.text)
        return ""
    except Exception as e:
        logger.error(f"提取节点文本时发生错误: {e}")
        return ""


def safe_get_line(lines: list, line_number: int, default: str = "") -> str:
    """安全地获取指定行号的内容"""
    try:
        if 0 <= line_number < len(lines):
            return lines[line_number]
        return default
    except Exception:
        return default


def find_matching_brace(text: str, start_pos: int = 0) -> int:
    """查找匹配的大括号位置"""
    try:
        brace_count = 0
        in_string = False
        string_char = None
        
        for i, char in enumerate(text[start_pos:], start_pos):
            # 处理字符串
            if char in ['"', "'"] and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                # 检查是否是转义字符
                if i == 0 or text[i-1] != '\\':
                    in_string = False
                    string_char = None
            
            # 如果不在字符串中，计算括号
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return i
        
        return -1  # 没有找到匹配的括号
    except Exception:
        return -1


def truncate_with_ellipsis(text: str, max_length: int = 100) -> str:
    """截断文本并添加省略号"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def is_valid_identifier(name: str) -> bool:
    """检查是否是有效的标识符"""
    import re
    # 简单的标识符检查：字母开头，包含字母、数字、下划线
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))


def normalize_line_endings(text: str) -> str:
    """标准化行结束符"""
    return text.replace('\r\n', '\n').replace('\r', '\n')


def count_leading_spaces(line: str) -> int:
    """计算行首的空格数量"""
    return len(line) - len(line.lstrip(' '))


def get_indentation_level(line: str, tab_size: int = 4) -> int:
    """获取缩进级别"""
    spaces = count_leading_spaces(line)
    tabs = len(line) - len(line.lstrip('\t'))
    return spaces + (tabs * tab_size)