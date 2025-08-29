"""
数据库配置提取和查询工具

该模块提供从指定目录中提取数据库配置信息的功能。核心类DatabaseConfigExtractor
能够解析Spring配置文件，连接数据库并执行查询操作。
工具从当前目录或指定目录中自动获取项目名称，无需显式指定项目名称。

功能特点:
- 从指定目录中搜索项目的数据库配置信息
- 解析Spring配置文件和属性文件
- 根据环境优先级选择合适的配置
- 连接数据库并执行表结构查询

使用方法:
    python -m tools.db_extractor
    python -m tools.db_extractor --table user_info
"""

import argparse
import json
import logging
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .base import BasePathTool
from .error_handler import ErrorHandler, handle_tool_errors
from .exceptions import ConfigurationError
from kengine.config import logging_config

logging_config.setup_logging()
logger = logging.getLogger(__name__)


def validate_table_name(table_name: str) -> bool:
    """
    验证表名是否合法，防止SQL注入
    
    Args:
        table_name: 要验证的表名
        
    Returns:
        bool: 表名是否合法
        
    Raises:
        ValueError: 表名不合法时抛出异常
    """
    if not table_name or not isinstance(table_name, str):
        raise ValueError("表名不能为空且必须是字符串")
        
    if not re.fullmatch(r'^[a-zA-Z0-9_]+$', table_name):
        raise ValueError(f"表名 '{table_name}' 包含非法字符，仅允许字母、数字和下划线")
    
    return True


class DatabaseConfig:
    """数据库配置类"""

    def __init__(self, name: str, url: str, username: str, password: str, driver: str):
        self.name = name
        self.url = url
        self.username = username
        self.password = password
        self.driver = driver

    def __str__(self):
        return f"DataSource[{self.name}]: {self.url} (user: {self.username})"


class DatabaseConfigExtractor:
    """数据库配置提取器"""

    def __init__(self, base_dir: str = "."):
        self.base_path = Path(base_dir)
        # 环境优先级：测试 > UAT > 灰度 > 开发 > 生产
        self.env_priority = [
            'test', 'uat', 'gray', 'grey', 'dev', 'prod', 'production'
        ]

    def find_project_path(self, project_name: str) -> Optional[Path]:
        """查找项目路径"""
        for root, dirs, files in os.walk(self.base_path):
            if project_name in dirs:
                return Path(root) / project_name
        return None

    def find_config_files(self, project_path: Path) -> List[Path]:
        """查找配置文件"""
        config_files = []

        # 搜索Spring配置文件
        spring_patterns = [
            "**/spring*.xml",
            "**/applicationContext*.xml",
            "**/*-dao.xml",
            "**/*-datasource.xml"
        ]

        for pattern in spring_patterns:
            config_files.extend(project_path.glob(pattern))

        # 搜索属性文件
        properties_patterns = [
            "**/application*.properties",
            "**/database*.properties",
            "**/jdbc*.properties"
        ]

        for pattern in properties_patterns:
            config_files.extend(project_path.glob(pattern))

        return config_files

    def get_env_priority_score(self, file_path: Path) -> int:
        """获取环境优先级分数，分数越低优先级越高"""
        file_name = file_path.name.lower()

        for i, env in enumerate(self.env_priority):
            if env in file_name:
                return i

        # 如果没有匹配到环境标识，返回最低优先级
        return len(self.env_priority)

    def select_preferred_properties_files(self, properties_files: List[Path]) -> List[Path]:
        """根据环境优先级选择properties文件"""
        if not properties_files:
            return []

        # 按环境优先级排序
        sorted_files = sorted(properties_files, key=self.get_env_priority_score)

        # 获取最高优先级的环境
        best_score = self.get_env_priority_score(sorted_files[0])

        # 返回所有具有最高优先级的文件
        preferred_files = [f for f in sorted_files if self.get_env_priority_score(f) == best_score]

        return preferred_files

    def _get_env_info(self, file_path: Path) -> str:
        """获取文件的环境信息"""
        file_name = file_path.name.lower()

        for env in self.env_priority:
            if env in file_name:
                return f"({env}环境)"

        return "(默认环境)"

    def parse_properties_file(self, file_path: Path) -> Dict[str, str]:
        """解析properties文件"""
        properties = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        properties[key.strip()] = value.strip()
        except Exception as e:
            print(f"解析properties文件失败 {file_path}: {e}")

        return properties

    def resolve_placeholder(self, value: str, properties: Dict[str, str]) -> str:
        """解析占位符变量"""
        if not value or not value.startswith('${'):
            return value

        # 提取占位符变量名
        match = re.match(r'\$\{([^}]+)\}', value)
        if match:
            placeholder = match.group(1)
            return properties.get(placeholder, value)

        return value

    def parse_spring_xml(self, file_path: Path, properties: Dict[str, str]) -> List[DatabaseConfig]:
        """解析Spring XML配置文件"""
        configs = []

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # 定义命名空间
            namespaces = {
                'beans': 'http://www.springframework.org/schema/beans'
            }

            # 查找所有数据源bean
            datasource_classes = [
                'org.apache.commons.dbcp.BasicDataSource',
                'org.apache.commons.dbcp2.BasicDataSource',
                'com.alibaba.druid.pool.DruidDataSource',
                'org.springframework.jdbc.datasource.DriverManagerDataSource'
            ]

            for bean in root.findall('.//beans:bean', namespaces):
                class_attr = bean.get('class', '')
                if any(ds_class in class_attr for ds_class in datasource_classes):
                    config = self._extract_datasource_config(bean, properties, namespaces)
                    if config:
                        configs.append(config)

            # 如果没有找到命名空间的bean，尝试不使用命名空间
            if not configs:
                for bean in root.findall('.//bean'):
                    class_attr = bean.get('class', '')
                    if any(ds_class in class_attr for ds_class in datasource_classes):
                        config = self._extract_datasource_config(bean, properties, {})
                        if config:
                            configs.append(config)

        except Exception as e:
            logger.error(f"解析Spring XML文件失败 {file_path}: {e}")

        return configs

    def _extract_datasource_config(self, bean_element, properties: Dict[str, str], namespaces: Dict[str, str]) -> \
    Optional[DatabaseConfig]:
        """从bean元素中提取数据源配置"""
        bean_id = bean_element.get('id', 'unknown')
        url = None
        username = None
        password = None
        driver = None

        # 查找属性
        property_mappings = {
            'url': ['url', 'jdbcUrl'],
            'username': ['username', 'user'],
            'password': ['password'],
            'driver': ['driverClassName', 'driver-class-name', 'driverClass']
        }

        if namespaces:
            properties_xpath = './/beans:property'
        else:
            properties_xpath = './/property'

        for prop in bean_element.findall(properties_xpath, namespaces):
            prop_name = prop.get('name', '')
            prop_value = prop.get('value', '')

            # 解析占位符
            resolved_value = self.resolve_placeholder(prop_value, properties)

            for config_key, prop_names in property_mappings.items():
                if prop_name in prop_names:
                    if config_key == 'url':
                        url = resolved_value
                    elif config_key == 'username':
                        username = resolved_value
                    elif config_key == 'password':
                        password = resolved_value
                    elif config_key == 'driver':
                        driver = resolved_value

        if url and username:  # password可能为空
            return DatabaseConfig(bean_id, url, username, password or '', driver or '')

        return None

    def extract_database_configs(self) -> List[DatabaseConfig]:
        """提取数据库配置"""
        # 从 base_path 中解析项目名称
        project_name = self.base_path.name
        project_path = self.base_path
        
        print(f"使用项目路径: {project_path}, 项目名称: {project_name}")

        config_files = self.find_config_files(project_path)
        if not config_files:
            print("未找到配置文件")
            return []

        print(f"找到配置文件: {len(config_files)} 个")
        for f in config_files:
            print(f"  - {f}")

        # 分离properties文件和XML文件
        properties_files = [f for f in config_files if f.suffix == '.properties']
        xml_files = [f for f in config_files if f.suffix == '.xml']

        # 根据环境优先级选择properties文件
        preferred_properties = self.select_preferred_properties_files(properties_files)

        if preferred_properties:
            print(f"\n根据环境优先级选择的配置文件:")
            for f in preferred_properties:
                env_info = self._get_env_info(f)
                print(f"  - {f} {env_info}")

        # 解析选中的properties文件
        all_properties = {}
        for config_file in preferred_properties:
            props = self.parse_properties_file(config_file)
            all_properties.update(props)

        # 然后解析XML文件
        all_configs = []
        for config_file in xml_files:
            configs = self.parse_spring_xml(config_file, all_properties)
            all_configs.extend(configs)

        return all_configs

    def connect_and_query(self, config: DatabaseConfig, table_name: Optional[str] = None) -> str:
        """连接数据库并执行查询（真实连接模式）"""
        result_text = []

        # 解析数据库连接信息
        url_pattern = r'jdbc:mysql://([^:/]+):?(\d+)?/([^?]+)'
        match = re.match(url_pattern, config.url)

        if not match:
            error_msg = f"无法解析数据库URL: {config.url}"
            logger.error(error_msg)
            return error_msg

        host = match.group(1)
        port = int(match.group(2)) if match.group(2) else 3306
        database = match.group(3)

        logger.info(f"尝试连接数据库: {host}:{port}/{database}, 用户: {config.username}")

        try:
            # 真实连接数据库
            import pymysql
            connection = pymysql.connect(
                host=host,
                port=port,
                user=config.username,
                password=config.password,
                database=database,
                charset='utf8mb4',
                connect_timeout=10
            )

            logger.info(f"数据库连接成功")

            with connection.cursor() as cursor:
                if table_name:
                    # 查询特定表的详细信息
                    logger.info(f"正在查询表 '{table_name}' 的结构...")

                    # 检查表是否存在
                    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                    table_exists = cursor.fetchone()

                    if not table_exists:
                        error_msg = f"❌ 表 '{table_name}' 在数据库 {database} 中不存在"
                        logger.error(error_msg)
                        return error_msg

                    result_text.append(f"## 📋 表 `{table_name}` 详细信息")
                    result_text.append(f"**数据库**: {database}")
                    result_text.append(f"**服务器**: {host}:{port}")
                    result_text.append(f"")
                    result_text.append(
                        "🔒 **字段名保护声明**：本文档中所有数据库字段名均为真实字段名，请严格按照原样使用，禁止进行任何形式的命名转换（如驼峰转下划线等）！")
                    result_text.append(f"")

                    # 验证表名，防止SQL注入
                    validate_table_name(table_name)
                    
                    # 获取表结构
                    logger.info(f"执行 DESCRIBE {table_name} 查询...")
                    try:
                        cursor.execute(f"DESCRIBE {table_name}")
                        columns = cursor.fetchall()
                        logger.info(f"DESCRIBE 查询返回 {len(columns) if columns else 0} 行数据")
                    except Exception as e:
                        logger.error(f"DESCRIBE 查询失败: {e}")
                        result_text.append(f"获取表结构失败: {e}")
                        columns = []

                    if columns:
                        result_text.append(f"## 表 {table_name} 的结构信息")
                        result_text.append("")
                        result_text.append(
                            "**⚠️ 重要提示：以下字段名为数据库中的真实字段名，请保持原样显示，不要进行任何命名转换！**")
                        result_text.append("")
                        result_text.append("### 字段信息")
                        result_text.append("| 字段名 | 数据类型 | 是否为空 | 键 | 默认值 | 额外信息 |")
                        result_text.append("|--------|----------|----------|-----|--------|----------|")

                        for column in columns:
                            field = column[0]
                            type_info = column[1]
                            null_info = column[2]
                            key_info = column[3]
                            default_info = column[4] if column[4] is not None else ""
                            extra_info = column[5]

                            # 使用反引号包围字段名，强调这是精确的字段名
                            result_text.append(
                                f"| `{field}` | {type_info} | {null_info} | {key_info} | {default_info} | {extra_info} |")

                        result_text.append("")
                        result_text.append(
                            "**注意：上述字段名使用反引号标记，表示这些是数据库中的精确字段名，请在引用时保持完全一致。**")
                        result_text.append("")
                    else:
                        result_text.append("⚠️ 未能获取到表字段信息")
                        result_text.append("")

                    # 获取建表语句
                    try:
                        # 表名已在前面验证，此处无需重复验证
                        cursor.execute(f"SHOW CREATE TABLE {table_name}")
                        create_table_result = cursor.fetchone()
                        if create_table_result:
                            create_sql = create_table_result[1]
                            result_text.append("### 建表语句")
                            result_text.append("```sql")
                            result_text.append(create_sql)
                            result_text.append("```")
                            result_text.append("")
                    except Exception as e:
                        result_text.append(f"获取建表语句失败: {e}")
                        result_text.append("")

                    # 获取索引信息
                    try:
                        # 表名已在前面验证，此处无需重复验证
                        cursor.execute(f"SHOW INDEX FROM {table_name}")
                        indexes = cursor.fetchall()
                        if indexes:
                            result_text.append("### 索引信息")
                            result_text.append("| 索引名 | 字段名 | 是否唯一 | 序列 | 排序 |")
                            result_text.append("|--------|--------|----------|------|------|")

                            for index in indexes:
                                key_name = index[2]
                                column_name = index[4]
                                non_unique = "否" if index[1] == 0 else "是"
                                seq_in_index = index[3]
                                collation = index[5] if index[5] else ""

                                result_text.append(
                                    f"| {key_name} | {column_name} | {non_unique} | {seq_in_index} | {collation} |")

                            result_text.append("")
                    except Exception as e:
                        result_text.append(f"获取索引信息失败: {e}")
                        result_text.append("")

                else:
                    # 查询所有表
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    table_count = len(tables)
                    logger.info(f"找到 {table_count} 个表")

                    result_text.append("=" * 50)
                    result_text.append(f"【表清单】数据库 {database} 中的表:")
                    for i, table in enumerate(tables, 1):
                        result_text.append(f"  {i:2d}. {table[0]}")
                    result_text.append("=" * 50)

            connection.close()

            # 返回构建的结果文本
            result_string = "\n".join(result_text)
            logger.debug(f"准备返回结果，长度: {len(result_string)} 字符")
            logger.debug(f"结果文本行数: {len(result_text)}")
            if result_text:
                logger.debug(f"结果文本前3行: {result_text[:3]}")
            return result_string

        except Exception as e:
            error_msg = f"连接数据库失败: {e}"
            logger.error(error_msg)
            return error_msg


# Pydantic 输入参数模型
class DBExtractorInput(BaseModel):
    """数据库提取工具输入参数模型
    
    提取项目的数据库配置信息，并可选择性地查询特定表的结构。
    也支持JSON格式参数输入：{"table_name": "user_info"}
    """
    table_name: Optional[str] = Field(
        default=None,
        description="表名（可选），用于查询特定表的结构信息。如果不提供，将返回所有表的列表",
        examples=["user_info", "order_detail", "product"]
    )


class DBExtractorTool(BasePathTool):
    """数据库配置提取和查询工具
    
    该工具提供从项目中提取数据库配置信息的功能，并可以查询数据库表结构。
    支持从Spring配置文件和属性文件中提取数据库连接信息，并根据环境优先级选择合适的配置。
    """
    
    def __init__(self, base_dir: str = "."):
        """初始化数据库提取工具
        
        Args:
            base_dir: 基础目录路径，默认为当前目录
        """
        super().__init__(base_dir)
        self.extractor = DatabaseConfigExtractor(base_dir=base_dir)
        self.error_handler = ErrorHandler()
    
    @handle_tool_errors(tool_name="DBExtractor", operation="extract", return_format="json")
    def run(self, table_name: Optional[str] = None) -> str:
        """
        执行数据库配置提取和查询
        
        Args:
            table_name: 表名（可选），用于查询特定表的结构信息
            
        Returns:
            JSON格式的查询结果或错误信息
        """
        # 从 base_dir 中解析项目名称
        project_name = self.base_dir.name
        
        # 检查 table_name 是否是 JSON 字符串
        if table_name and isinstance(table_name, str):
            # 规范化处理，去除空白字符
            table_name_normalized = table_name.strip()
            
            # 特殊处理空JSON对象 {}
            if table_name_normalized == '{}':
                logger.debug("检测到空JSON对象，将表名设置为None，只提取项目数据库配置")
                table_name = None
            # 处理其他JSON字符串
            elif table_name_normalized.startswith('{') and table_name_normalized.endswith('}'):
                try:
                    # 尝试解析 JSON
                    params = json.loads(table_name_normalized)
                    if isinstance(params, dict):
                        # 提取 table_name 字段
                        extracted_table_name = params.get('table_name')
                        
                        # 如果 table_name 参数为 None，使用从 JSON 中提取的值
                        if extracted_table_name is not None:
                            table_name = extracted_table_name
                        elif not params:  # 空字典情况
                            logger.debug("检测到空JSON对象字典，将表名设置为None，只提取项目数据库配置")
                            table_name = None
                        
                        logger.debug(f"从JSON中提取参数: table_name={table_name}")
                except json.JSONDecodeError:
                    # 如果解析失败，继续使用原始参数
                    logger.warning(f"JSON解析失败，使用原始参数: {table_name}")
        
        return self._extract_internal(table_name)
    
    def _extract_internal(self, table_name: Optional[str] = None) -> str:
        """
        内部提取方法
        
        Args:
            table_name: 表名（可选）
            
        Returns:
            查询结果
            
        Raises:
            ConfigurationError: 配置错误
            ServiceUnavailableError: 服务不可用
        """
        # 从 base_dir 中解析项目名称
        project_name = self.base_dir.name
        
        if not project_name or not project_name.strip():
            raise ConfigurationError(
                "无法从基础目录解析项目名称",
                pattern=str(self.base_dir),
                tool_name=self.__class__.__name__
            )
        
        # 提取数据库配置
        configs = self.extractor.extract_database_configs()
        
        if not configs:
            return json.dumps({
                "success": False,
                "message": f"未找到项目 '{project_name}' 的数据库配置",
                "project_name": project_name,
                "table_name": table_name,
                "configs_found": 0
            }, ensure_ascii=False, indent=2)
        
        # 连接数据库并查询
        results = []
        
        # 特殊处理空JSON对象 {}
        if table_name == '{}':
            logger.debug("_extract_internal: 检测到空JSON对象，将表名设置为None，只提取项目数据库配置")
            return json.dumps({
                "success": True,
                "message": f"成功提取项目 '{project_name}' 的数据库配置",
                "project_name": project_name,
                "table_name": None,
                "configs_found": len(configs),
                "configs": [str(config) for config in configs]
            }, ensure_ascii=False, indent=2)
        
        if table_name:
            # 如果指定了表名，需要智能选择数据库
            table_found = False
            
            # 验证表名，防止SQL注入
            validate_table_name(table_name)
            
            # 首先去重数据源，避免重复查询相同的数据库
            unique_configs = []
            seen_urls = set()
            
            for config in configs:
                # 提取数据库URL的关键部分（去掉参数）
                url_key = config.url.split('?')[0] if '?' in config.url else config.url
                if url_key not in seen_urls:
                    seen_urls.add(url_key)
                    unique_configs.append(config)
            
            for config in unique_configs:
                try:
                    # 解析数据库连接信息
                    url_pattern = r'jdbc:mysql://([^:/]+):?(\d+)?/([^?]+)'
                    match = re.match(url_pattern, config.url)
                    
                    if not match:
                        continue
                    
                    host = match.group(1)
                    port = int(match.group(2)) if match.group(2) else 3306
                    database = match.group(3)
                    
                    # 连接数据库检查表是否存在
                    import pymysql
                    try:
                        connection = pymysql.connect(
                            host=host,
                            port=port,
                            user=config.username,
                            password=config.password,
                            database=database,
                            charset='utf8mb4',
                            connect_timeout=5
                        )
                        
                        with connection.cursor() as cursor:
                            # 表名已在前面验证，此处无需重复验证
                            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                            table_exists = cursor.fetchone()
                            
                            if table_exists:
                                # 查询建表语句
                                result = self.extractor.connect_and_query(config, table_name)
                                if result:
                                    results.append(result)
                                    table_found = True
                                    connection.close()
                                    break  # 找到表后立即退出循环
                        
                        connection.close()
                    
                    except pymysql.err.OperationalError:
                        continue
                
                except Exception:
                    continue
            
            if not table_found:
                return json.dumps({
                    "success": False,
                    "message": f"在所有数据库中都未找到表 '{table_name}'",
                    "project_name": project_name,
                    "table_name": table_name,
                    "configs_found": len(configs),
                    "databases_checked": len(unique_configs)
                }, ensure_ascii=False, indent=2)
        
        else:
            # 如果没有指定表名，查询所有数据库的表列表
            # 首先去重数据源，避免重复连接相同的数据库
            unique_configs = []
            seen_urls = set()
            
            for config in configs:
                # 提取数据库URL的关键部分（去掉参数）
                url_key = config.url.split('?')[0] if '?' in config.url else config.url
                if url_key not in seen_urls:
                    seen_urls.add(url_key)
                    unique_configs.append(config)
            
            for config in unique_configs:
                try:
                    result = self.extractor.connect_and_query(config)
                    if result:
                        results.append(result)
                except Exception:
                    continue
        
        # 返回所有结果
        final_result = "\n\n".join(results) if results else "未能获取数据库信息"
        
        return json.dumps({
            "success": True,
            "message": f"成功查询项目 '{project_name}' 的数据库信息",
            "project_name": project_name,
            "table_name": table_name,
            "configs_found": len(configs),
            "result": final_result
        }, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='数据库配置提取和查询工具')
    parser.add_argument('--table', '-t', help='表名 (可选，用于查询建表语句)')
    parser.add_argument('--base-path', default='.', help='基础路径 (默认: 当前目录)')
    args = parser.parse_args()

    extractor = DatabaseConfigExtractor(args.base_path)
    
    # 从 base_path 中解析项目名称
    project_name = Path(args.base_path).resolve().name
    print(f"搜索项目: {project_name}")
    configs = extractor.extract_database_configs()

    if not configs:
        print("未找到数据库配置")
        return "未找到数据库配置"

    print(f"\n找到 {len(configs)} 个数据库配置:")
    for i, config in enumerate(configs, 1):
        print(f"{i}. {config}")

    # 连接数据库并查询
    results = []

    # 特殊处理空JSON对象 {}
    if args.table == '{}':
        print(f"\n检测到空JSON对象，只提取项目 '{project_name}' 的数据库配置")
        for i, config in enumerate(configs, 1):
            print(f"{i}. {config}")
        return json.dumps({
            "success": True,
            "message": f"成功提取项目 '{project_name}' 的数据库配置",
            "project_name": project_name,
            "table_name": None,  # 明确设置为None
            "configs_found": len(configs),
            "configs": [str(config) for config in configs]
        }, ensure_ascii=False, indent=2)
    
    if args.table:
        # 验证表名，防止SQL注入
        validate_table_name(args.table)
        
        # 如果指定了表名，需要智能选择数据库
        print(f"\n查询表 '{args.table}' 的结构...")
        table_found = False

        # 首先去重数据源，避免重复查询相同的数据库
        unique_configs = []
        seen_urls = set()

        for config in configs:
            # 提取数据库URL的关键部分（去掉参数）
            url_key = config.url.split('?')[0] if '?' in config.url else config.url
            if url_key not in seen_urls:
                seen_urls.add(url_key)
                unique_configs.append(config)
            else:
                print(f"跳过重复数据源: {config.name} -> {url_key}")

        print(f"去重后剩余 {len(unique_configs)} 个唯一数据源")

        for config in unique_configs:
            try:
                # 先检查表是否存在于该数据库中
                print(f"检查数据库 {config.name} 中是否存在表 '{args.table}'...")

                # 解析数据库连接信息
                url_pattern = r'jdbc:mysql://([^:/]+):?(\d+)?/([^?]+)'
                match = re.match(url_pattern, config.url)

                if not match:
                    print(f"无法解析数据库URL: {config.url}")
                    continue

                host = match.group(1)
                port = int(match.group(2)) if match.group(2) else 3306
                database = match.group(3)

                # 连接数据库检查表是否存在
                import pymysql
                try:
                    connection = pymysql.connect(
                        host=host,
                        port=port,
                        user=config.username,
                        password=config.password,
                        database=database,
                        charset='utf8mb4',
                        connect_timeout=5
                    )

                    with connection.cursor() as cursor:
                        # 表名已在前面验证，此处无需重复验证
                        cursor.execute(f"SHOW TABLES LIKE '{args.table}'")
                        table_exists = cursor.fetchone()

                        if table_exists:
                            print(f"✅ 在数据库 {database} 中找到表 '{args.table}'")
                            # 查询建表语句
                            result = extractor.connect_and_query(config, args.table)
                            if result:
                                results.append(result)
                                table_found = True
                                # 找到表后就退出循环，避免重复查询
                                connection.close()

                                # 输出最终结果
                                print("\n" + "=" * 80)
                                print("最终结果:")
                                print("=" * 80)
                                print(result)

                                return result  # 找到表后立即返回结果
                        else:
                            print(f"❌ 数据库 {database} 中不存在表 '{args.table}'")

                    connection.close()

                except pymysql.err.OperationalError as e:
                    print(f"连接数据库 {database} 失败: {e}")
                    continue

            except Exception as e:
                print(f"检查数据库 {config.name} 时出错: {e}")
                continue

        if not table_found:
            error_msg = f"在所有数据库中都未找到表 '{args.table}'"
            print(error_msg)
            return error_msg

    else:
        # 如果没有指定表名，查询所有数据库的表列表
        # 首先去重数据源，避免重复连接相同的数据库
        unique_configs = []
        seen_urls = set()

        for config in configs:
            # 提取数据库URL的关键部分（去掉参数）
            url_key = config.url.split('?')[0] if '?' in config.url else config.url
            if url_key not in seen_urls:
                seen_urls.add(url_key)
                unique_configs.append(config)
            else:
                print(f"跳过重复数据源: {config.name} -> {url_key}")

        print(f"\n去重后剩余 {len(unique_configs)} 个唯一数据源")

        for config in unique_configs:
            try:
                result = extractor.connect_and_query(config)
                if result:
                    results.append(result)
            except KeyboardInterrupt:
                print("\n用户中断操作")
                break
            except Exception as e:
                error_msg = f"处理配置 {config.name} 时出错: {e}"
                print(error_msg)
                # 打印更详细的错误信息
                import traceback
                detailed_error = traceback.format_exc()
                print(f"详细错误信息: {detailed_error}")
                results.append(f"{error_msg}\n详细错误信息:\n{detailed_error}")
                continue

    # 提取表信息并放在结果前面
    if results:
        all_tables = []
        for result in results:
            # 提取表信息
            tables_section = []
            in_table_section = False

            for line in result.split('\n'):
                if "=" * 50 in line:
                    in_table_section = not in_table_section
                    if in_table_section:  # 只在进入表区域时添加分隔符
                        tables_section.append(line)
                elif in_table_section:
                    tables_section.append(line)

            if tables_section:
                all_tables.extend(tables_section)

        # 如果找到了表信息，将其添加到结果的开头
        if all_tables:
            tables_summary = "\n".join(all_tables)
            print("\n表信息摘要:")
            print(tables_summary)

            # 将表信息添加到结果的开头
            combined_results = f"数据库表信息摘要:\n{tables_summary}\n\n完整查询结果:\n" + "\n\n".join(results)
            return combined_results

    # 返回所有结果
    final_result = "\n\n".join(results) if results else "未能获取数据库信息"

    # 输出最终结果
    print("\n" + "=" * 80)
    print("最终结果:")
    print("=" * 80)
    print(final_result)

    return final_result


if __name__ == '__main__':
    main()