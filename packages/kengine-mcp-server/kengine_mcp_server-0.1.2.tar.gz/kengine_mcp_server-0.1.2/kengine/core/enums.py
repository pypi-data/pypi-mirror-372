"""
统一的枚举定义模块

包含知识生成系统中使用的所有枚举类型，避免重复定义
"""

from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 待处理
    RUNNING = "running"      # 进行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


class ProgressStage(Enum):
    """进度阶段枚举"""
    CLONE = "clone"                           # 代码库克隆
    CLASSIFICATION = "classification"         # 项目分类
    RAG_BUILD = "rag_build"                  # RAG知识库构建
    CATALOGUE_GENERATION = "catalogue_generation"  # 文档目录生成
    DOCUMENT_GENERATION = "document_generation"    # 文档内容生成
    OVERVIEW_GENERATION = "overview_generation"    # 项目概览生成
    UNKNOWN = "unknown" # 未知阶段， 用于错误处理


class ProgressStatus(Enum):
    """进度状态枚举"""
    PENDING = "pending"      # 待处理
    RUNNING = "running"      # 进行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败


class LLMCallType(Enum):
    """大模型调用类型枚举"""
    CLASSIFICATION = "classification"           # 项目分类
    OVERVIEW_GENERATION = "overview_generation" # 概览生成
    CATALOGUE_GENERATION = "catalogue_generation" # 目录生成
    DOCUMENT_GENERATION = "document_generation"   # 文档生成
    SUMMARY_GENERATION = "summary_generation"     # 摘要生成
    RAG_QUERY = "rag_query"                      # RAG查询
    OTHER = "other"                              # 其他


class ExecuteStep(Enum):
    """执行步骤枚举"""
    CLASSIFICATION = "classification"
    OVERVIEW = "overview"
    CATALOGUE = "catalogue"
    DOCUMENT = "document"
    FULL = "full"
    
    @classmethod
    def from_string(cls, value: str) -> 'ExecuteStep':
        """
        从字符串转换为枚举值
        
        Args:
            value: 字符串值
            
        Returns:
            ExecuteStep枚举值
            
        Raises:
            ValueError: 当字符串值无效时
        """
        if not isinstance(value, str):
            raise ValueError(f"执行步骤必须是字符串类型，当前类型: {type(value).__name__}")
        
        value_lower = value.lower()
        for step in cls:
            if step.value.lower() == value_lower:
                return step
        
        valid_values = [step.value for step in cls]
        raise ValueError(f"无效的执行步骤: '{value}'，有效值为: {valid_values}")
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """
        验证字符串是否为有效的执行步骤
        
        Args:
            value: 要验证的字符串值
            
        Returns:
            bool: 是否有效
        """
        try:
            cls.from_string(value)
            return True
        except ValueError:
            return False
    
    @classmethod
    def steps(cls) -> list:
        """
        获取所有有效的执行步骤值
        
        Returns:
            list: 所有有效步骤值的列表
        """
        return [step.value for step in cls]


class GenerationStrategy(Enum):
    """生成策略枚举"""
    PROMPT = "prompt"
    AGENT = "agent"
    HYBRID = "hybrid"


class ValidationLevel(Enum):
    """验证级别枚举"""
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"


class ProgressType(Enum):
    """进度更新类型枚举
    
    用于区分不同类型的进度更新事件，主要用于SSE进度推送
    """
    STAGE_START = "stage_start"          # 阶段开始
    STAGE_PROGRESS = "stage_progress"    # 阶段进行中
    STAGE_COMPLETE = "stage_complete"    # 阶段完成
    DOCUMENT_PROGRESS = "document_progress"  # 文档进度更新
    ERROR = "error"                      # 错误
    COMPLETE = "complete"                # 完全完成

class MainLanguage(Enum):
    """主语言

    """
    JAVA = "java"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GOLANG = "golang"
    VUE = "vue"
    ANDROID = "android"
    ETC = "其他"

class EndpointType(Enum):
    """端点类型枚举"""
    JSF = 1
    JMQ = 2
    HTTP = 3
    TASK_TRIGGER = 4

class DocumentStatus(Enum):
    """文档状态枚举"""
    PENDING = 1
    COMPLETED = 2
    FAILED = 3

class DocumentVersionType(Enum):
    """文档版本类型枚举"""
    BIZ_DOMAIN = 1
    TECH_DOMAIN = 2

class DocumentChangeType(Enum):
    """文档变更类型枚举"""
    COMMENT = 1