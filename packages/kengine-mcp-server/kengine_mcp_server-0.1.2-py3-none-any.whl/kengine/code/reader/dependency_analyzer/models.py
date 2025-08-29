"""
基于 tree-sitter 的方法引用分析数据模型
定义方法引用分析过程中使用的数据结构，包括变量信息、方法调用信息和分析结果。
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
class VariableScope(Enum):
    """变量作用域枚举"""
    LOCAL = "local"           # 局部变量
    PARAMETER = "parameter"   # 方法参数
    FIELD = "field"          # 类字段
    STATIC_FIELD = "static_field"  # 静态字段
@dataclass
class VariableInfo:
    """变量信息"""
    name: str                    # 变量名
    type_name: str              # 变量类型名
    full_type_name: str         # 完整类型名（包含包名）
    scope: VariableScope        # 变量作用域
    declaration_line: int       # 声明行号
    declaration_column: int     # 声明列号
    
    def __str__(self) -> str:
        return f"{self.type_name} {self.name} (line {self.declaration_line})"
@dataclass
class MethodCallInfo:
    """方法调用信息"""
    caller_method_name: str     # 调用者方法名
    caller_method_line: int     # 调用者方法所在行号
    call_line: int             # 方法调用所在行号
    call_column: int           # 方法调用所在列号
    variable_name: str         # 调用的变量名
    method_name: str           # 被调用的方法名
    arguments: List[str]       # 方法参数（如果能解析到）
    context_code: str          # 调用上下文代码
    
    def __str__(self) -> str:
        return f"{self.caller_method_name}() -> {self.variable_name}.{self.method_name}() at line {self.call_line}"
@dataclass
class MethodReferenceResult:
    """方法引用分析结果"""
    success: bool                           # 分析是否成功
    target_class: str                       # 目标类名
    target_method: str                      # 目标方法名
    file_path: str                         # 分析的文件路径
    
    # 找到的变量信息
    variables: List[VariableInfo]          # 目标类型的变量列表
    
    # 找到的方法调用信息
    method_calls: List[MethodCallInfo]     # 方法调用列表
    
    # 错误信息
    error_message: Optional[str] = None    # 错误消息
    
    # 统计信息
    total_variables_found: int = 0         # 找到的变量总数
    total_calls_found: int = 0            # 找到的调用总数
    
    def __post_init__(self):
        """初始化后处理"""
        self.total_variables_found = len(self.variables)
        self.total_calls_found = len(self.method_calls)
    
    def get_summary(self) -> str:
        """获取分析结果摘要"""
        if not self.success:
            return f"分析失败: {self.error_message}"
        
        return (f"在 {self.file_path} 中找到 {self.total_variables_found} 个 {self.target_class} 类型变量，"
                f"{self.total_calls_found} 个 {self.target_method} 方法调用")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": self.success,
            "target_class": self.target_class,
            "target_method": self.target_method,
            "file_path": self.file_path,
            "variables": [
                {
                    "name": var.name,
                    "type_name": var.type_name,
                    "full_type_name": var.full_type_name,
                    "scope": var.scope.value,
                    "declaration_line": var.declaration_line,
                    "declaration_column": var.declaration_column
                }
                for var in self.variables
            ],
            "method_calls": [
                {
                    "caller_method_name": call.caller_method_name,
                    "caller_method_line": call.caller_method_line,
                    "call_line": call.call_line,
                    "call_column": call.call_column,
                    "variable_name": call.variable_name,
                    "method_name": call.method_name,
                    "arguments": call.arguments,
                    "context_code": call.context_code
                }
                for call in self.method_calls
            ],
            "error_message": self.error_message,
            "total_variables_found": self.total_variables_found,
            "total_calls_found": self.total_calls_found
        }
@dataclass
class ImportInfo:
    """导入信息"""
    import_name: str           # 导入名称
    alias: Optional[str]       # 别名
    is_static: bool           # 是否为静态导入
    is_wildcard: bool         # 是否为通配符导入
    line_number: int          # 导入语句行号
    
    def get_class_name(self) -> str:
        """获取类名"""
        if self.alias:
            return self.alias
        
        # 从完整包名中提取类名
        if '.' in self.import_name:
            return self.import_name.split('.')[-1]
        
        return self.import_name
    
    def get_package_name(self) -> str:
        """获取包名"""
        if self.is_wildcard:
            # 对于通配符导入，返回去掉.*的包名
            return self.import_name.rstrip('.*')
        elif '.' in self.import_name:
            # 对于具体导入，返回去掉类名的包名
            parts = self.import_name.split('.')
            return '.'.join(parts[:-1])
        return ""
@dataclass
class ClassInfo:
    """类信息"""
    name: str                 # 类名
    full_name: str           # 完整类名（包含包名）
    package_name: str        # 包名
    start_line: int          # 类开始行号
    end_line: int           # 类结束行号
    
    def __str__(self) -> str:
        return f"{self.full_name} (lines {self.start_line}-{self.end_line})"