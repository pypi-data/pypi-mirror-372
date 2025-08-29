"""
多Action输出解析器模块

提供ReAct风格的多Action输出解析功能，能够解析Agent输出中的多个Action-ActionInput对。
"""

import re
import logging
from typing import Union, List
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseOutputParser

from kengine.config import logging_config

logging_config.setup_logging()
logger = logging.getLogger(__name__)


class ReActMultiActionOutputParser(BaseOutputParser[Union[List[AgentAction], AgentFinish]]):
    """
    ReAct风格的多Action输出解析器
    
    能够解析包含多个Action-ActionInput对的Agent输出，支持以下格式：
    
    单Action格式：
    ```
    Thought: agent thought here
    Action: search
    Action Input: what is the temperature in SF?
    ```
    
    多Action格式：
    ```
    Thought: agent thought here
    Action: search
    Action Input: what is the temperature in SF?
    Action: calculator
    Action Input: 2 + 2
    ```
    
    Final Answer格式：
    ```
    Thought: agent thought here
    Final Answer: The temperature is 100 degrees
    ```
    """
    
    enable_fallback: bool = True
    
    def __init__(self, enable_fallback: bool = True, **kwargs):
        """
        初始化多Action解析器
        
        Args:
            enable_fallback: 是否启用回退机制，当解析失败时返回AgentFinish
        """
        super().__init__(enable_fallback=enable_fallback, **kwargs)
        
    def get_format_instructions(self) -> str:
        """获取格式说明"""
        return """Use the following format:

Thought: you should always think about what to do
Action: the action to take, should be one of the available tools
Action Input: the input to the action
... (this Action/Action Input pair can be repeated multiple times)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""

    def parse(self, text: str) -> Union[List[AgentAction], AgentFinish]:
        """
        解析Agent输出文本
        
        Args:
            text: Agent输出的文本
            
        Returns:
            Union[List[AgentAction], AgentFinish]: 解析结果
            
        Raises:
            OutputParserException: 解析失败时抛出
        """
        if text is None:
            if self.enable_fallback:
                logger.warning("输入文本为None，返回空AgentFinish")
                return AgentFinish({"output": ""}, "text is None")
            raise OutputParserException("输入文本不能为None")
        
        text = text.strip()
        
        # 检查中文"思考"和"行动"格式
        chinese_action_result = self._parse_chinese_thinking_action(text)
        if chinese_action_result:
            return chinese_action_result
        
        # 检查是否包含停止信息
        if 'Agent stopped due to iteration limit or time limit' in text:
            error_msg = 'Agent Error stopped due to iteration limit or time limit, Retry again!'
            if self.enable_fallback:
                logger.warning(f"检测到Agent停止信息: {error_msg}")
                return AgentFinish({"output": error_msg}, text)
            raise OutputParserException(error_msg)
        
        # 首先尝试解析Action，即使文本中包含Final Answer
        try:
            actions = self._parse_multiple_actions(text)
            if actions:
                logger.debug(f"成功解析到{len(actions)}个Action")
                return actions
            else:
                logger.debug("未解析到任何Action")
        except Exception as e:
            logger.error(f"解析Action时发生错误: {e}", exc_info=True)
        
        # 如果没有解析到Action，再检查Final Answer
        final_answer_text = 'Final Answer:'
        final_answer_idx = text.find(final_answer_text)
        if final_answer_idx > -1:
            output = text[final_answer_idx + len(final_answer_text):].strip()
            logger.debug(f"检测到Final Answer: {output[:100]}...")
            return AgentFinish({"output": output}, text)
        
        # 检查特殊格式（markdown, json, xml）
        if self._is_special_format(text):
            logger.debug("检测到特殊格式，返回AgentFinish")
            return AgentFinish({"output": text}, text)
        
        # 如果都没有匹配，使用回退机制
        logger.warning("未找到有效的Action或Final Answer")
        if self.enable_fallback:
            return AgentFinish({"output": text}, text)
        raise OutputParserException("未找到有效的Action或Final Answer")
    
    def _is_special_format(self, text: str) -> bool:
        """检查是否为特殊格式（markdown, json, xml）"""
        # 检查markdown格式
        markdown_pattern = r'```\s*markdown\s*.*?```'
        if re.search(markdown_pattern, text, re.IGNORECASE | re.DOTALL):
            return True
        
        # 检查JSON格式
        json_pattern = r'^\s*\{.*\}\s*$'
        if re.search(json_pattern, text, re.DOTALL):
            return True
        
        # 检查XML/HTML标签格式
        xml_tag_pattern = r'^\s*<([a-zA-Z][a-zA-Z0-9_-]*)[^>]*>.*?</\1>\s*$'
        if re.search(xml_tag_pattern, text, re.DOTALL):
            return True
            
        return False
    
    def _parse_multiple_actions(self, text: str) -> List[AgentAction]:
        """
        解析多个Action-ActionInput对
        
        Args:
            text: 要解析的文本
            
        Returns:
            List[AgentAction]: 解析出的Action列表
        """
        actions = []
        
        # 使用正则表达式匹配所有Action-ActionInput对
        # 支持Action和Action Input之间可能有数字编号
        action_pattern = r'Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*?)(?=Action\s*\d*\s*:|Final Answer:|Observation:|$)'
        
        matches = re.findall(action_pattern, text, re.DOTALL)
        
        for i, (action_name, action_input) in enumerate(matches):
            action_name = action_name.strip()
            action_input = action_input.strip()
            
            # 清理action_input中的引号和多余空白
            action_input = action_input.strip(' "\'')
            
            # 移除action_input末尾可能的换行和其他内容
            action_input = re.split(r'\n(?=Thought:|Action:|Observation:|Final Answer:)', action_input)[0].strip()
            
            if action_name and action_input:
                # 创建包含序号的日志信息
                log_text = f"Action {i+1}: {action_name}\nAction Input {i+1}: {action_input}"
                
                agent_action = AgentAction(
                    tool=action_name,
                    tool_input=action_input,
                    log=log_text
                )
                actions.append(agent_action)
                logger.debug(f"解析Action {i+1}: {action_name} -> {action_input[:50]}...")
        
        return actions
    
    def _parse_chinese_thinking_action(self, text: str) -> Union[List[AgentAction], None]:
        """
        解析中文"思考"和"行动"格式的文本
        
        支持格式：
        ```
        思考：[思考内容]
        行动：[行动描述]
        <ToolName>
        <param1>value1</param1>
        <param2>value2</param2>
        </ToolName>
        ```
        
        Args:
            text: 要解析的文本
            
        Returns:
            Union[List[AgentAction], None]: 解析出的Action列表，如果不匹配则返回None
        """
        import xml.etree.ElementTree as ET
        
        # 检查是否包含"思考"和"行动"关键词
        if '思考：' not in text or '行动：' not in text:
            return None
        
        try:
            # 提取思考部分
            thinking_match = re.search(r'思考：(.*?)(?=行动：|$)', text, re.DOTALL)
            thinking_content = thinking_match.group(1).strip() if thinking_match else ""
            
            # 提取行动部分
            action_match = re.search(r'行动：(.*?)(?=<[^>]+>|$)', text, re.DOTALL)
            action_description = action_match.group(1).strip() if action_match else ""
            
            # 提取XML工具调用
            xml_pattern = r'<([a-zA-Z][a-zA-Z0-9_-]*)[^>]*>(.*?)</\1>'
            xml_matches = re.findall(xml_pattern, text, re.DOTALL)
            
            if not xml_matches:
                logger.debug("未找到XML工具调用")
                return None
            
            actions = []
            for i, (tool_name, xml_content) in enumerate(xml_matches):
                try:
                    # 构建完整的XML字符串进行解析
                    full_xml = f'<{tool_name}>{xml_content}</{tool_name}>'
                    root = ET.fromstring(full_xml)
                    
                    # 提取参数
                    tool_input = {}
                    for child in root:
                        tool_input[child.tag] = child.text or ""
                    
                    # 创建日志文本
                    log_parts = []
                    if thinking_content:
                        log_parts.append(f"思考: {thinking_content}")
                    if action_description:
                        log_parts.append(f"行动: {action_description}")
                    log_parts.append(f"工具: {tool_name}")
                    log_parts.append(f"参数: {tool_input}")
                    
                    log_text = "\n".join(log_parts)
                    
                    # 创建AgentAction
                    agent_action = AgentAction(
                        tool=tool_name,
                        tool_input=tool_input,
                        log=log_text
                    )
                    actions.append(agent_action)
                    logger.debug(f"解析中文格式Action {i+1}: {tool_name} -> {str(tool_input)[:50]}...")
                    
                except ET.ParseError as e:
                    logger.warning(f"XML解析失败: {e}, 跳过工具调用: {tool_name}")
                    continue
                except Exception as e:
                    logger.warning(f"解析工具调用时发生错误: {e}, 跳过工具调用: {tool_name}")
                    continue
            
            return actions if actions else None
            
        except Exception as e:
            logger.error(f"解析中文思考行动格式时发生错误: {e}", exc_info=True)
            return None
    
    @property
    def _type(self) -> str:
        """返回解析器类型"""
        return "react-multi-action"


class EnhancedMultiActionOutputParser(ReActMultiActionOutputParser):
    """
    增强版多Action输出解析器
    
    在基础多Action解析器的基础上，添加了更多的错误处理和特殊情况处理。
    """
    
    max_actions: int = 10
    
    def __init__(self, enable_fallback: bool = True, max_actions: int = 10, **kwargs):
        """
        初始化增强版多Action解析器
        
        Args:
            enable_fallback: 是否启用回退机制
            max_actions: 最大Action数量限制
        """
        super().__init__(enable_fallback=enable_fallback, max_actions=max_actions, **kwargs)
    
    def parse(self, text: str) -> Union[List[AgentAction], AgentFinish]:
        """
        增强版解析方法
        
        Args:
            text: Agent输出的文本
            
        Returns:
            Union[List[AgentAction], AgentFinish]: 解析结果
        """
        result = super().parse(text)
        
        # 如果是Action列表，检查数量限制
        if isinstance(result, list) and len(result) > self.max_actions:
            logger.warning(f"Action数量({len(result)})超过限制({self.max_actions})，截取前{self.max_actions}个")
            result = result[:self.max_actions]
        
        return result
    
    @property
    def _type(self) -> str:
        """返回解析器类型"""
        return "enhanced-react-multi-action"