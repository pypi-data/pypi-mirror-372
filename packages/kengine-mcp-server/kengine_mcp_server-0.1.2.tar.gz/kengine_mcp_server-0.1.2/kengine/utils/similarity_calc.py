"""
使用 spaCy 实现文本相似度计算的方法， 返回是否相似 ， 用户可传入相似度的阈值
"""

import spacy
import logging
from typing import Any, Callable, Optional, Tuple
import warnings

# 配置日志
logger = logging.getLogger(__name__)

class SimilarityCalculator:
    """
    基于 spaCy 的文本相似度计算器
    
    使用预训练的中文模型计算两个文本之间的语义相似度
    """
    
    def __init__(self, model_name: str = "zh_core_web_md"):
        """
        初始化相似度计算器
        
        Args:
            model_name: spaCy 模型名称，默认使用中文模型 zh_core_web_md
        """
        self.model_name = model_name
        self.nlp = None
        self._load_model()
    
    def _load_model(self) -> None:
        """
        加载 spaCy 模型
        
        Raises:
            OSError: 当模型未安装或加载失败时
        """
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"成功加载 spaCy 模型: {self.model_name}")
        except OSError as e:
            error_msg = f"无法加载 spaCy 模型 '{self.model_name}': {str(e)}"
            logger.error(error_msg)
            raise OSError(error_msg) from e
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本之间的相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            float: 相似度分数，范围 [0, 1]，1 表示完全相似，0 表示完全不相似
            
        Raises:
            ValueError: 当输入文本为空或无效时
            RuntimeError: 当模型未正确加载时
        """
        if not isinstance(text1, str) or not isinstance(text2, str):
            raise ValueError("输入必须是字符串类型")
        
        if not text1.strip() or not text2.strip():
            logger.warning("输入文本为空，返回相似度为 0")
            return 0.0
        
        if self.nlp is None:
            raise RuntimeError("spaCy 模型未正确加载")
        
        try:
            # 处理文本并获取文档向量
            doc1 = self.nlp(text1.strip())
            doc2 = self.nlp(text2.strip())
            
            # 检查文档是否有向量表示
            if not doc1.has_vector or not doc2.has_vector:
                logger.warning("文档缺少向量表示，可能是因为文本太短或包含未知词汇")
                return 0.0
            
            # 计算相似度
            similarity = doc1.similarity(doc2)
            
            # 确保返回值在有效范围内
            similarity = max(0.0, min(1.0, similarity))
            
            logger.debug(f"文本相似度计算完成: {similarity:.4f}")
            return similarity
            
        except Exception as e:
            logger.error(f"计算相似度时发生错误: {str(e)}")
            raise RuntimeError(f"相似度计算失败: {str(e)}") from e
    
    def is_similar(self, text1: str, text2: str, threshold: float = 0.85) -> bool:
        """
        判断两个文本是否相似
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            threshold: 相似度阈值，默认为 0.7
            
        Returns:
            bool: True 表示相似，False 表示不相似
            
        Raises:
            ValueError: 当阈值不在有效范围内时
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"阈值必须在 [0, 1] 范围内，当前值: {threshold}")
        
        similarity = self.calculate_similarity(text1, text2)
        is_sim = similarity >= threshold
        
        logger.info(f"相似度判断: {similarity:.4f} {'≥' if is_sim else '<'} {threshold} = {is_sim}")
        return is_sim
    
    def deduplicate_by_similarity(self, texts: list, threshold: float = 0.85) -> list:
        """
        根据相似度对文本数组进行去重
        
        Args:
            texts: 文本列表
            threshold: 相似度阈值，默认为 0.85
            
        Returns:
            list: 去重后的文本列表
        """
        if not isinstance(texts, list):
            raise ValueError("输入必须是列表类型")
        
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"阈值必须在 [0, 1] 范围内，当前值: {threshold}")
        
        if len(texts) <= 1:
            return texts.copy()
        
        # 过滤掉空文本和非字符串类型
        valid_texts = []
        for i, text in enumerate(texts):
            if isinstance(text, str) and text.strip():
                valid_texts.append(text.strip())
            else:
                logger.warning(f"跳过无效文本 (索引 {i}): {text}")
        
        if len(valid_texts) <= 1:
            return valid_texts
        
        # 去重算法：保留第一个出现的文本，移除后续相似的文本
        unique_texts = []
        
        for current_text in valid_texts:
            is_duplicate = False
            
            # 与已保留的文本进行相似度比较
            for unique_text in unique_texts:
                try:
                    similarity = self.calculate_similarity(current_text, unique_text)
                    if similarity >= threshold:
                        logger.debug(f"发现重复文本 (相似度: {similarity:.4f}): '{current_text[:50]}...' 与 '{unique_text[:50]}...'")
                        is_duplicate = True
                        break
                except Exception as e:
                    logger.error(f"计算相似度时出错: {str(e)}")
                    continue
            
            if not is_duplicate:
                unique_texts.append(current_text)
        
        logger.info(f"文本去重完成: {len(valid_texts)} -> {len(unique_texts)} (阈值: {threshold})")
        return unique_texts
    
    
    def deduplicate_by_text_similarity(self, objects: list, text_getter: Callable[[Any], str],  threshold: float = 0.85) -> list:
        """
        根据相似度对对象数组进行去重
        
        Args:
            objects: 对象列表
            text_getter: 文本获取函数
            threshold: 相似度阈值，默认为 0.85
            
        Returns:
            list: 去重后的文本列表
        """
        if not isinstance(objects, list):
            raise ValueError("输入必须是列表类型")
        
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"阈值必须在 [0, 1] 范围内，当前值: {threshold}")
        
        if len(objects) <= 1:
            return objects
        
        # 过滤掉空文本和非字符串类型
        valid_objects = []
        for i, obj in enumerate(objects):
            text = text_getter(obj)
            if isinstance(text, str) and text.strip():
                valid_objects.append(obj)
            else:
                logger.warning(f"跳过无效文本 (索引 {i}): {text}")
        
        if len(valid_objects) <= 1:
            return valid_objects
        
        # 去重算法：保留第一个出现的文本，移除后续相似的文本
        unique_objs = []
        
        for current_object in valid_objects:
            is_duplicate = False
            current_text = text_getter(current_object)
            # 与已保留的文本进行相似度比较
            for unique_obj in unique_objs:
                try:
                    unique_text = text_getter(unique_obj)
                    similarity = self.calculate_similarity(current_text, unique_text)
                    if similarity >= threshold:
                        logger.debug(f"发现重复文本 (相似度: {similarity:.4f}): '{current_text[:50]}...' 与 '{unique_text[:50]}...'")
                        is_duplicate = True
                        break
                except Exception as e:
                    logger.error(f"计算相似度时出错: {str(e)}")
                    continue
            
            if not is_duplicate:
                unique_objs.append(current_object)
        
        logger.info(f"对象去重完成: {len(valid_objects)} -> {len(unique_objs)} (阈值: {threshold})")
        return unique_objs
    
    def get_model_info(self) -> dict:
        """
        获取当前加载的模型信息
        
        Returns:
            dict: 模型信息字典
        """
        if self.nlp is None:
            return {"model_name": self.model_name, "loaded": False}
        
        return {
            "model_name": self.model_name,
            "loaded": True,
            "lang": self.nlp.lang,
            "pipeline": list(self.nlp.pipe_names),
            "vocab_size": len(self.nlp.vocab),
            "has_vectors": self.nlp.vocab.vectors_length > 0,
            "vector_size": self.nlp.vocab.vectors_length
        }


# 便捷函数
_default_calculator = None

def get_default_calculator() -> SimilarityCalculator:
    """
    获取默认的相似度计算器实例（单例模式）
    
    Returns:
        SimilarityCalculator: 默认计算器实例
    """
    global _default_calculator
    if _default_calculator is None:
        _default_calculator = SimilarityCalculator()
    return _default_calculator


def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度（便捷函数）
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        
    Returns:
        float: 相似度分数 [0, 1]
    """
    calculator = get_default_calculator()
    return calculator.calculate_similarity(text1, text2)


def is_similar(text1: str, text2: str, threshold: float = 0.85) -> bool:
    """
    判断两个文本是否相似（便捷函数）
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        threshold: 相似度阈值，默认 0.7
        
    Returns:
        bool: 是否相似
    """
    calculator = get_default_calculator()
    return calculator.is_similar(text1, text2, threshold)


def deduplicate_by_similarity(texts: list, threshold: float = 0.85) -> list:
    """
    根据相似度对文本数组进行去重（便捷函数）
    
    Args:
        texts: 文本列表
        threshold: 相似度阈值，默认 0.85
        
    Returns:
        list: 去重后的文本列表
    """
    calculator = get_default_calculator()
    return calculator.deduplicate_by_similarity(texts, threshold)


def deduplicate_by_text_similarity(objects: list, text_getter: Callable[[Any], str], threshold: float = 0.85) -> list:
    """
    根据相似度对对象数组进行去重（便捷函数）
    
    Args:
        objects: 对象列表
        text_getter： 根据对象获得文本的函数
        threshold: 相似度阈值，默认 0.85
        
    Returns:
        list: 去重后的对象列表
    """
    calculator = get_default_calculator()
    return calculator.deduplicate_by_text_similarity(objects, text_getter, threshold)
