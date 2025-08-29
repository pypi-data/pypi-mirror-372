

from typing import Any, Dict, List, Optional
from kengine.config.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

"""
为catalogue数据处理提供utils函数， catalogue_data 是一个树形结构， children 为子节点
{
  "title": "Application Documentation Structure",
  "description": "Comprehensive documentation catalog generated through systematic agent analysis",
  "items": [
    {
      "title": "Document Section Title(Avoid purely technical terms such as: interface, API, message, MQ)",
      "name": "document-filename",
      "prompt": "Detailed, specific prompt for generating this documentation section based on discovered information. Include specific file references and implementation details found during analysis.",
      "relatedFilenames": ["related_file1", "related_file2", "related_fileX"],
      "children": [
        {
          "title": "Subsection Title(Avoid purely technical terms such as: interface, API, message, MQ)", 
          "name": "subsection-filename",
          "prompt": "Specific prompt for subsection content with concrete findings from tool analysis",
          "relatedFilenames": ["related_file1", "related_file2", "related_fileX"],
        }
      ]
    }
  ]
}
"""


def count_documents_in_catalogue(catalogue_data: Dict[str, Any]) -> int:
    """递归计算目录中的文档数量"""
    if not isinstance(catalogue_data, dict) or "items" not in catalogue_data:
        return 0
    
    count = 0
    items = catalogue_data.get("items", [])
    
    # 验证items是否为列表
    if not isinstance(items, list):
        return 0
    
    for item in items:
        # 验证item是否为有效的字典且包含必要字段
        if not isinstance(item, dict) or "name" not in item:
            continue
            
        # 每个有效项目都算作一个文档
        count += 1
        
        # 递归计算子项目
        if "children" in item and isinstance(item["children"], list) and item["children"]:
            child_catalogue = {"items": item["children"]}
            count += count_documents_in_catalogue(child_catalogue)
    
    return count

def find_document_item_in_catalogue(document_path: str,
                                    catalogue_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证参数并查找文档项的公共逻辑
    
    Args:
        document_path: 文档在目录结构中的路径
        catalogue_data: 文档目录结构数据
        
    Returns:
        找到的文档项
        
    Raises:
        ValueError: 当参数验证失败时抛出
        KeyError: 当catalogue_data缺少必要字段时抛出
        RuntimeError: 当未找到指定文档项时抛出
    """
    # 参数验证
    if not document_path:
        raise ValueError("document_path 不能为空")
        
    if not catalogue_data:
        raise ValueError("catalogue_data 不能为空")
        
    if "items" not in catalogue_data:
        raise KeyError("catalogue_data 缺少 items 字段")

    items = catalogue_data["items"]
    
    # 验证items是否为列表
    if not isinstance(items, list):
        raise KeyError("catalogue_data 的 items 字段必须是列表类型")

    def _find_document_item_by_path(document_path: str,
                                    items: List[Dict[str, Any]],
                                    current_path: str = "") -> Optional[Dict[str, Any]]:
        
        for item in items:
            # 验证item是否为有效的字典且包含name字段
            if not isinstance(item, dict) or "name" not in item:
                continue
                
            # 构建当前项的完整路径
            item_path = f"{current_path}/{item['name']}" if current_path else item['name']
            
            # 如果路径匹配，返回该项
            if item_path == document_path:
                return item
            
            # 递归搜索子项
            if "children" in item and isinstance(item["children"], list):
                found_item = _find_document_item_by_path(document_path, item["children"], item_path)
                if found_item:
                    return found_item
        
        return None
    
    # 根据document_path找到对应的文档项
    document_item = _find_document_item_by_path(document_path, catalogue_data["items"])
    if not document_item:
        raise RuntimeError(f"未找到文档项: {document_path}")
        
    return document_item


def set_catalogue_saved_path(document_path: str, catalogue_data: Dict[str, Any], saved_path: str) -> None:
    """
    更新 catalogue_data 中指定文档项的 saved_path 属性
    
    Args:
        document_path: 文档在目录结构中的路径
        catalogue_data: 文档目录结构数据
        saved_path: 生成文档的保存路径
        
    Raises:
        ValueError: 当参数验证失败时抛出
        KeyError: 当catalogue_data缺少必要字段时抛出
        RuntimeError: 当未找到指定文档项时抛出
    """
    try:
        # 使用现有的验证和查找逻辑
        document_item = find_document_item_in_catalogue(document_path, catalogue_data)
        # 为找到的文档项添加 saved_path 属性
        document_item["saved_path"] = saved_path
        logger.debug(f"已为文档项 {document_path} 添加 saved_path: {saved_path}")
    except Exception as e:
        logger.error(f"更新 catalogue_data 失败: {document_path}, 错误: {e}")
        raise
    
def filter_catalogue_by_path(catalogue_data: Dict[str, Any], specify_document_path: Optional[str]) -> Dict[str, Any]:
    """
    根据指定路径过滤目录数据，保留匹配的目录项及其子项
    
    Args:
        catalogue_data: 目录数据，格式为 {"items": [...]}
        specify_document_path: 指定的文档路径，格式如 "overview/business"
                               如果为None或空字符串，则返回原始数据
        
    Returns:
        Dict[str, Any]: 过滤后的目录数据，格式为 {"items": [...]}
        
    Raises:
        ValueError: 当catalogue_data为None或格式不正确时抛出
        TypeError: 当参数类型不正确时抛出
        
    Example:
        >>> catalogue_data = {
        ...     "items": [
        ...         {"name": "overview", "title": "项目概览", "children": [...]}
        ...     ]
        ... }
        >>> filtered = filter_catalogue_by_path(catalogue_data, "overview/business")
        >>> # 返回只包含匹配路径的过滤数据
    """
    # 参数验证
    if catalogue_data is None:
        raise ValueError("catalogue_data 不能为 None")
        
    if not isinstance(catalogue_data, dict):
        raise TypeError("catalogue_data 必须是字典类型")
        
    if specify_document_path is not None and not isinstance(specify_document_path, str):
        raise TypeError("specify_document_path 必须是字符串类型或 None")
    
    # 如果没有指定路径或目录数据为空，返回原始数据
    if not catalogue_data or not specify_document_path:
        logger.debug("未指定过滤路径或目录数据为空，返回原始数据")
        return catalogue_data
        
    # 验证catalogue_data结构
    if "items" not in catalogue_data:
        logger.warning("catalogue_data 缺少 'items' 字段，返回原始数据")
        return catalogue_data
        
    catalogue_items = catalogue_data.get("items", [])
    if not isinstance(catalogue_items, list):
        logger.warning("items 不是列表类型，返回原始数据")
        return catalogue_data
        
    # 创建过滤后的数据结构
    filtered_data = {"items": []}
    
    # 解析指定路径
    path_parts = specify_document_path.strip('/').split('/')
    if not path_parts or path_parts == ['']:
        logger.debug("路径解析后为空，返回原始数据")
        return catalogue_data
        
    logger.info(f"开始过滤目录，指定路径: {specify_document_path}")
    
    def _find_matching_items(items: List[Dict[str, Any]], 
                           path_parts: List[str], 
                           current_level: int = 0) -> List[Dict[str, Any]]:
        """
        递归查找匹配指定路径的目录项
        
        Args:
            items: 当前层级的目录项列表
            path_parts: 路径分段列表
            current_level: 当前递归层级
            
        Returns:
            List[Dict[str, Any]]: 匹配的目录项列表
        """
        matching_items = []
        
        # 如果已经超过路径深度，返回所有项
        if current_level >= len(path_parts):
            return items
            
        target_name = path_parts[current_level]
        logger.debug(f"在第{current_level}层查找目标: {target_name}")
        
        for item in items:
            # 验证item结构
            if not isinstance(item, dict) or "name" not in item:
                logger.warning(f"跳过无效的目录项: {item}")
                continue
                
            if item.get('name') == target_name:
                logger.debug(f"找到匹配项: {item.get('name')}")
                
                # 如果还有更深层的路径，继续递归查找
                if current_level < len(path_parts) - 1:
                    if 'children' in item and isinstance(item['children'], list):
                        child_matches = _find_matching_items(
                            item['children'],
                            path_parts,
                            current_level + 1
                        )
                        # 只有当子路径找到匹配时，才创建父级项
                        if child_matches:
                            matched_item = {
                                "title": item.get("title"),
                                "name": item.get("name"),
                                "prompt": item.get("prompt"),
                                "relatedFilenames": item.get("relatedFilenames", []),
                                "children": child_matches
                            }
                            # 保留其他可能的字段
                            for key, value in item.items():
                                if key not in ["title", "name", "prompt", "children"]:
                                    matched_item[key] = value
                            matching_items.append(matched_item)
                            logger.debug(f"创建父级项: {item.get('name')} (包含{len(child_matches)}个子项)")
                    else:
                        logger.debug(f"路径 {'/'.join(path_parts[:current_level+2])} 不存在，跳过")
                        # 如果没有children但还有更深层路径，说明路径不存在
                        # 不添加任何项到matching_items
                else:
                    # 到达目标层级，创建匹配项
                    matched_item = {
                        "title": item.get("title"),
                        "name": item.get("name"),
                        "prompt": item.get("prompt"),
                        "relatedFilenames": item.get("relatedFilenames", [])
                    }
                    # 包含所有子项（如果存在）
                    if 'children' in item and isinstance(item['children'], list):
                        matched_item['children'] = item['children']
                        logger.debug(f"包含完整子树: {item.get('name')} (包含{len(item['children'])}个子项)")
                    
                    # 保留其他可能的字段
                    for key, value in item.items():
                        if key not in ["title", "name", "prompt", "children"]:
                            matched_item[key] = value
                            
                    matching_items.append(matched_item)
                    logger.debug(f"创建目标项: {item.get('name')}")
                
                break  # 找到匹配项后跳出循环
                
        return matching_items

    # 查找匹配的目录项
    filtered_items = _find_matching_items(catalogue_items, path_parts)
    filtered_data["items"] = filtered_items
    
    if filtered_items:
        logger.info(f"成功过滤目录，找到 {len(filtered_items)} 个匹配项")
    else:
        logger.warning(f"未找到匹配路径 '{specify_document_path}' 的目录项")
        
    return filtered_data