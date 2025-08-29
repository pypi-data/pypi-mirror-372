"""
Agent工具工厂
"""

import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool

from .file_search import FileSearchTool
from .file_read import FileReadTool
from .directory_structure import DirectoryStructureTool
from .rag_search import RAGSearchTool
from .code_skeleton_tool import CodeSkeletonTool
from .method_extractor_tool import MethodExtractorTool
from .dependency_extractor_tool import DependencyExtractorTool
from .text_grep_tool import TextGrepTool
from .db_extractor_tool import DBExtractorTool, DBExtractorInput
from .prd_review_tools import (
    PRDDocumentStructureAnalysisTool
)
from .exceptions import ConfigurationError
from .error_handler import ErrorHandler, safe_execute


# Pydantic 输入参数模型定义

class FileSearchInput(BaseModel):
    """文件搜索工具输入参数模型
    
    支持通配符模式搜索文件，可指定搜索根目录。
    也支持JSON格式参数输入：{"pattern": "*.py", "root": "src"}
    """
    pattern: str = Field(
        description="搜索模式，支持通配符。支持递归搜索(**/)和多扩展名匹配({py,js})",
        examples=["*.py", "**/*.java", "src/**/*.{py,js}", "test_*.py"]
    )
    root: str = Field(
        default=".",
        description="搜索根目录，相对于项目根目录的路径，默认为当前目录(.)"
    )


class FileReadInput(BaseModel):
    """文件读取工具输入参数模型
    
    读取指定文件的完整内容，支持自动编码检测和行范围读取。
    也支持JSON格式参数输入：{"file_path": "src/main.py", "start_line": 10, "end_line": 50}
    """
    file_path: str = Field(
        description="要读取的文件路径，相对于项目根目录。支持路径兼容性处理",
        examples=["src/main.py", "config/settings.json", "README.md", "docs/api.md"]
    )
    start_line: Optional[int] = Field(
        default=None,
        description="起始行号，从1开始计数，用于指定读取范围的开始位置。当指定此参数时，将跳过内容压缩，返回原始文件内容",
        examples=[1, 10, 50],
        ge=1
    )
    end_line: Optional[int] = Field(
        default=None,
        description="结束行号，包含该行，用于指定读取范围的结束位置。支持边界处理，超出文件行数时返回可用部分",
        examples=[20, 100, 500],
        ge=1
    )


class DirectoryStructureInput(BaseModel):
    """目录结构分析工具输入参数模型
    
    分析目录的树状结构，支持多种输出格式和深度控制。
    也支持JSON格式参数输入：{"target_path": "src", "max_depth": 3, "include_files": true}
    支持特殊格式：路径后跟数字表示深度，如 "src 5" 或 "src"
    """
    target_path: str = Field(
        description="目标目录路径，相对于项目根目录。",
        examples=["src", ".", "config"]
    )
    max_depth: int = Field(
        default=3,
        description="最大递归深度，控制目录树的深度",
        ge=1,
        le=10
    )
    include_files: bool = Field(
        default=True,
        description="是否在结果中包含文件，false时只显示目录结构"
    )


class CodeSkeletonInput(BaseModel):
    """代码骨架提取工具输入参数模型
    
    提取代码文件的结构骨架，支持多种编程语言。
    也支持JSON格式参数输入：{"file_path": "src/main.py"}
    """
    file_path: str = Field(
        description="代码文件的路径，相对于项目根目录。必须是支持的编程语言文件",
        examples=["src/main.py", "lib/utils.js", "service/UserService.java", "components/App.tsx"]
    )


class MethodExtractorInput(BaseModel):
    """方法提取工具输入参数模型
    
    从代码文件中提取指定方法的完整代码，支持参数类型匹配。
    也支持JSON格式参数输入：{"file_path": "src/utils.py", "method_name": "calculate", "arg_types": "int, str"}
    """
    file_path: str = Field(
        description="代码文件的路径，相对于项目根目录。必须是支持的编程语言文件",
        examples=["src/utils.py", "service/Utils.java", "lib/helper.js", "controllers/UserController.py"]
    )
    method_name: Optional[str] = Field(
        default=None,
        description="要提取的方法名称。如果为空，工具将报错要求提供方法名"
    )
    arg_types: Optional[str] = Field(
        default=None,
        description="参数类型列表，支持多种格式：逗号分隔字符串、JSON数组字符串。为空时取第一个匹配方法名的方法",
        examples=["String, int, boolean", "[\"String\", \"int\", \"boolean\"]", "String", "int, List<String>"]
    )


class DependencyExtractorInput(BaseModel):
    """依赖提取工具输入参数模型
    
    提取代码文件的项目内部依赖文件列表，自动排除第三方库和内置依赖。
    也支持JSON格式参数输入：{"file_path": "src/main.py"}
    """
    file_path: str = Field(
        description="要分析的代码文件路径，相对于项目根目录。必须是支持的编程语言文件",
        examples=["src/main.py", "service/Main.java", "app/app.js", "controllers/UserController.py"]
    )


class RAGSearchInput(BaseModel):
    """RAG搜索工具输入参数模型
    
    在项目知识库中进行智能语义搜索，支持自然语言查询。
    也支持JSON格式参数输入：{"query": "用户认证逻辑", "k": 5}
    """
    query: str = Field(
        description="搜索查询字符串，支持自然语言、技术关键词、代码元素、功能描述等",
        examples=["用户认证逻辑", "JWT认证", "Redis缓存", "数据库连接", "UserService", "@RequestMapping"]
    )
    k: int = Field(
        default=5,
        description="返回结果数量，默认为5个，最大20个",
        ge=1,
        le=20
    )


class TextGrepInput(BaseModel):
    """文本搜索工具输入参数模型
    
    根据关键字搜索对应的文本块，返回包含关键字的代码块。
    支持英文搜索时自动忽略大小写，中文搜索保持大小写敏感。
    也支持JSON格式参数输入：{"keyword": "UserService"}
    """
    keyword: str = Field(
        description="搜索关键字，将在代码文件中搜索包含此关键字的文本块。英文搜索时自动忽略大小写, 主要用于搜索方法名、变量名等",
        examples=["UserService", "authenticate", "@RequestMapping", "public void", "class User", "用户名"]
    )

from .method_dependency_analyzer import MethodDependencyAnalyzerInput, MethodDependencyAnalyzer

class PRDStructureAnalysisInput(BaseModel):
    """PRD文档结构分析工具输入参数模型"""
    prd_content: str = Field(
        description="PRD文档内容，用于分析文档结构",
        examples=["# 项目背景\n## 需求概述\n### 功能需求"]
    )


class AgentToolFactory:
    """Agent工具工厂类 - 重构版本（使用 StructuredTool）
    
    提供统一的工具创建和管理接口，支持灵活的配置选项和统一的错误处理机制。
    
    ## 主要改进
    
    1. **StructuredTool 支持**: 使用 StructuredTool 替代 Tool.from_function()
    2. **Pydantic 验证**: 为每个工具定义输入参数的 Pydantic 模型
    3. **JSON 格式支持**: 支持 JSON 格式的参数输入和验证
    4. **统一错误处理**: 所有工具现在使用统一的错误处理机制
    5. **结构化响应**: 工具返回标准化的响应格式
    6. **增强配置**: 支持更多配置选项和验证
    7. **向后兼容**: 保持与现有代码的兼容性
    8. **详细文档**: 提供完整的工具使用说明
    """
    
    def __init__(self):
        """初始化工具工厂"""
        self.error_handler = ErrorHandler()
    
    @staticmethod
    def create_tools(base_dir: str, rag_service=None, tool_config: dict = None) -> List[StructuredTool]:
        """
        创建Agent工具列表
        
        Args:
            base_dir: 基础目录路径
            rag_service: RAG服务实例（可选）
            tool_config: 工具配置字典（可选），支持的配置项：
                - file_search_format: FileSearchTool的输出格式
                - directory_format: DirectoryStructureTool的输出格式
                - max_file_size: FileReadTool的最大文件大小限制
                - use_error_handling: 是否使用统一错误处理（默认True）
            
        Returns:
            StructuredTool 工具列表
            
        Raises:
            ConfigurationError: 配置错误
        """
        try:
            # 验证base_dir
            validated_base_dir = AgentToolFactory.validate_base_dir(base_dir)
            
            # 处理工具配置
            config = tool_config or {}
            file_search_format = config.get('file_search_format', 'plain')
            directory_format = config.get('directory_format', 'simple')
            max_file_size = config.get('max_file_size', 10 * 1024 * 1024)  # 10MB
            
            # 创建工具实例
            file_search_tool = FileSearchTool(base_dir=validated_base_dir, output_format=file_search_format)
            file_read_tool = FileReadTool(base_dir=validated_base_dir)
            directory_tool = DirectoryStructureTool(base_dir=validated_base_dir, output_format=directory_format)
            code_skeleton_tool = CodeSkeletonTool(base_dir=validated_base_dir)
            method_extractor_tool = MethodExtractorTool(base_dir=validated_base_dir)
            dependency_extractor_tool = DependencyExtractorTool(base_dir=validated_base_dir)
            text_grep_tool = TextGrepTool(base_dir=validated_base_dir)
            method_dependency_analyzer = MethodDependencyAnalyzer(base_dir=validated_base_dir)
            db_extractor_tool = DBExtractorTool(base_dir=validated_base_dir)
            
            # 设置文件读取工具的大小限制
            if max_file_size != file_read_tool.max_file_size:
                file_read_tool.set_max_file_size(max_file_size)
            
            tools = [
                StructuredTool.from_function(
                    func=file_search_tool.run,
                    name="FileSearch",
                    description="根据通配符模式搜索文件。支持递归搜索和多种输出格式，可指定搜索根目录。支持JSON格式参数输入",
                    args_schema=FileSearchInput
                ),
                StructuredTool.from_function(
                    func=file_read_tool.run,
                    name="FileRead",
                    description="读取文件，文件过大时会被提取摘要返回。读取完整内容可指定行号参数",
                    args_schema=FileReadInput
                ),
                StructuredTool.from_function(
                    func=directory_tool.run,
                    name="DirectoryStructure",
                    description="分析并返回目录的树状结构。支持多种输出格式(simple/compact/json)和深度控制。支持JSON格式参数和特殊路径格式",
                    args_schema=DirectoryStructureInput
                ),
                StructuredTool.from_function(
                    func=code_skeleton_tool.run,
                    name="CodeSkeleton",
                    description="提取代码文件的结构骨架。支持多种编程语言，提取类、方法、函数等结构信息。支持JSON格式参数输入",
                    args_schema=CodeSkeletonInput
                ),
                StructuredTool.from_function(
                    func=method_extractor_tool.run,
                    name="MethodExtractor",
                    description="从代码文件中提取指定方法的完整代码。支持参数类型匹配和方法重载识别。支持JSON格式参数输入",
                    args_schema=MethodExtractorInput
                ),
                StructuredTool.from_function(
                    func=dependency_extractor_tool.run,
                    name="DependencyExtractor",
                    description="提取代码文件的项目内部依赖文件列表。自动排除第三方库和内置依赖，只返回项目内文件。支持JSON格式参数输入",
                    args_schema=DependencyExtractorInput
                ),
                StructuredTool.from_function(
                    func=text_grep_tool.run,
                    name="TextGrep",
                    description="根据关键字搜索对应的文本块，智能提取完整的方法、函数或字段定义。支持多种编程语言，返回完整代码块包含注释。支持JSON格式参数输入",
                    args_schema=TextGrepInput
                ),
                StructuredTool.from_function(
                    func=method_dependency_analyzer.run,
                    name="MethodDependencyAnalyzer",
                    description="根据方法全名搜索方法引用，返回markdown格式引用说明。支持JSON格式参数输入",
                    args_schema=MethodDependencyAnalyzerInput
                ),
                StructuredTool.from_function(
                    func=db_extractor_tool.run,
                    name="DBExtractor",
                    description="数据库配置提取和查询工具。从项目中提取数据库配置信息，并可查询表结构。支持JSON格式参数输入",
                    args_schema=DBExtractorInput
                )
            ]
            
            # 如果有RAG服务，添加RAG搜索工具
            if rag_service:
                rag_tool = RAGSearchTool(rag_service=rag_service)
                tools.append(
                    StructuredTool.from_function(
                        func=rag_tool.run,
                        name="RAGSearch",
                        description="在项目知识库中进行智能语义搜索。支持自然语言查询、技术关键词、代码元素搜索。支持JSON格式参数输入",
                        args_schema=RAGSearchInput
                    )
                )
            
            
            return tools
            
        except Exception as e:
            raise ConfigurationError(
                f"创建Agent工具失败，base_dir={base_dir}: {str(e)}",
                tool_name="AgentToolFactory"
            ) from e
    
    @staticmethod
    def validate_base_dir(base_dir: str) -> str:
        """
        验证并标准化基础目录路径
        
        Args:
            base_dir: 基础目录路径
            
        Returns:
            标准化后的绝对路径
            
        Raises:
            ConfigurationError: 目录无效
        """
        if not base_dir or not base_dir.strip():
            raise ConfigurationError(
                "基础目录路径不能为空",
                config_key="base_dir",
                tool_name="AgentToolFactory"
            )
        
        base_dir = os.path.abspath(base_dir.strip())
        base_path = Path(base_dir)
        
        if not base_path.exists():
            raise ConfigurationError(
                f"基础目录不存在: {base_dir}",
                config_key="base_dir",
                config_value=base_dir,
                tool_name="AgentToolFactory"
            )
        if not base_path.is_dir():
            raise ConfigurationError(
                f"基础路径不是目录: {base_dir}",
                config_key="base_dir",
                config_value=base_dir,
                tool_name="AgentToolFactory"
            )
        
        return base_dir
        