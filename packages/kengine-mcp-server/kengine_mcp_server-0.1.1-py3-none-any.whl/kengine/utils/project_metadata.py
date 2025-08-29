"""
项目元数据管理模块

用于生成和管理项目元数据信息
支持新的分组数据结构和向后兼容性
"""

import json
import os
import logging
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
import re


class ProjectMetadataManager:
    """项目元数据管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 敏感信息模式列表
        self.sensitive_patterns = [
            r'key',              # 通用API密钥字段
            r'secret',               # 密钥字段
            r'token',                # 令牌字段
            r'password',   
            r'pwd'          # 密码字段
        ]
    
    def _sanitize_model_options(self, model_options: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理模型选项中的敏感信息
        
        Args:
            model_options: 原始模型选项
            
        Returns:
            清理后的模型选项
        """
        if not model_options:
            return {}
        
        return {key: '*****' if self._is_secret_key(key) else value for key, value in model_options.items()}
    
    def _is_secret_key(self, key: str) -> bool:
        for p in self.sensitive_patterns:
            if p in key.lower():
                return True
        return False
    
    def create_project_metadata(self,
                               local_path: str,
                               project_type: str,
                               git_repository: str,
                               git_branch: str = "master",
                               name: str = "",
                               group: str = "",
                               strategy: str = "",
                               model_name: str = "",
                               prompt_version: str = "",
                               model_options: Dict[str, Any] = None,
                               output_uri: str = "",
                               document_metadata_path: str = "",
                               status: str = "",
                               event: str = "",
                               event_time: str = "") -> Dict[str, Any]:
        """
        创建项目元数据字典
        
        Args:
            local_path: 本地项目路径
            project_type: 项目类型
            git_repository: Git仓库地址
            git_branch: Git分支
            name: 项目名称
            group: 项目组
            strategy: 生成策略
            model_name: 模型名称
            prompt_version: 提示词版本
            model_options: 模型选项
            output_uri: 输出路径
            document_metadata_path: 文档元数据路径
            status: 项目状态
            event: 事件类型（如 started、cloned、classified、completed、error 等）
            event_time: 事件时间
            
        Returns:
            项目元数据字典
        """
        if model_options is None:
            model_options = {}
        
        # 清理敏感信息
        sanitized_model_options = self._sanitize_model_options(model_options)
            
        return {
            # 基础项目信息
            "generated_at": datetime.now().isoformat(),
            "project_path": local_path,
            "project_type": project_type,
            "strategy": strategy,
            "git_repository_url": git_repository,
            "doc_output_base_path": output_uri,
            "name": name,
            "group": group,
            "status": status,
            "event": event,
            "event_time": event_time or datetime.now().isoformat(),
            # 文档生成信息 - 移到根级别，符合前端期望
            "document_generate_info": {
                "generated_time": datetime.now().isoformat(),
                "model_name": model_name,
                "prompt_version": prompt_version or "",
                "model_options": sanitized_model_options,
                "document_metadata_path": document_metadata_path
            },
            # 额外上下文信息
            "extra_context": {
                "git_branch": git_branch
            }
        }
    
    def save_project_metadata(self,
                             metadata: Dict[str, Any],
                             output_dir: str,
                             filename: str = "project_metadata.json") -> str:
        """
        保存项目元数据到文件，支持新的分组格式，基于group+name去重更新
        
        Args:
            metadata: 项目元数据
            output_dir: 输出目录
            filename: 文件名
            
        Returns:
            保存的文件路径
            
        Raises:
            OSError: 当文件写入失败时
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建文件路径
            file_path = os.path.join(output_dir, filename)
            
            # 加载现有的分组元数据
            grouped_data = self.load_all_project_metadata_grouped(file_path)
            
            # 获取项目信息
            new_group = metadata.get("group", "")
            new_name = metadata.get("name", "")
            
            if not new_group:
                new_group = "default"
            
            # 查找或创建对应的组织
            target_group = None
            for group_data in grouped_data:
                if group_data.get("group") == new_group:
                    target_group = group_data
                    break
            
            if target_group is None:
                # 创建新的组织
                target_group = {
                    "group": new_group,
                    "project_count": 0,
                    "created_time": datetime.now().isoformat(),
                    "updated_time": datetime.now().isoformat(),
                    "projects": []
                }
                grouped_data.append(target_group)
                self.logger.info(f"创建新的项目组织: {new_group}")
            
            # 在组织内查找是否存在相同的项目
            projects = target_group.get("projects", [])
            updated = False
            
            for i, existing_project in enumerate(projects):
                if existing_project.get("name") == new_name:
                    # 更新现有项目
                    projects[i] = metadata
                    updated = True
                    self.logger.info(f"更新已存在的项目元数据: {new_group}/{new_name}")
                    break
            
            if not updated:
                # 添加新项目
                projects.append(metadata)
                self.logger.info(f"添加新的项目元数据: {new_group}/{new_name}")
            
            # 更新组织统计信息
            target_group["projects"] = projects
            self._calculate_group_statistics(target_group)
                        
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(grouped_data, f, ensure_ascii=False, indent=4)
            return file_path
            
        except (OSError, IOError) as e:
            error_msg = f"无法保存项目元数据到 {output_dir}: {e}"
            self.logger.error(error_msg)
            raise OSError(error_msg) from e
    
    def load_all_project_metadata(self, file_path: str) -> List[Dict[str, Any]]:
        """
        从文件加载所有项目元数据（向后兼容方法）
        自动检测格式并返回扁平化的项目列表，保持与现有代码的兼容性
        
        Args:
            file_path: 元数据文件路径
            
        Returns:
            项目元数据列表，如果文件不存在或格式错误则返回空列表
        """
        try:
            if not os.path.exists(file_path):
                self.logger.info(f"项目元数据文件不存在，将创建新文件: {file_path}")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检测数据格式
            format_type = self._detect_metadata_format(data)
            
            if format_type == 'grouped':
                # 新格式：提取所有项目到扁平列表
                projects = []
                if isinstance(data, list):
                    for group_data in data:
                        if isinstance(group_data, dict) and 'projects' in group_data:
                            projects.extend(group_data['projects'])
                return projects
            else:
                # 旧格式：直接返回
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
                else:
                    self.logger.warning(f"项目元数据文件格式不正确: {file_path}")
                    return []
                
        except (json.JSONDecodeError, OSError, IOError) as e:
            self.logger.error(f"加载项目元数据失败 {file_path}: {e}")
            return []
    
    def load_project_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        从文件加载项目元数据（兼容性方法，返回第一个项目的元数据）
        
        Args:
            file_path: 元数据文件路径
            
        Returns:
            项目元数据字典，如果文件不存在或格式错误则返回None
        """
        all_metadata = self.load_all_project_metadata(file_path)
        return all_metadata[0] if all_metadata else None
    
    def find_project_metadata(self, file_path: str, group: str, name: str) -> Optional[Dict[str, Any]]:
        """
        根据group和name查找特定项目的元数据（向后兼容方法）
        
        Args:
            file_path: 元数据文件路径
            group: 项目组
            name: 项目名称
            
        Returns:
            匹配的项目元数据，如果未找到则返回None
        """
        # 优先使用新的分组查找方法
        result = self.find_project_by_group(file_path, group, name)
        if result:
            return result
        
        # 回退到旧方法（兼容性保证）
        all_metadata = self.load_all_project_metadata(file_path)
        
        for metadata in all_metadata:
            if metadata.get("group") == group and metadata.get("name") == name:
                return metadata
        
        return None
    
    def update_generation_info(self,
                              metadata: Dict[str, Any],
                              strategy: str = "",
                              model_name: str = "",
                              prompt_version: str = "",
                              model_options: Dict[str, Any] = None,
                              output_uri: str = "",
                              document_metadata_path: str = "") -> Dict[str, Any]:
        """
        更新元数据中的生成信息
        
        Args:
            metadata: 现有元数据
            strategy: 生成策略
            model_name: 模型名称
            prompt_version: 提示词版本
            model_options: 模型选项
            output_uri: 输出路径
            document_metadata_path: 文档元数据路径
            
        Returns:
            更新后的元数据
        """
        if model_options is None:
            model_options = {}
        
        # 清理敏感信息
        sanitized_model_options = self._sanitize_model_options(model_options)
            
        # 更新生成信息
        generation_info = metadata.get("document_generate_info", {})
        generation_info.update({
            "generated_time": datetime.now().isoformat(),
            "strategy": strategy,
            "model_name": model_name,
            "prompt_version": prompt_version or "",
            "model_options": sanitized_model_options,
            "output_uri": output_uri,
            "document_metadata_path": document_metadata_path
        })
        
        metadata["document_generate_info"] = generation_info
        return metadata
    
    def _detect_metadata_format(self, data: Any) -> str:
        """
        检测元数据格式类型
        
        Args:
            data: 元数据内容
            
        Returns:
            格式类型: 'legacy' (旧格式) 或 'grouped' (新分组格式)
        """
        if not isinstance(data, list):
            return 'legacy'
        
        if not data:
            return 'grouped'  # 空数据默认使用新格式
        
        # 检查第一个元素的结构
        first_item = data[0]
        if isinstance(first_item, dict):
            # 如果包含 'projects' 字段，则为新格式
            if 'projects' in first_item and 'group' in first_item:
                return 'grouped'
            # 如果包含 'local_path' 字段，则为旧格式
            elif 'local_path' in first_item:
                return 'legacy'
        
        return 'legacy'  # 默认为旧格式
    
    def _backup_original_file(self, file_path: str) -> str:
        """
        备份原始文件
        
        Args:
            file_path: 原始文件路径
            
        Returns:
            备份文件路径
            
        Raises:
            OSError: 当备份失败时
        """
        if not os.path.exists(file_path):
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"已备份原始文件: {backup_path}")
            return backup_path
        except (OSError, IOError) as e:
            error_msg = f"无法备份文件 {file_path}: {e}"
            self.logger.error(error_msg)
            raise OSError(error_msg) from e
    
    def _group_projects_by_organization(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将项目列表按组织分组
        
        Args:
            projects: 项目列表（旧格式）
            
        Returns:
            按组织分组的项目列表（新格式）
        """
        groups = {}
        
        for project in projects:
            group_name = project.get("group", "")
            if not group_name:
                group_name = "default"
            
            if group_name not in groups:
                groups[group_name] = {
                    "group": group_name,
                    "project_count": 0,
                    "created_time": datetime.now().isoformat(),
                    "updated_time": datetime.now().isoformat(),
                    "projects": []
                }
            
            groups[group_name]["projects"].append(project)
            groups[group_name]["project_count"] += 1
            
            # 更新组的时间信息
            project_created = project.get("created_time", "")
            if project_created and project_created < groups[group_name]["created_time"]:
                groups[group_name]["created_time"] = project_created
        
        return list(groups.values())
    
    def _calculate_group_statistics(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算组织级别的统计信息
        
        Args:
            group_data: 组织数据
            
        Returns:
            更新后的组织数据（包含统计信息）
        """
        projects = group_data.get("projects", [])
        group_data["project_count"] = len(projects)
        
        # 计算最早创建时间
        earliest_time = None
        latest_time = None
        
        for project in projects:
            created_time = project.get("created_time")
            if created_time:
                if earliest_time is None or created_time < earliest_time:
                    earliest_time = created_time
                if latest_time is None or created_time > latest_time:
                    latest_time = created_time
        
        if earliest_time:
            group_data["created_time"] = earliest_time
        if latest_time:
            group_data["updated_time"] = latest_time
        
        return group_data
    
    def _migrate_to_grouped_format(self, legacy_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将旧格式数据迁移到新的分组格式
        
        Args:
            legacy_data: 旧格式的项目列表
            
        Returns:
            新格式的分组项目列表
        """
        self.logger.info(f"开始迁移 {len(legacy_data)} 个项目到新的分组格式")
        
        # 按组织分组
        grouped_data = self._group_projects_by_organization(legacy_data)
        
        # 计算统计信息
        for group in grouped_data:
            self._calculate_group_statistics(group)
        
        self.logger.info(f"迁移完成，共创建 {len(grouped_data)} 个组织")
        return grouped_data
    
    def load_all_project_metadata_grouped(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载所有项目元数据（新格式，按组织分组）
        
        Args:
            file_path: 元数据文件路径
            
        Returns:
            按组织分组的项目元数据列表
        """
        try:
            
            
            if not os.path.exists(file_path):
                self.logger.info(f"项目元数据文件不存在，将创建新文件: {file_path}")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检测数据格式
            format_type = self._detect_metadata_format(data)
            
            if format_type == 'grouped':
                self.logger.info("检测到新格式数据，直接返回")
                return data if isinstance(data, list) else [data]
            else:
                self.logger.info("检测到旧格式数据，进行自动迁移")
                # 备份原文件
                self._backup_original_file(file_path)
                
                # 迁移到新格式
                legacy_projects = data if isinstance(data, list) else [data]
                grouped_data = self._migrate_to_grouped_format(legacy_projects)
                
                # 保存新格式数据
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(grouped_data, f, ensure_ascii=False, indent=4)
                
                self.logger.info(f"已自动迁移并保存新格式数据到: {file_path}")
                return grouped_data
                
        except (json.JSONDecodeError, OSError, IOError) as e:
            self.logger.error(f"加载项目元数据失败 {file_path}: {e}")
            return []
    
    def find_project_by_group(self, file_path: str, group: str, name: str) -> Optional[Dict[str, Any]]:
        """
        在新格式数据中根据组织和项目名查找项目
        
        Args:
            file_path: 元数据文件路径
            group: 项目组织
            name: 项目名称
            
        Returns:
            匹配的项目元数据，如果未找到则返回None
        """
        grouped_data = self.load_all_project_metadata_grouped(file_path)
        
        for group_data in grouped_data:
            if group_data.get("group") == group:
                for project in group_data.get("projects", []):
                    if project.get("name") == name:
                        return project
        
        return None
    
    def get_group_statistics(self, file_path: str, group: str = None) -> Dict[str, Any]:
        """
        获取组织统计信息
        
        Args:
            file_path: 元数据文件路径
            group: 指定组织名称，如果为None则返回所有组织的统计信息
            
        Returns:
            组织统计信息字典
        """
        grouped_data = self.load_all_project_metadata_grouped(file_path)
        
        if group:
            # 返回指定组织的统计信息
            for group_data in grouped_data:
                if group_data.get("group") == group:
                    return {
                        "group": group_data.get("group"),
                        "project_count": group_data.get("project_count", 0),
                        "created_time": group_data.get("created_time"),
                        "updated_time": group_data.get("updated_time")
                    }
            return {}
        else:
            # 返回所有组织的统计信息
            stats = {
                "total_groups": len(grouped_data),
                "total_projects": sum(g.get("project_count", 0) for g in grouped_data),
                "groups": []
            }
            
            for group_data in grouped_data:
                stats["groups"].append({
                    "group": group_data.get("group"),
                    "project_count": group_data.get("project_count", 0),
                    "created_time": group_data.get("created_time"),
                    "updated_time": group_data.get("updated_time")
                })
            
            return stats