"""
文本总结工具模块

提供基于LLM的文本总结功能，支持自定义提示词模板和参数配置。
支持超长文本的分批总结功能。
"""

import logging
from typing import List

from kengine.tasks.llm import init_llm
from kengine.utils.prompt_loader import load_summerize_prompt
from kengine.core.utils.exceptions import SummarizeError
from kengine.config.application_config import get_application_config

logger = logging.getLogger(__name__)

MAX_LLM_INPUT_LENGTH = 4096


def _split_content_by_lines(content: str, max_length: int) -> List[str]:
    """
    按行分割内容，确保每个分块不超过最大长度
    
    Args:
        content (str): 需要分割的内容
        max_length (int): 每个分块的最大长度
        
    Returns:
        List[str]: 分割后的内容块列表
    """
    lines = content.split('\n')
    chunks = []
    current_chunk = ""
    
    for line in lines:
        # 如果单行就超过最大长度，需要按字符分割
        if len(line) > max_length:
            # 先保存当前块（如果有内容）
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # 按字符分割超长行
            line_chunks = _split_content_by_chars(line, max_length)
            chunks.extend(line_chunks)
        else:
            # 检查添加这一行后是否会超过限制
            test_chunk = current_chunk + ('\n' if current_chunk else '') + line
            if len(test_chunk) > max_length:
                # 保存当前块并开始新块
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                # 添加到当前块
                current_chunk = test_chunk
    
    # 添加最后一个块
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def _split_content_by_chars(content: str, max_length: int) -> List[str]:
    """
    按字符长度分割内容
    
    Args:
        content (str): 需要分割的内容
        max_length (int): 每个分块的最大长度
        
    Returns:
        List[str]: 分割后的内容块列表
    """
    chunks = []
    start = 0
    
    while start < len(content):
        end = start + max_length
        chunk = content[start:end]
        chunks.append(chunk)
        start = end
    
    return chunks


def _split_content(content: str, max_length: int) -> List[str]:
    """
    智能分割内容，优先按行分割，必要时按字符分割
    
    Args:
        content (str): 需要分割的内容
        max_length (int): 每个分块的最大长度
        
    Returns:
        List[str]: 分割后的内容块列表
    """
    if len(content) <= max_length:
        return [content]
    
    # 检查是否包含换行符
    if '\n' in content:
        logger.debug("使用按行分割策略")
        return _split_content_by_lines(content, max_length)
    else:
        logger.debug("使用按字符分割策略")
        return _split_content_by_chars(content, max_length)


def _calculate_effective_max_length(prompt_template: str, max_tokens: int, max_output_length: int) -> int:
    """
    计算有效的最大内容长度（考虑提示词模板的长度）
    
    Args:
        prompt_template (str): 提示词模板
        max_length (int): 用户指定的最大长度
        
    Returns:
        int: 有效的最大内容长度
    """
    # 估算提示词模板的长度（不包括变量部分）
    template_overhead = len(prompt_template) - len('{content}') - len('{max_length}') + len(str(max_output_length))
    
    # 预留一些缓冲空间
    buffer = 100
    
    effective_length = max_tokens - template_overhead - buffer
    
    # 确保有效长度是正数且合理
    if effective_length < 500:
        effective_length = 500
        logger.warning(f"提示词模板过长，有效内容长度被限制为 {effective_length}")
    
    return effective_length


def _summerize_single_chunk(content: str, prompt_name: str, max_length: int, llm) -> str:
    """
    总结单个内容块
    
    Args:
        content (str): 需要总结的内容
        prompt_name (str): 提示词名称
        max_length (int): 最大长度
        llm: LLM实例
        
    Returns:
        str: 总结结果
    """
    prompt_template = load_summerize_prompt(prompt_name)
    formatted_prompt = prompt_template.format(
        content=content,
        max_length=max_length
    )
    
    response = llm.invoke(formatted_prompt)
    summary = response.content.strip()
    
    if not summary:
        raise SummarizeError("LLM返回了空的总结结果")
    
    return summary


def summerize(content: str, prompt_name: str, max_length: int) -> str:
    """
    根据总结的提示词模板，实现将输入内容 content 总结成摘要的功能
    支持超长文本的分批总结
    
    Args:
        content (str): 需要总结的原始内容
        prompt_name (str): 提示词模板名称，用于从 prompts-template/summerize/ 目录加载
        max_length (int): 总结的最大长度限制
        
    Returns:
        str: 总结后的摘要内容
        
    Raises:
        SummarizeError: 总结过程中发生的各种错误
        ValueError: 参数验证失败
        FileNotFoundError: 提示词模板文件不存在
        
    Examples:
        >>> content = "这是一段很长的文本内容..."
        >>> summary = summerize(content, "default", 200)
        >>> print(summary)
        "这是总结后的内容"
    """
    # 参数验证
    if not isinstance(content, str):
        raise ValueError("内容参数必须是字符串类型")
    
    if not content.strip():
        raise ValueError("内容不能为空")
    
    if not isinstance(prompt_name, str) or not prompt_name.strip():
        raise ValueError("提示词名称必须是非空字符串")
    
    if not isinstance(max_length, int) or max_length <= 0:
        raise ValueError("最大长度必须是正整数")
    
    try:
        logger.info(f"开始总结内容，提示词: {prompt_name}, 最大长度: {max_length}, 内容长度: {len(content)}")
        
        # 加载提示词模板
        prompt_template = load_summerize_prompt(prompt_name)
        logger.debug(f"成功加载提示词模板: {prompt_name}")
        
        # 初始化LLM
        app_config = get_application_config()
        summarize_settings = app_config.get('summarize_settings')
        summarize_model_name = summarize_settings.get('model_name', 'default')
        model_config = app_config.get_model_config(summarize_model_name)
        llm = init_llm(model_config)
        logger.debug("LLM初始化成功")
        
        # 计算有效的最大内容长度
        effective_max_length = _calculate_effective_max_length(prompt_template, model_config.get('max_tokens', MAX_LLM_INPUT_LENGTH), max_length)
        logger.debug(f"有效最大内容长度: {effective_max_length}")
        
        # 检查是否需要分批处理
        if len(content) <= effective_max_length:
            logger.debug("内容长度在限制范围内，直接总结")
            return _summerize_single_chunk(content, prompt_name, max_length, llm)
        
        # 分批处理超长内容
        logger.info(f"内容过长({len(content)} > {effective_max_length})，开始分批总结")
        chunks = _split_content(content, effective_max_length)
        logger.info(f"内容被分割为 {len(chunks)} 个块")
        
        # 对每个块进行总结
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            logger.debug(f"正在总结第 {i}/{len(chunks)} 个块，长度: {len(chunk)}")
            chunk_summary = _summerize_single_chunk(chunk, prompt_name, max_length, llm)
            chunk_summaries.append(chunk_summary)
            logger.debug(f"第 {i} 个块总结完成，总结长度: {len(chunk_summary)}")
        
        # 合并所有块的总结
        combined_summary = '\n\n'.join(chunk_summaries)
        logger.info(f"所有块总结完成，合并后长度: {len(combined_summary)}")
        
        # 检查合并后的总结是否仍然过长，如果是则递归总结
        if len(combined_summary) > effective_max_length:
            logger.info(f"合并后的总结仍然过长({len(combined_summary)} > {effective_max_length})，进行递归总结")
            return summerize(combined_summary, prompt_name, max_length)
        else:
            # 对合并后的内容进行最终总结
            logger.info("对合并后的内容进行最终总结")
            final_summary = _summerize_single_chunk(combined_summary, prompt_name, max_length, llm)
            logger.info(f"最终总结完成，原文长度: {len(content)}, 最终总结长度: {len(final_summary)}")
            return final_summary
            
    except (ValueError, FileNotFoundError):
        # 重新抛出已知的异常类型
        raise
    except SummarizeError:
        # 重新抛出自定义异常
        raise
    except Exception as e:
        # 捕获所有其他未预期的异常
        error_msg = f"总结过程中发生未知错误: {str(e)}"
        logger.error(error_msg)
        raise SummarizeError(error_msg) from e



def summerize_chunks(chunks: List[str],
                     chunk_prompt_name: str,
                     chunk_max_length: int,
                     summarize_chunk_prompt: str,
                     final_max_length: int) -> str:
    """
    对文本块列表进行分批总结，然后合并结果
    
    该函数实现两阶段总结策略：
    1. 第一阶段：使用 chunk_prompt_name 对每个文本块进行独立总结
    2. 第二阶段：使用 summarize_chunk_prompt 对所有块总结进行最终合并总结
    
    Args:
        chunks (List[str]): 需要总结的文本块列表，每个元素是一个独立的文本块
        chunk_prompt_name (str): 用于总结单个块的提示词名称，从 prompts-template/summerize/ 目录加载
        chunk_max_length (int): 单个块总结的最大长度限制，必须是正整数
        summarize_chunk_prompt (str): 用于最终合并总结的提示词名称，从 prompts-template/summerize/ 目录加载
        final_max_length (int): 最终总结的最大长度限制，必须是正整数
        
    Returns:
        str: 最终合并后的总结内容
        
    Raises:
        ValueError: 参数验证失败时抛出
        SummarizeError: 总结过程中发生错误时抛出
        FileNotFoundError: 提示词模板文件不存在时抛出
        
    Examples:
        >>> chunks = ["第一段内容...", "第二段内容...", "第三段内容..."]
        >>> result = summerize_chunks(chunks, "default", 100, "default", 200)
        >>> print(result)
        "合并后的总结内容"
        
    Note:
        - 如果输入的chunks列表为空，将返回空字符串
        - 如果只有一个chunk，仍会执行两阶段总结流程
        - 函数会自动处理超长的合并总结，必要时进行递归总结
    """
    # 参数验证
    if not isinstance(chunks, list):
        raise ValueError("chunks参数必须是列表类型")
    
    if not chunks:
        logger.warning("输入的文本块列表为空，返回空字符串")
        return ""
    
    # 验证chunks中的每个元素都是字符串且不为空
    for i, chunk in enumerate(chunks):
        if not isinstance(chunk, str):
            raise ValueError(f"chunks[{i}]必须是字符串类型，当前类型: {type(chunk)}")
        if not chunk:
            raise ValueError(f"chunks[{i}]不能为空字符串")
        if not chunk.strip():
            raise ValueError(f"chunks[{i}]不能为空白字符串")
    
    if not isinstance(chunk_prompt_name, str) or not chunk_prompt_name.strip():
        raise ValueError("chunk_prompt_name必须是非空字符串")
    
    if not isinstance(chunk_max_length, int) or chunk_max_length <= 0:
        raise ValueError("chunk_max_length必须是正整数")
    
    if not isinstance(summarize_chunk_prompt, str) or not summarize_chunk_prompt.strip():
        raise ValueError("summarize_chunk_prompt必须是非空字符串")
    
    if not isinstance(final_max_length, int) or final_max_length <= 0:
        raise ValueError("final_max_length必须是正整数")
    
    try:
        logger.info(f"开始分批总结，共{len(chunks)}个文本块")
        logger.debug(f"块总结提示词: {chunk_prompt_name}, 块最大长度: {chunk_max_length}")
        logger.debug(f"最终总结提示词: {summarize_chunk_prompt}, 最终最大长度: {final_max_length}")
        
        # 第一阶段：对每个文本块进行独立总结
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            logger.debug(f"正在总结第{i}/{len(chunks)}个文本块，长度: {len(chunk)}")
            
            try:
                # ignore empty chunk
                if not chunk or len(chunk.strip()) == 0:
                    continue
                
                # 使用现有的summerize函数对单个块进行总结
                chunk_summary = summerize(chunk, chunk_prompt_name, chunk_max_length)
                chunk_summaries.append(chunk_summary)
                logger.debug(f"第{i}个文本块总结完成，总结长度: {len(chunk_summary)}")
                
            except (ValueError, FileNotFoundError):
                # 重新抛出已知的异常类型，不进行包装
                raise
            except SummarizeError:
                # 重新抛出自定义异常，不进行包装
                raise
            except Exception as e:
                error_msg = f"总结第{i}个文本块时发生错误: {str(e)}"
                logger.error(error_msg)
                raise SummarizeError(error_msg) from e
        
        logger.info(f"第一阶段完成，生成了{len(chunk_summaries)}个块总结")
        
        # 第二阶段：合并所有块总结
        if len(chunk_summaries) == 1:
            # 如果只有一个块总结，仍需要进行最终总结以确保格式一致
            logger.debug("只有一个块总结，直接进行最终总结")
            combined_content = chunk_summaries[0]
        else:
            # 将所有块总结合并，使用双换行符分隔以保持结构清晰
            combined_content = '\n'.join(chunk_summaries)
            logger.debug(f"合并所有块总结，合并后长度: {len(combined_content)}")
        
        # 使用最终总结提示词对合并内容进行总结
        logger.info("开始第二阶段：对合并内容进行最终总结")
        try:
            final_summary = summerize(combined_content, summarize_chunk_prompt, final_max_length)
            logger.info(f"分批总结完成，最终总结长度: {len(final_summary)}")
            return final_summary
            
        except Exception as e:
            error_msg = f"最终总结阶段发生错误: {str(e)}"
            logger.error(error_msg)
            raise SummarizeError(error_msg) from e
            
    except (ValueError, FileNotFoundError):
        # 重新抛出已知的异常类型
        raise
    except SummarizeError:
        # 重新抛出自定义异常
        raise
    except Exception as e:
        # 捕获所有其他未预期的异常
        error_msg = f"分批总结过程中发生未知错误: {str(e)}"
        logger.error(error_msg)
        raise SummarizeError(error_msg) from e