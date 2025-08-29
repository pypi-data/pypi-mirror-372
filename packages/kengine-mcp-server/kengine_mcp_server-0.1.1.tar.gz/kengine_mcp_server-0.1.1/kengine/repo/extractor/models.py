"""
数据模型定义

定义了端点提取器使用的核心数据结构，包括语言规则和端点候选项。
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LanguageRule:
    """语言规则定义"""
    name: str
    file_patterns: List[str]
    annotations: List[str]
    directories: List[str]
    priority_weight: float = 1.0
    framework_hints: List[str] = field(default_factory=list)


@dataclass
class EndpointCandidate:
    """端点候选项"""
    file_path: str
    language: str
    confidence_score: float
    match_reasons: List[str]
    framework: Optional[str] = None
    skeleton: Optional[str] = None