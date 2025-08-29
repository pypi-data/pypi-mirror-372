"""
工具函数

提供端点提取器使用的辅助工具函数。
"""

import logging
from typing import List, Optional, Dict, Any

from .models import EndpointCandidate
from .rule_engine import LanguageRuleEngine
from ...code.skeleton import extract_skeleton, validate_file_for_skeleton_extraction

logger = logging.getLogger(__name__)


def get_supported_languages() -> List[str]:
    """获取支持的编程语言列表"""
    engine = LanguageRuleEngine()
    return list(engine.rules.keys())


def analyze_single_file(file_path: str) -> Optional[Dict[str, Any]]:
    """分析单个文件是否为端点文件"""
    engine = LanguageRuleEngine()
    candidate = engine.evaluate_file(file_path)
    
    if candidate:
        # 提取详细骨架
        is_valid, validation_msg = validate_file_for_skeleton_extraction(file_path)
        if is_valid:
            try:
                candidate.skeleton = extract_skeleton(file_path)
            except Exception as e:
                logger.warning(f"提取骨架时出错: {e}")
        else:
            logger.warning(f"文件验证失败 {file_path}: {validation_msg}")
        
        return {
            'file_path': candidate.file_path,
            'language': candidate.language,
            'confidence_score': candidate.confidence_score,
            'match_reasons': candidate.match_reasons,
            'skeleton': candidate.skeleton
        }
    
    return None