"""
PRD文档搜索模块

在docs4demo目录中搜索与关键词相关的PRD文档，并提取相关信息
"""

import logging
import os
import re
import time
from typing import Dict, Any, List

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

def search_prd_documents(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    搜索PRD文档并提取相关信息
    
    Args:
        params: 处理后的参数字典，包含search_keywords和primary_keyword等
        
    Returns:
        Dict[str, Any]: PRD信息字典
    """
    # 如果不需要包含PRD信息，则返回空结果
    if not params.get("include_prd", True):
        return None
    
    search_keywords = params.get("search_keywords", [])
    primary_keyword = params.get("primary_keyword", "")
    
    # 初始化PRD信息，添加search_status字段
    prd_info = {
        "title": f"{primary_keyword}模块PRD",
        "description": "",
        "requirements": [],
        "business_rules": [],
        "search_status": "正在搜索相关PRD文档..."
    }
    
    try:
        # 使用绝对路径访问docs4demo目录
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        docs_path = os.path.join(base_dir, "docs4demo")
        logger.info(f"使用docs4demo目录: {docs_path}")
        
        # 检查docs4demo目录是否存在
        if not os.path.exists(docs_path) or not os.path.isdir(docs_path):
            logger.warning(f"docs4demo目录不存在: {docs_path}")
            # 尝试在当前工作目录下查找
            current_docs_path = os.path.join(os.getcwd(), "docs4demo")
            if os.path.exists(current_docs_path) and os.path.isdir(current_docs_path):
                docs_path = current_docs_path
                logger.info(f"使用当前工作目录下的docs4demo: {docs_path}")
            else:
                logger.warning(f"在当前工作目录下也未找到docs4demo目录: {current_docs_path}")
                prd_info["search_status"] = "未找到docs4demo目录，无法搜索PRD文档"
                return prd_info
        
        logger.info(f"开始查找PRD文档: {docs_path}")
        # 查找相关文档
        module_docs = find_matching_documents(docs_path, search_keywords)
        
        # 检查是否找到了匹配的文档
        if not module_docs:
            # 未找到任何匹配文档
            prd_info["search_status"] = "未找到匹配的PRD文档，请尝试其他关键词"
            logger.warning(f"未找到关于 '{primary_keyword}' 的任何PRD文档")
            return prd_info
        
        # 从文档中提取PRD信息
        # 记录开始时间，用于性能监控
        start_time = time.time()
        
        # 优化：使用列表推导式预先过滤匹配的文档，减少循环中的条件判断
        relevant_docs = [
            doc for doc in module_docs 
            if ("overview" in doc["filename"].lower() or 
                "business" in doc["filename"].lower() or 
                "order-fulfillment" in doc["filename"].lower() or
                any(kw.lower() in doc["filename"].lower() for kw in search_keywords))
        ]
        
        # 如果没有找到相关文档，尝试在所有文档中搜索
        if not relevant_docs:
            relevant_docs = module_docs
        
        # 记录匹配的文档数量
        prd_info["matched_docs"] = [doc["filename"] for doc in relevant_docs]
        found_match = False
        
        # 初始化 content 字段（如果不存在）
        if "content" not in prd_info:
            prd_info["content"] = ""
        
        # 处理所有匹配的文档
        for doc in relevant_docs:
            # 检查文件名是否包含关键词，或者是否是 order-fulfillment.md 文件
            if ("overview" in doc["filename"].lower() or 
                "business" in doc["filename"].lower() or 
                "order-fulfillment" in doc["filename"].lower() or
                any(kw.lower() in doc["content"].lower() for kw in search_keywords)):
                
                content = doc["content"]
                # 提取标题（如果尚未设置）
                if not prd_info["title"] or prd_info["title"] == f"{primary_keyword}模块PRD":
                    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                    if title_match:
                        prd_info["title"] = title_match.group(1)
                
                # 提取描述（如果尚未设置）
                if not prd_info["description"]:
                    desc_match = re.search(r"^(?!#)(.+?)$", content, re.MULTILINE)
                    if desc_match:
                        prd_info["description"] = desc_match.group(1).strip()
                
                # 存储完整文档内容（累积所有匹配文档的内容）
                if prd_info["content"]:
                    prd_info["content"] += "\n\n--- 分隔线：新文档 ---\n\n"
                prd_info["content"] += f"# 文件：{doc['filename']}\n\n{content}"
                
                # 提取需求和规则（累积收集）
                requirements = []
                rules = []
                
                # 查找列表项
                list_items = re.findall(r"^-\s+(.+)$", content, re.MULTILINE)
                if list_items:
                    for i, item in enumerate(list_items):
                        # 优化：使用集合去重，避免重复添加相同的需求或规则
                        if "需求" in item or "功能" in item or i % 2 == 0:
                            if item not in prd_info.get("requirements", []) and len(prd_info.get("requirements", [])) < 10:
                                requirements.append(item)
                        elif "规则" in item or "限制" in item:
                            if item not in prd_info.get("business_rules", []) and len(prd_info.get("business_rules", [])) < 5:
                                rules.append(item)
                
                # 合并需求和规则
                if "requirements" not in prd_info:
                    prd_info["requirements"] = []
                if "business_rules" not in prd_info:
                    prd_info["business_rules"] = []
                    
                prd_info["requirements"].extend(requirements)
                prd_info["business_rules"].extend(rules)
                
                # 标记找到匹配
                found_match = True
                
                # 记录日志
                logger.info(f"处理文档: {doc['filename']}, 提取了 {len(requirements)} 个需求和 {len(rules)} 个规则")
        
        # 更新搜索状态
        if found_match:
            prd_info["search_status"] = f"成功找到相关PRD文档，共处理 {len(relevant_docs)} 个文档"
        else:
            prd_info["search_status"] = "未找到匹配的PRD文档，请尝试其他关键词"
        
        # 记录处理时间
        processing_time_ms = round((time.time() - start_time) * 1000, 2)
        prd_info["processing_time_ms"] = processing_time_ms
        logger.info(f"PRD信息提取完成，处理时间: {processing_time_ms}ms, 找到 {len(relevant_docs)} 个相关文档")
        
    except Exception as e:
        logger.error(f"搜索PRD文档失败: {str(e)}", exc_info=True)
        prd_info["search_status"] = f"搜索PRD文档过程中发生错误: {str(e)}"
    
    return prd_info

def find_matching_documents(docs_path: str, search_keywords: List[str]) -> List[Dict[str, Any]]:
    """
    在指定目录中查找与关键词匹配的文档
    
    Args:
        docs_path: 文档目录路径
        search_keywords: 搜索关键词列表
        
    Returns:
        List[Dict[str, Any]]: 匹配的文档列表，每个文档包含路径、内容和文件名
    """
    module_docs = []
    
    try:
        for root, _, files in os.walk(docs_path):
            for file in files:
                # 只处理 Markdown 文件
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        # 尝试多种编码读取文件
                        encodings = ['utf-8', 'gbk', 'latin-1']
                        content = None
                        
                        for encoding in encodings:
                            try:
                                with open(file_path, 'r', encoding=encoding) as f:
                                    content = f.read()
                                    break
                            except UnicodeDecodeError:
                                continue
                        
                        if not content:
                            continue
                            
                        # 检查文件名、目录名或文件内容是否包含任一搜索关键词
                        file_matches = False
                        for keyword in search_keywords:
                            if (keyword.lower() in file.lower() or
                                keyword.lower() in os.path.basename(root).lower() or
                                keyword.lower() in content.lower()):  # 新增：检查文件内容
                                file_matches = True
                                logger.info(f"找到匹配文件: {file_path}, 匹配关键词: {keyword}")
                                break
                        
                        if file_matches:
                            # 文件内容已经读取，直接添加到结果中
                            module_docs.append({
                                "path": file_path,
                                "content": content,
                                "filename": file
                            })
                            logger.info(f"找到匹配文档: {file_path}")
                    except Exception as e:
                        logger.error(f"处理文档失败: {file_path}, 错误: {str(e)}")
    except Exception as e:
        logger.error(f"遍历docs4demo目录失败: {str(e)}", exc_info=True)
    
    return module_docs