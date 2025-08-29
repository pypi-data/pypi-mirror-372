"""
目录压缩算法模块

提供智能目录压缩功能，支持：
1. Maven 标准目录结构压缩（src/main/java、src/test/resources 等）
2. Java 包结构压缩（com/company/project 等）  
3. 通用单链路径压缩

该模块被 markdown_generator.py 和 tree_builder.py 共同使用，避免代码重复。
"""

from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple


class DirectoryCompressor:
    """
    目录压缩器类
    
    提供各种目录压缩策略的统一接口
    """
    
    def __init__(self):
        """初始化压缩器"""
        pass
    
    def compress_tree(self, tree: Dict, enable_compression: bool = True) -> List[Dict]:
        """
        对目录树进行压缩处理
        
        Args:
            tree (Dict): 目录树结构
            enable_compression (bool): 是否启用压缩功能
            
        Returns:
            List[Dict]: 压缩后的路径信息列表，每个元素包含：
                - type: 'compressed' 或 'normal'
                - path: 压缩后的路径字符串（仅compressed类型）
                - children: 子项字典
                - tree: 原始树结构（仅normal类型）
                - compression_info: 压缩信息（可选）
        """
        if not enable_compression or not tree.get('children') or tree['type'] != 'directory':
            return self._convert_to_normal_items(tree.get('children', []))
        
        children = tree['children']
        compressed_results = []
        processed_children = set()
        
        # 按名称排序子项，确保处理顺序一致
        sorted_children = sorted(children, key=lambda x: x['name'])
        
        # 首先检查当前节点是否是src节点，如果是则直接应用Maven压缩
        if tree['name'] == 'src':
            maven_result = self._compress_maven_structure(tree['name'], tree)
            if maven_result:
                return maven_result
        
        for child_tree in sorted_children:
            child_name = child_tree['name']
            if child_name in processed_children:
                continue
                
            # 尝试不同的压缩策略
            compression_result = None
            
            # 策略1: Maven标准目录结构压缩
            if child_name == 'src':
                compression_result = self._compress_maven_structure(child_name, child_tree)
            # 策略2: Java包结构压缩
            elif self._is_java_package_structure(child_tree):
                compression_result = self._compress_java_package_structure(child_name, child_tree)
            
            # 策略3: 通用单链路径压缩
            elif self._is_single_chain_directory(child_tree):
                compression_result = self._compress_single_chain_path(child_name, child_tree)
            
            if compression_result:
                # Maven结构返回的是列表，需要特殊处理
                if isinstance(compression_result, list):
                    compressed_results.extend(compression_result)
                else:
                    compressed_results.append(compression_result)
                processed_children.add(child_name)
            else:
                # 无法压缩，正常显示
                compressed_results.append({
                    'type': 'normal',
                    'tree': child_tree,
                    'compression_info': {'strategy': 'none', 'reason': 'no_applicable_pattern'}
                })
                processed_children.add(child_name)
        
        return compressed_results
    
    def _convert_to_normal_items(self, children: List) -> List[Dict]:
        """
        将子项转换为正常显示的格式
        
        Args:
            children (List): 子项列表
            
        Returns:
            List[Dict]: 正常显示的项目列表
        """
        return [
            {
                'type': 'normal',
                'tree': child_tree,
                'compression_info': {'strategy': 'none', 'reason': 'compression_disabled'}
            }
            for child_tree in sorted(children, key=lambda x: x['name'])
        ]
    
    def _compress_maven_structure(self, root_name: str, tree: Dict) -> Optional[List[Dict]]:
        """
        压缩Maven标准目录结构
        
        识别并压缩如下结构：
        - src/main/java
        - src/main/resources
        - src/test/java
        - src/test/resources
        - target/classes
        等
        
        Args:
            root_name (str): 根目录名（通常是'src'）
            tree (Dict): 目录树结构
            
        Returns:
            Optional[List[Dict]]: 压缩结果列表，如果无法压缩则返回None
        """
        if root_name != 'src' or tree['type'] != 'directory':
            return None
        
        children = tree.get('children', [])
        if not children:
            return None
        
        # 将数组格式转换为字典格式以便查找
        children_dict = {child['name']: child for child in children}
        
        # Maven标准路径模式
        maven_patterns = [
            ['main', 'java'],
            ['main', 'resources'],
            ['test', 'java'],
            ['test', 'resources'],
            ['main', 'webapp']
        ]
        
        compressed_paths = []
        processed_top_level = set()
        
        for pattern in maven_patterns:
            current = tree
            current_dict = children_dict
            path_exists = True
            
            # 检查路径是否存在
            for part in pattern:
                if part in current_dict:
                    current = current_dict[part]
                    current_dict = {child['name']: child for child in current.get('children', [])}
                else:
                    path_exists = False
                    break
            
            if path_exists:
                # 构建压缩路径
                compressed_path = f"{root_name}/" + "/".join(pattern)
                compressed_paths.append({
                    'type': 'compressed',
                    'path': compressed_path,
                    'children': current.get('children', []),
                    'compression_info': {
                        'strategy': 'maven',
                        'pattern': pattern,
                        'original_depth': len(pattern) + 1
                    }
                })
                # 标记顶级目录已处理
                processed_top_level.add(pattern[0])
        
        # 处理剩余的子目录（不符合Maven模式的）
        remaining_items = []
        for child in children:
            if child['name'] not in processed_top_level:
                remaining_items.append({
                    'type': 'normal',
                    'tree': child,
                    'compression_info': {'strategy': 'none', 'reason': 'not_maven_pattern'}
                })
        
        # 合并压缩路径和剩余项目
        result = compressed_paths + remaining_items
        
        return result if result else None
    
    def _compress_java_package_structure(self, root_name: str, tree: Dict) -> Optional[Dict]:
        """
        压缩Java包结构
        
        识别并压缩如下结构：
        - com/company/project
        - org/apache/commons
        - net/sf/json
        等
        
        Args:
            root_name (str): 根目录名
            tree (Dict): 目录树结构
            
        Returns:
            Optional[Dict]: 压缩结果，如果无法压缩则返回None
        """
        if tree['type'] != 'directory':
            return None
        
        # 检查是否是Java包结构的开始
        java_package_prefixes = ['com', 'org', 'net', 'io', 'cn']
        
        if root_name not in java_package_prefixes:
            return None
        
        # 获取完整的包路径
        package_path = self._get_java_package_chain(root_name, tree)
        
        if len(package_path) >= 3:  # 至少要有3层才值得压缩 (如 com/company/project)
            # 找到链的末端
            current = tree
            for part in package_path[1:]:  # 跳过根名称
                # 在children列表中查找对应的子项
                children = current.get('children', [])
                current = next((child for child in children if child['name'] == part), None)
                if current is None:
                    return None
            
            compressed_path = "/".join(package_path)
            
            return {
                'type': 'compressed',
                'path': compressed_path,
                'children': current.get('children', []),
                'compression_info': {
                    'strategy': 'java_package',
                    'package_path': package_path,
                    'original_depth': len(package_path)
                }
            }
        
        return None
    
    def _compress_single_chain_path(self, root_name: str, tree: Dict) -> Optional[Dict]:
        """
        压缩通用单链路径结构
        
        对于只有单一子目录的连续路径进行压缩
        
        Args:
            root_name (str): 根目录名
            tree (Dict): 目录树结构
            
        Returns:
            Optional[Dict]: 压缩结果，如果无法压缩则返回None
        """
        if tree['type'] != 'directory':
            return None
        
        chain_path = self._get_single_directory_chain(root_name, tree)
        
        # 只有当链长度大于等于2时才进行压缩
        if len(chain_path) >= 2:
            # 找到链的末端
            current = tree
            for part in chain_path[1:]:  # 跳过根名称
                # 在children列表中查找对应的子项
                children = current.get('children', [])
                current = next((child for child in children if child['name'] == part), None)
                if current is None:
                    return None
            
            compressed_path = "/".join(chain_path)
            
            return {
                'type': 'compressed',
                'path': compressed_path,
                'children': current.get('children', []),
                'compression_info': {
                    'strategy': 'single_chain',
                    'chain_path': chain_path,
                    'original_depth': len(chain_path)
                }
            }
        
        return None
    
    def _is_java_package_structure(self, tree: Dict) -> bool:
        """
        判断是否是Java包结构
        
        Args:
            tree (Dict): 目录树结构
            
        Returns:
            bool: 如果是Java包结构返回True
        """
        if tree['type'] != 'directory':
            return False
        
        # Java包通常以这些前缀开始
        java_package_prefixes = ['com', 'org', 'net', 'io', 'cn']
        
        return tree['name'] in java_package_prefixes
    
    def _is_single_chain_directory(self, tree: Dict) -> bool:
        """
        判断是否是单链目录结构（只有一个子目录的连续结构）
        
        Args:
            tree (Dict): 目录树结构
            
        Returns:
            bool: 如果是单链目录结构返回True
        """
        if tree['type'] != 'directory':
            return False
        
        children = tree.get('children', [])
        
        # 必须只有一个子项，且该子项是目录
        if len(children) != 1:
            return False
        
        child_tree = children[0]
        
        # 子项必须是目录
        if child_tree['type'] != 'directory':
            return False
        
        # 递归检查子目录是否也是单链结构
        child_children = child_tree.get('children', [])
        
        # 如果子目录有多个子项，或者有文件，则停止链式检查
        if len(child_children) > 1:
            return True  # 这里仍然返回True，因为至少有一层可以压缩
        
        # 如果子目录也只有一个子目录，继续检查
        if len(child_children) == 1:
            next_child = child_children[0]
            if next_child['type'] == 'directory':
                return True
        
        return len(child_children) == 0  # 空目录也可以压缩
    
    def _get_java_package_chain(self, root_name: str, tree: Dict) -> List[str]:
        """
        获取Java包的完整链路径
        
        Args:
            root_name (str): 根目录名
            tree (Dict): 目录树结构
            
        Returns:
            List[str]: 包路径列表
        """
        chain = [root_name]
        current = tree
        
        while True:
            children = current.get('children', [])
            
            # 如果没有子项或有多个子项，停止
            if len(children) != 1:
                break
            
            child_tree = children[0]
            
            # 如果子项不是目录，停止
            if child_tree['type'] != 'directory':
                break
            
            # 检查子目录是否包含Java文件或其他非目录项
            child_children = child_tree.get('children', [])
            has_non_directory = any(
                child['type'] != 'directory'
                for child in child_children
            )
            
            # 如果包含非目录项且有多个子项，这可能是包的末端
            if has_non_directory and len(child_children) > 1:
                chain.append(child_tree['name'])
                break
            
            # 如果只有目录，继续链式
            if len(child_children) == 1 and not has_non_directory:
                chain.append(child_tree['name'])
                current = child_tree
            else:
                chain.append(child_tree['name'])
                break
        
        return chain
    
    def _get_single_directory_chain(self, root_name: str, tree: Dict) -> List[str]:
        """
        获取单目录链的完整路径
        
        Args:
            root_name (str): 根目录名
            tree (Dict): 目录树结构
            
        Returns:
            List[str]: 目录链路径列表
        """
        chain = [root_name]
        current = tree
        
        while True:
            children = current.get('children', [])
            
            # 如果没有子项或有多个子项，停止
            if len(children) != 1:
                break
            
            child_tree = children[0]
            
            # 如果子项不是目录，停止
            if child_tree['type'] != 'directory':
                break
            
            chain.append(child_tree['name'])
            current = child_tree
            
            # 检查下一层是否还是单链
            next_children = current.get('children', [])
            if len(next_children) != 1:
                break
            
            next_child = next_children[0]
            if next_child['type'] != 'directory':
                break
        
        return chain


# 全局压缩器实例
_compressor = DirectoryCompressor()




