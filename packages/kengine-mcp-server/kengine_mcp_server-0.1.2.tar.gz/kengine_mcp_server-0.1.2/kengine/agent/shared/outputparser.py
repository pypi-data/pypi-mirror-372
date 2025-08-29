

import re
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain_core.agents import AgentAction, AgentFinish

import logging
from kengine.config import logging_config

logging_config.setup_logging()
logger = logging.getLogger(__name__)

class EnhancedAgentOutputParser(ReActSingleInputOutputParser):
    
    def parse(self, text):
        if text is None:
            return AgentFinish({"output": ""}, "text is None")
        
        text = text.strip()
        
        if 'Agent stopped due to iteration limit or time limit' in text:
            raise RuntimeError('Agent Error stopped due to iteration limit or time limit, Retry again!')
        
        final_answer_text = 'Final Answer:'
        final_answer_idx =  text.find(final_answer_text)
        if final_answer_idx > -1:
            output = text[final_answer_idx + len(final_answer_text):]
            return AgentFinish({"output": output}, text)
        
        # 如果text匹配 ```markdown ``` 格式，则返回AgentFinish
        markdown_pattern = r'```\s*markdown\s*.*?```'
        if re.search(markdown_pattern, text, re.IGNORECASE | re.DOTALL):
            logger.debug("Detected markdown code block format, returning AgentFinish")
            return AgentFinish({"output": text}, text)
        
        # 如果text匹配 json格式 { } ，则返回AgentFinish
        json_pattern = r'^\s*\{.*\}\s*$'
        if re.search(json_pattern, text, re.DOTALL):
            logger.debug("Detected JSON format, returning AgentFinish")
            return AgentFinish({"output": text}, text)
        
        # 如果text匹配 <tag> 任意字符 </tag> 格式，则返回AgentFinish
        xml_tag_pattern = r'<([a-zA-Z][a-zA-Z0-9_-]*)[^>]*>.*?</\1>'
        if re.search(xml_tag_pattern, text, re.DOTALL):
            logger.debug("Detected XML/HTML tag format, returning AgentFinish")
            return AgentFinish({"output": text}, text)
        
        # if has output return AgentFinish
        try:        
            return super().parse(text)
        except Exception as e:
            logger.error(f"Error parsing agent output: {text}", exc_info=True)
            
            return AgentFinish({"output": text}, text)