"""
应用程序配置模块

提供全面的应用程序配置管理功能，包括分类、策略和全局设置
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class ApplicationConfig:
    """应用程序配置管理器（只读）
    
    统一管理应用程序的所有配置，包括：
    - 项目分类配置
    - 文档生成策略配置
    - 全局应用设置
    - 模型配置
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化应用程序配置
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认配置
        """
        self.config_file = config_file or self._get_default_config_path()
        self._config_data  = {}
        self._classifications = {}
        self._models_configs = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "config" / "application_config.json")
    
    def _load_config(self) -> None:
        """加载应用程序配置"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"应用程序配置文件不存在: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config_data = json.load(f)
                logger.info(f"成功加载应用程序配置文件: {self.config_file}")

            # 遍历配置项， 对于 格式为 {env:ABC}的配置项的值， 根据环境变量进行替换
            self._config_data = self._replace_env_variables(self._config_data)
            
            
            self._classifications = self._config_data.get('classifications', {})
            self._models_configs = self._config_data.get('model_configs', {})
                
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise RuntimeError(f"加载应用程序配置失败: {e}")
    
    def _replace_env_variables(self, data: Any) -> Any:
        """
        递归替换配置中的环境变量
        
        支持两种格式：
        1. {env:VARIABLE_NAME} - 环境变量不存在时抛出异常
        2. {env:VARIABLE_NAME:default_value} - 环境变量不存在时使用默认值
        
        示例：
        - "{env:API_KEY}" - 必须设置 API_KEY 环境变量
        - "{env:PORT:8080}" - 如果 PORT 未设置，使用默认值 8080
        - "{env:BASE_URL:http://localhost}" - 如果 BASE_URL 未设置，使用默认 URL
        
        Args:
            data: 要处理的数据（可以是字典、列表、字符串等）
            
        Returns:
            处理后的数据
            
        Raises:
            ValueError: 当环境变量不存在且没有提供默认值时抛出异常
        """
        if isinstance(data, dict):
            # 处理字典类型
            result = {}
            for key, value in data.items():
                result[key] = self._replace_env_variables(value)
            return result
        elif isinstance(data, list):
            # 处理列表类型
            return [self._replace_env_variables(item) for item in data]
        elif isinstance(data, str):
            # 处理字符串类型，查找并替换环境变量
            return self._replace_env_in_string(data)
        else:
            # 其他类型直接返回
            return data
    
    def _replace_env_in_string(self, text: str) -> str:
        """
        在字符串中替换环境变量
        
        支持两种格式：
        1. {env:VARIABLE_NAME} - 环境变量不存在时抛出异常
        2. {env:VARIABLE_NAME:default_value} - 环境变量不存在时使用默认值
        
        Args:
            text: 包含环境变量引用的字符串
            
        Returns:
            替换后的字符串
            
        Raises:
            ValueError: 当环境变量不存在且没有提供默认值时抛出异常
        """
        # 使用正则表达式匹配环境变量格式，支持空格和默认值
        # 支持格式：
        # {env:ABC}, { env : ABC }, {env : ABC}, { env:ABC}, { env: ABC }
        # {env:ABC:default}, {env:ABC:1}, {env:ABC:http://localhost}
        env_pattern = r'\{\s*env\s*:\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*([^}]*))?\s*\}'
        
        def replace_match(match):
            env_var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else None
            
            # 去除默认值两端的空格
            if default_value is not None:
                default_value = default_value.strip()
            
            env_value = os.getenv(env_var_name)
            
            # 如果环境变量存在且不为空，直接使用
            if env_value is not None and env_value != '':
                logger.debug(f"替换环境变量: {env_var_name} -> {env_value}")
                return env_value
            
            # 如果环境变量不存在或为空，检查是否有默认值
            if default_value is not None:
                logger.debug(f"环境变量 '{env_var_name}' 未设置，使用默认值: {default_value}")
                return default_value
            
            # 如果没有默认值，抛出异常
            error_msg = f"环境变量 '{env_var_name}' 未设置或为空，且未提供默认值"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            # 执行替换
            result = re.sub(env_pattern, replace_match, text)
            return result
        except ValueError:
            # 重新抛出环境变量相关的错误
            raise
        except Exception as e:
            error_msg = f"替换环境变量时发生错误: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_enabled_classifications(self) -> List[str]:
        """获取启用的分类列表"""
        return list(self._classifications.keys())
    
    def get_all_classifications(self) -> List[str]:
        """获取所有分类列表"""
        return list(self._classifications.keys())
    
    def get_classification_info(self, category_name: str) -> Optional[Dict[str, Any]]:
        """获取分类详细信息"""
        return self._classifications.get(category_name)
    
    def get_classification_generation_strategy(self, category_name: str) -> Optional[str]:
        """
        获取分类的生成策略
        
        Args:
            category_name: 分类名称
            
        Returns:
            生成策略字符串或None
        """
        category_info = self.get_classification_info(category_name)
        if category_info:
            strategy_name = category_info.get('generation_strategy')
            return strategy_name
        return None
    
    def get_project_strategy_mapping(self) -> Dict[str, str]:
        """
        获取项目类型到生成策略的映射
        
        Returns:
            项目类型到策略的映射字典
        """
        mapping = {}
        for category_name in self._classifications.keys():
            strategy = self.get_classification_generation_strategy(category_name)
            if strategy:
                mapping[category_name] = strategy
        return mapping
    
    def get_strategy_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有策略配置
        
        Returns:
            策略配置字典
        """
        return self._config_data.get('strategy_configs', {})
    
    def get_strategy_config(self, strategy: str) -> Dict[str, Any]:
        """
        获取特定策略的配置
        
        Args:
            strategy: 策略名称 ('prompt', 'agent')
            
        Returns:
            策略配置字典
        """
        strategy_configs = self.get_strategy_configs()
        return strategy_configs.get(strategy, {}).copy()

    
    def validate_classfication(self, classification_name: str) -> bool:
        """
        验证分类是否有效
        
        Args:
            category_name: 分类名称
            
        Returns:
            是否有效
        """
        return classification_name in self._classifications
    
    def get_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有模型配置
        
        Returns:
            模型配置字典
        """
        return self._config_data.get('model_configs', {})
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        获取特定模型的配置
        
        Args:
            model_name: 模型名称 (如 'gpt-4', 'claude-3-5-sonnet')
            
        Returns:
            模型配置字典
        """
        model_configs = self.get_model_configs()
        if model_name in model_configs:
            return model_configs[model_name].copy()
        
        # 如果未找到指定模型，返回默认配置
        default_config = model_configs.get('default', {})
        if default_config:
            return default_config.copy()
        
        raise ValueError(f"未找到模型 '{model_name}' 的配置，且未设置默认配置")
    
    def get_default_model_config(self) -> Dict[str, Any]:
        """
        获取默认模型配置
        
        Returns:
            默认模型配置字典
        """
        return self.get_model_config('default')
    
    def get_available_model_names(self) -> List[str]:
        """
        获取所有可用的模型名称
        
        Returns:
            模型名称列表
        """
        model_configs = self.get_model_configs()
        return [name for name in model_configs.keys() if name != 'default']
    
    
    def get(self, key, default_value=None):
        return self._config_data.get(key, default_value)
    
   

# 全局配置实例
_application_config = None

def get_application_config() -> ApplicationConfig:
    """获取全局应用程序配置实例"""
    global _application_config
    if _application_config is None:
        _application_config = ApplicationConfig()
    return _application_config


# 保持向后兼容性的别名
def get_classification_config() -> ApplicationConfig:
    """获取全局分类配置实例（已废弃，请使用 get_application_config）"""
    return get_application_config()

