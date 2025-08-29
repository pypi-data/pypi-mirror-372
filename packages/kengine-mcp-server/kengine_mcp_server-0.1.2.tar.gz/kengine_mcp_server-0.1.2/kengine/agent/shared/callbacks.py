"""
增强版Agent回调处理器模块

在原有功能基础上增加了详细的LLM调用日志记录功能和大模型统计功能
"""

import logging
import re
import threading
import os
import json
import time
from uuid import UUID
from json import JSONEncoder
from langchain_core.messages import BaseMessage

class CustomJSONEncoder(JSONEncoder):
    """自定义JSON编码器，用于处理特殊类型的序列化"""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)
from datetime import datetime
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish



class ReactAgentLoggingHandler(BaseCallbackHandler):
    """React Agent执行过程的日志记录处理器，支持大模型统计"""
    
    def __init__(self, logger: Optional[logging.Logger] = None, session_name: str = "",
                 enable_file_logging: bool = True, log_dir: str = "logs/llm",
                 task_id: Optional[str] = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # 获取当前线程信息
        current_thread = threading.current_thread()
        thread_info = f"{current_thread.name}-{current_thread.ident}"
        
        # 将线程信息添加到session_name
        if session_name:
            self.session_name = f"{session_name}@{thread_info}"
        else:
            self.session_name = f"Agent@{thread_info}"
            
        self.iteration_count = 0
        self.tool_calls = 0
        self.tools_used = set()
        self.current_thought = ""
        
        # 文件日志相关配置
        self.enable_file_logging = enable_file_logging
        self.log_dir = log_dir
        self.llm_log_file = None
        
        # 初始化文件日志
        if self.enable_file_logging:
            self._init_file_logging()
        
        # LLM调用计数器
        self.llm_call_count = 0
        
        # 大模型统计相关
        self.task_id = task_id
        self.current_llm_start_time = None
        
        # 导入大模型统计管理器
        try:
            from kengine.core.llm_stats import llm_stats_manager
            from kengine.core.enums import LLMCallType
            self.llm_stats_manager = llm_stats_manager
            self.LLMCallType = LLMCallType
        except ImportError:
            self.logger.warning("无法导入大模型统计模块，统计功能将被禁用")
            self.llm_stats_manager = None
            self.LLMCallType = None
        
    def _init_file_logging(self):
        """初始化文件日志记录"""
        try:
            # 确保日志目录存在
            os.makedirs(self.log_dir, exist_ok=True)
            
            # 生成日志文件名：年月日时分-session_name.log
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d%H%M")
            clean_session_name = self._clean_filename(self.session_name.split('@')[0])
            filename = f"{timestamp}-{clean_session_name}.log"
            self.llm_log_file = os.path.join(self.log_dir, filename)
            
            # 写入日志文件头部信息
            with open(self.llm_log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== LLM调用日志 ===\n")
                f.write(f"会话名称: {self.session_name}\n")
                f.write(f"开始时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"时区: Asia/Shanghai (UTC+8:00)\n")
                f.write("=" * 50 + "\n\n")
                
        except Exception as e:
            self.logger.error(f"初始化文件日志失败: {e}")
            self.enable_file_logging = False
    
    def _clean_filename(self, filename: str) -> str:
        """清理文件名中的非法字符"""
        # 移除或替换文件名中的非法字符
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        return filename[:50]  # 限制长度
    
    
    def _truncate_content(self, content: str, max_length: int = 1000) -> str:
        """截断过长的内容"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + f"...(截断，总长度: {len(content)}字符)"
    
    def _extract_response_text(self, response: Any) -> str:
        """从response对象中提取文本内容"""
        try:
            if response is None:
                return "None"
            
            # 尝试不同的属性来获取响应文本
            if hasattr(response, 'generations') and response.generations:
                if hasattr(response.generations[0], 'text'):
                    return response.generations[0].text
                elif hasattr(response.generations[0], 'message'):
                    if hasattr(response.generations[0].message, 'content'):
                        return response.generations[0].message.content
            
            # 如果是字典类型
            if isinstance(response, dict):
                return json.dumps(response, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
            
            # 如果是字符串类型
            if isinstance(response, str):
                return response
            
            # 其他类型转换为字符串
            return str(response)
            
        except Exception as e:
            return f"提取响应内容失败: {e}"

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """LLM开始调用时记录"""
        try:
            self.llm_call_count += 1
            
            # 记录到文件
            if self.enable_file_logging:
                self._write_to_file(f"=== LLM调用 #{self.llm_call_count} 开始 ===")
                self._write_to_file(f"模型信息: {json.dumps(serialized, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
                
                # 安全处理prompts参数，防止None值
                if prompts is not None:
                    self._write_to_file(f"Prompt数量: {len(prompts)}")
                    for i, prompt in enumerate(prompts):
                        self._write_to_file(f"Prompt[{i}]: {prompt}")
                else:
                    self._write_to_file("Prompt数量: 0 (prompts为None)")
                    
                if kwargs:
                    self._write_to_file(f"额外参数: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
                self._write_to_file("")
                    
        except Exception as e:
            self.logger.error(f"🧠 [{self.session_name}] on_llm_start处理异常: {e}")
            if self.enable_file_logging:
                self._write_to_file(f"错误: on_llm_start处理异常: {e}")
        
    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """LLM调用结束时记录"""
        try:
            # 提取响应内容
            response_text = self._extract_response_text(response)
            
            # 更新大模型统计
            if self.llm_stats_manager and self.task_id and self.current_llm_start_time:
                duration = time.time() - self.current_llm_start_time
                output_tokens = len(response_text.split())  # 简单估算
                
                # 这里我们更新最近的调用记录
                # 注意：这是一个简化的实现，实际可能需要更复杂的跟踪机制
                
            # 记录到文件
            if self.enable_file_logging:
                self._write_to_file(f"=== LLM调用 #{self.llm_call_count} 完成 ===")
                self._write_to_file(f"响应内容: {response_text}")
                if kwargs:
                    self._write_to_file(f"额外参数: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
                self._write_to_file(f"响应长度: {len(response_text)}字符")
                self._write_to_file("=" * 50)
                self._write_to_file("")
                
        except Exception as e:
            self.logger.error(f"🧠 [{self.session_name}] on_llm_end处理异常: {e}")
            if self.enable_file_logging:
                self._write_to_file(f"错误: on_llm_end处理异常: {e}")

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """LLM调用出错时记录"""
        try:
            # 更新大模型统计（标记为失败）
            if self.llm_stats_manager and self.task_id and self.current_llm_start_time:
                duration = time.time() - self.current_llm_start_time
                
                # 记录失败的调用
                call_type = self.LLMCallType.OTHER if self.LLMCallType else "other"
                self.llm_stats_manager.record_call(
                    task_id=self.task_id,
                    call_type=call_type,
                    input_tokens=0,
                    output_tokens=0,
                    success=False,
                    duration=duration,
                    model_name="unknown",
                    stage=self._get_current_stage(),
                    error_message=str(error)
                )
            
            # 记录到文件
            if self.enable_file_logging:
                self._write_to_file(f"=== LLM调用 #{self.llm_call_count} 错误 ===")
                self._write_to_file(f"错误类型: {type(error).__name__}")
                self._write_to_file(f"错误信息: {str(error)}")
                if kwargs:
                    self._write_to_file(f"错误上下文: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
                self._write_to_file("=" * 50)
                self._write_to_file("")
                
        except Exception as e:
            self.logger.error(f"🧠 [{self.session_name}] on_llm_error处理异常: {e}")

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """当Agent选择执行某个Action时调用"""
        self.tool_calls += 1
        self.tools_used.add(action.tool)
        
        # 记录到文件
        if self.enable_file_logging:
            self._write_to_file(f"=== Agent Action #{self.tool_calls} ===")
            self._write_to_file(f"工具名称: {action.tool}")
            self._write_to_file(f"输入参数: {action.tool_input}")
            if hasattr(action, 'log') and action.log:
                thought = self._extract_thought_from_log(action.log)
                if thought:
                    self._write_to_file(f"思考过程: {thought}")
            if kwargs:
                self._write_to_file(f"额外参数: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
            self._write_to_file("")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """工具开始执行时调用"""
        if self.enable_file_logging:
            self._write_to_file(f"=== 工具执行开始 ===")
            self._write_to_file(f"工具信息: {json.dumps(serialized, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
            self._write_to_file(f"输入内容: {input_str}")
            if kwargs:
                self._write_to_file(f"额外参数: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
            self._write_to_file("")
            
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """工具执行完成时调用"""
        if self.enable_file_logging:
            self._write_to_file(f"=== 工具执行完成 ===")
            self._write_to_file(f"输出内容: {output}")
            if kwargs:
                self._write_to_file(f"额外参数: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
            self._write_to_file("")
        
    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """工具执行出错时调用"""
        if self.enable_file_logging:
            self._write_to_file(f"=== 工具执行错误 ===")
            self._write_to_file(f"错误类型: {type(error).__name__}")
            self._write_to_file(f"错误信息: {str(error)}")
            if kwargs:
                self._write_to_file(f"错误上下文: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
            self._write_to_file("")
            
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Agent完成执行时调用"""
        if self.enable_file_logging:
            self._write_to_file("=== Agent执行完成 ===")
            self._write_to_file(f"返回值: {json.dumps(finish.return_values, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
            self._write_to_file(f"日志: {finish.log if hasattr(finish, 'log') else 'None'}")
            self._write_to_file("\n=== 会话统计信息 ===")
            self._write_to_file(f"总迭代次数: {self.iteration_count}")
            self._write_to_file(f"总工具调用次数: {self.tool_calls}")
            self._write_to_file(f"总LLM调用次数: {self.llm_call_count}")
            self._write_to_file(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self._write_to_file("=" * 50)
            self._write_to_file("")
        
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        """链开始执行时调用"""
        if serialized and serialized.get('name') == 'AgentExecutor':
            self.iteration_count += 1
            self.logger.info(f"🚀 [{self.session_name}] Agent Iteration #{self.iteration_count} Started")
            
            # 将参数写入文件
            if self.enable_file_logging:
                self._write_to_file(f"=== Chain Start - Iteration #{self.iteration_count} ===")
                self._write_to_file(f"Serialized: {json.dumps(serialized, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
                self._write_to_file(f"Inputs: {json.dumps(inputs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
                if kwargs:
                    self._write_to_file(f"Additional Args: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
                self._write_to_file("")
            
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """链执行结束时调用"""
        if self.enable_file_logging:
            self._write_to_file(f"=== Chain End - Iteration #{self.iteration_count} ===")
            self._write_to_file(f"输出结果: {json.dumps(outputs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
            if kwargs:
                self._write_to_file(f"额外参数: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
            self._write_to_file("")

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """链执行出错时调用"""
        if self.enable_file_logging:
            self._write_to_file(f"=== Chain Error - Iteration #{self.iteration_count} ===")
            self._write_to_file(f"错误类型: {type(error).__name__}")
            self._write_to_file(f"错误信息: {str(error)}")
            if kwargs:
                self._write_to_file(f"错误上下文: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
            self._write_to_file("")
        
    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        **kwargs: Any,
    ) -> None:
        """聊天模型开始调用时记录"""
        try:
            self.llm_call_count += 1
            
            # 记录到文件
            if self.enable_file_logging:
                self._write_to_file(f"=== 聊天模型调用 #{self.llm_call_count} 开始 ===")
                self._write_to_file(f"模型信息: {json.dumps(serialized, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
                self._write_to_file(f"消息数量: {len(messages)}")
                for i, message_list in enumerate(messages):
                    self._write_to_file(f"消息组[{i}]:")
                    for msg in message_list:
                        self._write_to_file(f"  - 类型: {msg.type}")
                        self._write_to_file(f"    内容: {msg.content}")
                if kwargs:
                    self._write_to_file(f"额外参数: {json.dumps(kwargs, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")
                self._write_to_file("")
                    
        except Exception as e:
            self.logger.error(f"🧠 [{self.session_name}] on_chat_model_start处理异常: {e}")
            if self.enable_file_logging:
                self._write_to_file(f"错误: on_chat_model_start处理异常: {e}")
    
    def _extract_thought_from_log(self, log: str) -> str:
        """从Agent日志中提取Thought部分"""
        # 尝试匹配React格式的Thought
        thought_patterns = [
            r'Thought:\s*(.+?)(?=\nAction:|$)',
            r'I need to (.+?)(?=\nAction:|$)',
            r'Let me (.+?)(?=\nAction:|$)',
            r'First (.+?)(?=\nAction:|$)'
        ]
        
        for pattern in thought_patterns:
            match = re.search(pattern, log, re.DOTALL | re.IGNORECASE)
            if match:
                thought = match.group(1).strip()
                # 清理多余的空白字符
                thought = re.sub(r'\s+', ' ', thought)
                return thought
                
        return ""
    
    def _truncate_output(self, output: str, max_length: int = 200) -> str:
        """截断过长的输出"""
        if len(output) <= max_length:
            return output
            
        # 尝试在句号或换行符处截断
        truncate_pos = max_length
        for pos in [output.rfind('.', 0, max_length), output.rfind('\n', 0, max_length)]:
            if pos > max_length * 0.7:  # 确保不会截断得太短
                truncate_pos = pos + 1
                break
                
        return output[:truncate_pos] + "..."
    
    def get_session_stats(self) -> Dict[str, int]:
        """获取当前会话的统计信息"""
        return {
            "iterations": self.iteration_count,
            "tool_calls": self.tool_calls,
            "llm_calls": self.llm_call_count
        }
    
    def get_log_file_path(self) -> Optional[str]:
        """获取日志文件路径"""
        return self.llm_log_file if self.enable_file_logging else None
    
    def _infer_call_type(self, prompts: List[str]) -> str:
        """根据提示内容推断大模型调用类型"""
        if not self.LLMCallType:
            return "other"
            
        # 合并所有提示内容进行分析
        combined_prompt = " ".join(prompts).lower()
        
        # 根据关键词推断调用类型
        if any(keyword in combined_prompt for keyword in ["分类", "classify", "category", "类别"]):
            return self.LLMCallType.CLASSIFICATION
        elif any(keyword in combined_prompt for keyword in ["目录", "catalogue", "index", "toc"]):
            return self.LLMCallType.CATALOGUE_GENERATION
        elif any(keyword in combined_prompt for keyword in ["文档", "document", "生成", "generate"]):
            return self.LLMCallType.DOCUMENT_GENERATION
        elif any(keyword in combined_prompt for keyword in ["概述", "overview", "summary", "总结"]):
            return self.LLMCallType.OVERVIEW_GENERATION
        elif any(keyword in combined_prompt for keyword in ["检索", "search", "query", "rag"]):
            return self.LLMCallType.RAG_QUERY
        else:
            return self.LLMCallType.OTHER
    
    def _get_current_stage(self) -> str:
        """获取当前执行阶段"""
        # 这里可以根据实际情况返回更具体的阶段信息
        # 目前简单返回基于迭代次数的阶段
        if self.iteration_count <= 1:
            return "初始化"
        elif self.iteration_count <= 3:
            return "分析阶段"
        elif self.iteration_count <= 6:
            return "执行阶段"
        else:
            return "完善阶段"
    
    def _extract_response_text(self, response: Any) -> str:
        """提取LLM响应的文本内容"""
        try:
            if hasattr(response, 'content'):
                return str(response.content)
            elif hasattr(response, 'text'):
                return str(response.text)
            elif hasattr(response, 'generations') and response.generations:
                # 处理LangChain的LLMResult格式
                if hasattr(response.generations[0][0], 'text'):
                    return response.generations[0][0].text
            elif isinstance(response, str):
                return response
            else:
                return str(response)
        except Exception as e:
            self.logger.warning(f"提取响应文本失败: {e}")
            return str(response)
    
    def _write_to_file(self, content: str):
        """写入内容到日志文件"""
        if not self.enable_file_logging or not self.llm_log_file:
            return
            
        try:
            with open(self.llm_log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%H:%M:%S')
                f.write(f"[{timestamp}] {content}\n")
        except Exception as e:
            self.logger.error(f"写入日志文件失败: {e}")


    def get_tools_used(self) -> List[str]:
        """获取工具使用情况"""
        return self.tools_used
