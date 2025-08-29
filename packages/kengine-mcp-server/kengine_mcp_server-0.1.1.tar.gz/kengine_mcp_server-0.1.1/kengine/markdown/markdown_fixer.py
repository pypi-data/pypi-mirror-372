def extract_markdown_content(markdown: str) -> str:
    """
    修复markdown中的语法错误
    
    错误案例1：
    
下面是返回内容

```markdown

真正的内容主题在这里

```
后面可能有一些总结性的文本

    需要保留 第一个 ```markdown  和最后一个 \n``` 之间的内容
    
    """
    if not markdown or not isinstance(markdown, str):
        return ""
    
    # 查找第一个 ```markdown 标记
    start_marker = "```markdown"
    start_index = markdown.find(start_marker)
    
    if start_index == -1:
        # 如果没有找到 ```markdown 标记，返回原始内容
        return markdown
    
    # 从 ```markdown 后开始查找内容
    content_start = start_index + len(start_marker)
    
    # 查找最后一个 \n``` 标记
    end_marker = "\n```"
    end_index = markdown.rfind(end_marker)
    
    if end_index == -1 or end_index < content_start:
        # 如果没有找到结束标记，或者结束标记在开始标记之前，返回原始内容
        return markdown
    
    # 提取内容（不包括开始和结束的换行符）
    content = markdown[content_start:end_index]
    
    # 大模型返回的markdown中有可能包含如下内容， 需要删除包含如下内容的一行， 最多有一行
    # Thought: I now know the final answer
    content = _remove_thought_line(content)
    
    # 去除开头和结尾的空白字符，但保留内部格式
    content = content.strip()
    
    return content


def _remove_thought_line(content: str) -> str:
    """
    删除包含 'Thought: I now know the final answer' 的行，最多删除一行
    
    Args:
        content (str): 需要处理的markdown内容
        
    Returns:
        str: 处理后的内容
        
    Raises:
        TypeError: 当输入不是字符串类型时抛出异常
    """
    if not isinstance(content, str):
        raise TypeError("输入内容必须是字符串类型")
    
    if not content:
        return content
    
    # 目标匹配文本
    target_text = "Thought: I now know the final answer"
    # 按行分割内容
    lines = content.split('\n')
    
    # 查找包含目标文本的行（只删除第一个匹配的行）
    for i, line in enumerate(lines):
        if target_text in line:
            # 找到匹配行，删除该行
            lines.pop(i)
            
            # 处理删除行后可能产生的连续空行问题
            # 如果删除的行前后都是空行，则删除其中一个空行以避免产生过多空行
            if (i > 0 and i < len(lines) and
                lines[i-1].strip() == '' and lines[i].strip() == ''):
                lines.pop(i)
            
            break  # 只删除第一个匹配的行
    
    # 重新组合内容
    result = '\n'.join(lines)
    return result