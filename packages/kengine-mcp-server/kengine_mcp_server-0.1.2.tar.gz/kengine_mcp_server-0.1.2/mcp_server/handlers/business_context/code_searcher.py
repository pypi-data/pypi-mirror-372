"""
代码信息搜索模块

使用RAG向量库查询相关代码信息
"""

import logging
import os
import re
import time
from typing import Dict, Any, List, Optional

# 获取日志记录器
logger = logging.getLogger("kengine_mcp_server")

def search_code_information(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    搜索代码信息
    
    Args:
        params: 处理后的参数字典，包含search_keywords和primary_keyword等
        
    Returns:
        Dict[str, Any]: 代码信息字典
    """
    # 如果不需要包含代码信息，则返回空结果
    if not params.get("include_code", True):
        return None
    
    search_keywords = params.get("search_keywords", [])
    primary_keyword = params.get("primary_keyword", "")
    method_name = params.get("method_name", "")
    
    # 初始化代码信息
    code_info = {
        "file_paths": [],
        "main_classes": [],
        "key_methods": [method_name] if method_name else [],
        "dependencies": []
    }
    
    try:
        logger.info("开始查询代码信息")
        
        # 使用绝对路径访问项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # 加载.env文件中的环境变量
        load_environment_variables(base_dir)
        
        # 对每个关键词进行RAG查询，合并结果
        all_code_results = []
        
        # 使用两种搜索方式：
        # 1. 对于代码相关内容，使用RAG向量搜索.kb目录
        # 2. 对于文档，直接在docs4demo目录中搜索
        
        # 首先，使用RAG向量搜索.kb目录
        kb_dir = os.path.join(base_dir, ".kb")
        vector_store_path = os.path.join(kb_dir, "app/eclp-isv/")
        
        # 检查必要的环境变量是否存在
        check_and_set_environment_variables()
        
        if os.path.exists(vector_store_path):
            # 使用RAGService向量搜索
            all_code_results.extend(search_with_rag_service(vector_store_path, search_keywords))
        elif os.path.exists(kb_dir) and os.path.isdir(kb_dir):
            # 如果向量库不存在，但.kb目录存在，则使用SimpleRAG作为备选方案
            all_code_results.extend(search_with_simple_rag(kb_dir, search_keywords))
        else:
            logger.warning(f".kb目录不存在: {kb_dir}")
        
        # 如果RAG查询没有找到足够的结果，使用普通文本搜索docs4demo目录
        if len(all_code_results) < 2:
            docs_path = os.path.join(base_dir, "docs4demo")
            if os.path.exists(docs_path) and os.path.isdir(docs_path):
                all_code_results.extend(search_with_text_search(docs_path, search_keywords))
        
        # 去重（基于文件路径）
        seen_paths = set()
        code_results = []
        for result in all_code_results:
            if result["path"] not in seen_paths:
                seen_paths.add(result["path"])
                code_results.append(result)
        
        # 限制结果数量
        code_results = code_results[:5]
        logger.info(f"找到 {len(code_results)} 个代码文件")
        
        # 添加日志：检查最终结果
        for i, result in enumerate(code_results):
            path = result.get("path", "")
            content = result.get("content", "")
            logger.info(f"最终结果 {i+1}: 路径={path}, 内容长度={len(content)}")
        
        # 提取代码信息
        for code_doc in code_results:
            file_path = code_doc.get("path", "")
            if file_path and file_path not in code_info["file_paths"]:
                code_info["file_paths"].append(file_path)
            
            # 简单解析类名和方法名
            content = code_doc.get("content", "")
            
            # 添加日志：检查文件内容是否为空
            if not content:
                logger.warning(f"文件内容为空: {file_path}")
            else:
                logger.info(f"处理文件内容: {file_path}, 内容长度={len(content)}")
                
                # 提取类名
                extract_classes(content, code_info)
                
                # 提取方法名
                extract_methods(content, code_info, method_name)
                
                # 提取依赖
                extract_dependencies(content, code_info)
        
        # 如果没有找到任何信息，返回明确的提示而不是假数据
        if not code_info["file_paths"] and not code_info["main_classes"] and len(code_info["key_methods"]) <= 1:
            # 记录未找到数据的情况
            logger.warning(f"未找到关于 '{primary_keyword}' 的任何代码信息")
            
            # 返回明确的提示信息
            code_info = {
                "file_paths": [],
                "main_classes": [],
                "key_methods": code_info["key_methods"],  # 保留可能已有的方法名
                "dependencies": [],
                "search_status": "未找到匹配数据，请尝试其他关键词或检查 .kb 目录是否包含相关向量数据"
            }
        else:
            # 如果找到了部分信息，可以适当补充
            if not code_info["file_paths"]:
                # 不使用假路径，而是返回空列表
                logger.info("未找到文件路径信息")
            if not code_info["main_classes"]:
                # 不使用假类名，而是返回空列表
                logger.info("未找到类名信息")
            if len(code_info["key_methods"]) <= 1:
                # 只保留已有的方法名，不添加假方法
                logger.info("未找到足够的方法信息")
            if not code_info["dependencies"]:
                # 不使用假依赖，而是返回空列表
                logger.info("未找到依赖信息")
            
            # 添加文件内容到code_info中
            if code_results:
                code_info["file_contents"] = []
                for result in code_results:
                    path = result.get("path", "")
                    content = result.get("content", "")
                    if content:
                        # 限制内容长度，避免返回过大
                        max_content_length = 2000
                        if len(content) > max_content_length:
                            content = content[:max_content_length] + "... (内容已截断)"
                        
                        code_info["file_contents"].append({
                            "path": path,
                            "content": content,
                            "is_test_file": result.get("is_test_file", False)
                        })
                        logger.info(f"添加文件内容到结果: {path}, 内容长度: {len(content)}")
        
    except Exception as e:
        logger.error(f"RAG查询失败: {str(e)}", exc_info=True)
        # 返回错误信息而不是默认值
        code_info = {
            "file_paths": [],
            "main_classes": [],
            "key_methods": [method_name] if method_name else [],
            "dependencies": [],
            "error": f"RAG查询失败: {str(e)}",
            "search_status": "查询过程中发生错误，请检查日志获取详细信息"
        }
    
    return code_info

def load_environment_variables(base_dir: str) -> None:
    """
    加载环境变量
    
    Args:
        base_dir: 项目根目录
    """
    try:
        from dotenv import load_dotenv
        
        dotenv_path = os.path.join(base_dir, '.env')
        if os.path.exists(dotenv_path):
            logger.info(f"从 {dotenv_path} 加载环境变量")
            load_dotenv(dotenv_path)
            logger.info(f"成功加载环境变量，JDL_ROUTER_BASE={os.environ.get('JDL_ROUTER_BASE', '未设置')}")
        else:
            logger.warning(f".env文件不存在: {dotenv_path}")
    except ImportError:
        logger.warning("未安装python-dotenv库，无法加载.env文件")
    except Exception as e:
        logger.error(f"加载.env文件失败: {str(e)}")

def check_and_set_environment_variables() -> None:
    """
    检查并设置必要的环境变量
    """
    # 检查必要的环境变量是否存在
    required_env_vars = ['JDL_ROUTER_BASE']
    missing_env_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_env_vars:
        logger.warning(f"环境变量 {', '.join(missing_env_vars)} 未设置，使用默认值")
        # 设置默认环境变量值
        if 'JDL_ROUTER_BASE' not in os.environ:
            os.environ['JDL_ROUTER_BASE'] = 'http://airouter.jdl.com'  # 使用.env文件中的值

def search_with_rag_service(vector_store_path: str, search_keywords: List[str]) -> List[Dict[str, Any]]:
    """
    使用RAGService进行向量搜索
    
    Args:
        vector_store_path: 向量库路径
        search_keywords: 搜索关键词列表
        
    Returns:
        List[Dict[str, Any]]: 搜索结果列表
    """
    all_results = []
    
    try:
        logger.info(f"使用RAGService向量搜索，向量库路径: {vector_store_path}")
        
        # 导入RAG相关模块
        from kengine.rag import RAGService
        from kengine.rag.config import RAGConfig
        
        # 创建RAG配置
        config = RAGConfig()
        
        # 创建RAGService实例
        rag_service = RAGService(config)
        
        # 加载向量库
        rag_service.load_knowledge_base(vector_store_path)
        
        # 对每个关键词进行RAG查询，合并结果
        for keyword in search_keywords:
            logger.info(f"RAGService查询关键词: {keyword}")
            try:
                # 使用RAGService进行相似度搜索
                # 增加k值以获取更多结果，提高找到非test文件的概率
                results = rag_service.similarity_search(keyword, k=10)
                
                # 转换结果格式以兼容现有代码，并添加日志
                filtered_results = []
                test_files = []
                non_test_files = []
                
                for result in results:
                    path = result.get("source", "")
                    content = result.get("content", "")
                    content_length = len(content)
                    
                    # 检查是否为test目录文件
                    if "test" in path.lower():
                        logger.warning(f"RAGService发现test目录文件: {path}, 内容长度: {content_length}")
                        test_files.append(path)
                        # 不立即跳过，而是保存以备后用
                    else:
                        logger.info(f"RAGService搜索结果(非test): 路径={path}, 内容长度={content_length}")
                        non_test_files.append(path)
                        
                        # 添加到过滤结果列表
                        filtered_results.append({
                            "path": path,
                            "content": content,
                            "relevance_score": 0.8,  # 默认相关性分数
                            "filename": result.get("filename", "")
                        })
                
                # 如果没有找到非test文件，但有test文件，则使用test文件（但添加警告）
                if not filtered_results and test_files:
                    logger.warning(f"未找到非test目录文件，将使用test目录文件作为备选，共 {len(test_files)} 个")
                    for result in results:
                        path = result.get("source", "")
                        if "test" in path.lower():
                            filtered_results.append({
                                "path": path,
                                "content": result.get("content", ""),
                                "relevance_score": 0.7,  # 降低相关性分数
                                "filename": result.get("filename", ""),
                                "is_test_file": True  # 标记为test文件
                            })
                
                all_results.extend(filtered_results)
                logger.info(f"RAGService查询关键词 '{keyword}' 找到 {len(filtered_results)} 个结果（过滤后），非test文件: {len(non_test_files)}，test文件: {len(test_files)}")
            except Exception as e:
                logger.error(f"RAGService查询关键词 '{keyword}' 失败: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"RAGService向量搜索失败: {str(e)}", exc_info=True)
    
    return all_results

def search_with_simple_rag(kb_dir: str, search_keywords: List[str]) -> List[Dict[str, Any]]:
    """
    使用SimpleRAG进行搜索
    
    Args:
        kb_dir: 知识库目录
        search_keywords: 搜索关键词列表
        
    Returns:
        List[Dict[str, Any]]: 搜索结果列表
    """
    all_results = []
    
    try:
        logger.warning(f"向量库不存在，使用similarity_search作为备选方案")
        logger.info(f"使用similarity_search搜索.kb目录: {kb_dir}")
        
        # 导入RAG相关模块
        from kengine.rag import similarity_search
        
        # 对每个关键词进行RAG查询
        for keyword in search_keywords:
            logger.info(f"SimpleRAG查询关键词: {keyword}")
            try:
                # 限制只在.kb目录中搜索，避免搜索整个系统
                # 增加max_results以获取更多结果
                results = similarity_search(keyword, kb_dir, max_results=10)
                
                # 添加日志：检查结果中是否包含test目录的文件
                test_files = []
                non_test_files = []
                
                for result in results:
                    path = result.get("path", "")
                    content_length = len(result.get("content", ""))
                    if "test" in path.lower():
                        logger.warning(f"SimpleRAG发现test目录文件: {path}, 内容长度: {content_length}")
                        test_files.append(result)
                    else:
                        logger.info(f"SimpleRAG搜索结果(非test): 路径={path}, 内容长度={content_length}")
                        non_test_files.append(result)
                
                # 优先使用非test文件
                if non_test_files:
                    all_results.extend(non_test_files)
                    logger.info(f"SimpleRAG查询关键词 '{keyword}' 找到 {len(non_test_files)} 个非test文件")
                else:
                    # 如果没有非test文件，则使用test文件（但添加警告）
                    if test_files:
                        logger.warning(f"SimpleRAG未找到非test目录文件，将使用test目录文件作为备选，共 {len(test_files)} 个")
                        all_results.extend(test_files)
                
                logger.info(f"SimpleRAG查询关键词 '{keyword}' 总共找到 {len(results)} 个结果，非test文件: {len(non_test_files)}，test文件: {len(test_files)}")
            except Exception as e:
                logger.error(f"SimpleRAG查询关键词 '{keyword}' 失败: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"SimpleRAG搜索失败: {str(e)}", exc_info=True)
    
    return all_results

def search_with_text_search(docs_path: str, search_keywords: List[str]) -> List[Dict[str, Any]]:
    """
    使用普通文本搜索
    
    Args:
        docs_path: 文档目录
        search_keywords: 搜索关键词列表
        
    Returns:
        List[Dict[str, Any]]: 搜索结果列表
    """
    all_results = []
    
    logger.info(f"RAG查询结果不足，使用普通文本搜索docs4demo目录: {docs_path}")
    
    for keyword in search_keywords:
        logger.info(f"文本搜索关键词: {keyword}")
        try:
            # 直接在docs4demo目录中搜索
            keyword_results = []
            test_files = []
            
            for root, _, files in os.walk(docs_path):
                for file in files:
                    if keyword.lower() in file.lower() or keyword.lower() in os.path.basename(root).lower():
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
                            
                            if content:
                                # 检查是否为test目录文件
                                if "test" in file_path.lower():
                                    logger.warning(f"文本搜索发现test目录文件: {file_path}, 内容长度: {len(content)}")
                                    # 保存test文件，但不立即添加到结果中
                                    test_files.append({
                                        "path": file_path,
                                        "content": content,
                                        "score": 0.7,  # 降低相关性分数
                                        "is_test_file": True
                                    })
                                else:
                                    keyword_results.append({
                                        "path": file_path,
                                        "content": content,
                                        "score": 0.8  # 模拟相关性分数
                                    })
                                    logger.info(f"找到匹配文件(非test): {file_path}, 内容长度: {len(content)}")
                        except Exception as e:
                            logger.error(f"读取文件失败: {file_path}, 错误: {str(e)}")
            
            # 如果没有找到非test文件，但有test文件，则使用test文件
            if not keyword_results and test_files:
                logger.warning(f"文本搜索未找到非test目录文件，将使用test目录文件作为备选，共 {len(test_files)} 个")
                keyword_results.extend(test_files)
            
            # 限制每个关键词的结果数量
            keyword_results = keyword_results[:5]
            all_results.extend(keyword_results)
            logger.info(f"关键词 '{keyword}' 找到 {len(keyword_results)} 个匹配文件")
        except Exception as e:
            logger.error(f"处理关键词 '{keyword}' 失败: {str(e)}", exc_info=True)
    
    return all_results

def extract_classes(content: str, code_info: Dict[str, Any]) -> None:
    """
    从代码内容中提取类名
    
    Args:
        content: 代码内容
        code_info: 代码信息字典，将被修改
    """
    class_matches = re.findall(r"class\s+(\w+)", content)
    for cls in class_matches:
        if cls not in code_info["main_classes"]:
            code_info["main_classes"].append(cls)

def extract_methods(content: str, code_info: Dict[str, Any], method_name: Optional[str] = None) -> None:
    """
    从代码内容中提取方法名
    
    Args:
        content: 代码内容
        code_info: 代码信息字典，将被修改
        method_name: 要特别关注的方法名
    """
    method_matches = re.findall(r"def\s+(\w+)", content)
    for method in method_matches:
        if method not in code_info["key_methods"] and method_name and method.lower() == method_name.lower():
            code_info["key_methods"].append(method)

def extract_dependencies(content: str, code_info: Dict[str, Any]) -> None:
    """
    从代码内容中提取依赖
    
    Args:
        content: 代码内容
        code_info: 代码信息字典，将被修改
    """
    import_matches = re.findall(r"import\s+(\w+)", content)
    for imp in import_matches:
        if imp not in code_info["dependencies"]:
            code_info["dependencies"].append(imp)