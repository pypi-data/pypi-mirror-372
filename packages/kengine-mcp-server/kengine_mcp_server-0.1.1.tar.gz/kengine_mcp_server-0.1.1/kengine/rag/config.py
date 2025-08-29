"""
RAG配置模块

该模块包含RAG服务的所有配置选项和设置。
"""

import fnmatch
from pathlib import Path, PurePath
from kengine.config.application_config import get_application_config

class RAGConfigManager:
    """RAG配置管理器，配置结构如下：
  "rag":{
    "search": {
      "model_options": {
        "base_url": "{env:JDT_ROUTER_BASE}",
        "api_key": "{env:JDT_API_KEY}",
        "model": "anthropic.claude-sonnet-4-20250514-v1:0",
        "temperature": 0.1,
        "max_tokens": 65536
      },
      "default_retrieval_k": 5
    },
    "embeddings": {
      "model_options": {
        "model": "text-embedding-3-small",
        "base_url": "{env:JDT_ROUTER_BASE}",
        "api_key": "{env:JDT_API_KEY}",
        "max_retries": 3,
        "timeout": 120,
        "show_progress_bar": true
      },
      "text_splitter": {
        "chunk_size": 1000,
        "chunk_overlap": 200
      },
      "constraints": {
        "max_file_size": 1024000,
        "exclude_patterns": [
          "*.min.js", "**/bin/*", "**/build/*","**/.cache/*",
          "**/node_modules/*", "**/dist/*"
        ],
        "include_extensions": [
          ".java", ".go", ".c", ".cpp", ".cs", ".html", ".vue", ".py", ".dart", ".kt", ".ktl",
          ".md", ".ts", ".tsx", ".xml", ".config"
        ]
      }
    }
  }
    """
    
    def __init__(self):
        app_config = get_application_config()
        self.rag_config = app_config.get('rag', {})
    
    
    def embeddings_model_options(self):
        if not self.rag_config:
            return {}
        return self.rag_config.get('embeddings', {}).get('model_options', {})
    
    def text_splitter_options(self):
        if not self.rag_config:
            return {}
        return self.rag_config.get('embeddings', {}).get('text_splitter', {})
      
    def search_model_options(self):
        if not self.rag_config:
            return {}
        return self.rag_config.get('search', {}).get('model_options', {})
    
    def default_retrieval_k(self):
        if not self.rag_config:
            return 5
        return self.rag_config.get('search', {}).get('default_retrieval_k', 5)

    def should_embedding(self, file_path: str) -> bool:
        """
        判断给定的文件路径是否应该进行嵌入处理
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: True表示应该进行嵌入，False表示不应该
        """
        if not file_path:
            return False
            
        # 获取约束条件配置
        if not self.rag_config:
            return True  # 如果没有rag配置，默认允许嵌入
        
        constraints = self.rag_config.get('embeddings', {}).get('constraints', {})
        if not constraints:
            return True  # 如果没有约束条件，默认允许嵌入
        
        # 转换为Path对象以便处理
        path = Path(file_path)
        
        # 检查文件大小限制
        max_file_size = constraints.get('max_file_size', float('inf'))
        try:
            if path.exists() and path.stat().st_size > max_file_size:
                return False
        except (OSError, IOError):
            # 如果无法获取文件大小，继续其他检查
            pass
        
        # 检查排除模式
        exclude_patterns = constraints.get('exclude_patterns', [])
        for pattern in exclude_patterns:
            # 使用多种方式匹配模式以确保兼容性
            matched = False
            
            # 方法1: 使用 pathlib.Path.match() 来支持 ** 递归通配符
            try:
                if path.match(pattern):
                    matched = True
            except ValueError:
                pass
            
            # 方法2: 如果模式包含 **，尝试简化的模式
            if not matched and '**' in pattern:
                # 将 **/build/* 转换为 build/* 等简化模式
                simplified_pattern = pattern.replace('**/', '')
                try:
                    if path.match(simplified_pattern):
                        matched = True
                except ValueError:
                    pass
                
                # 也尝试 fnmatch 与简化模式
                if not matched:
                    if fnmatch.fnmatch(file_path, simplified_pattern):
                        matched = True
            
            # 方法3: 回退到 fnmatch
            if not matched:
                if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(str(path), pattern):
                    matched = True
            
            if matched:
                return False
        
        # 检查包含的文件扩展名
        include_extensions = constraints.get('include_extensions', [])
        if include_extensions:
            file_extension = path.suffix.lower()
            # 如果指定了包含扩展名列表，只有在列表中的扩展名才允许
            if file_extension not in [ext.lower() for ext in include_extensions]:
                return False
        
        return True
    
    def get_embeddings_concurrent(self):
        if not self.rag_config:
            return 1
        return self.rag_config.get('embeddings', {}).get('concurrent', 1)
    
    def get_embedding_batch_size(self):
        default_batch_size = 500
        if not self.rag_config:
            return default_batch_size
        return self.rag_config.get('embeddings', {}).get('batch_size', default_batch_size)
    
    def get_vector_store_type(self):
        """获取向量存储类型，默认为local"""
        if not self.rag_config:
            return 'local'
        
        # 读取 vector_store_type 配置
        vector_store_type = self.rag_config.get('vector_store_type')
        
        # 处理空值情况：None、空字符串、空白字符串都默认为 local
        if not vector_store_type or not vector_store_type.strip():
            # 兼容模式：检查是否有 vearch 配置节点（向后兼容）
            if 'vearch' in self.rag_config:
                return 'vearch'
            return 'local'
        
        # 返回配置的值
        return vector_store_type.strip()
    
    def vearch_config(self):
        """获取Vearch配置"""
        if not self.rag_config:
            return {}
        return self.rag_config.get('vearch', {})
    
    def vearch_master_server(self):
        """获取Vearch Master服务器地址"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('master_server')
    
    def vearch_router_server(self):
        """获取Vearch Router服务器地址"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('router_server')
    
    def vearch_default_db_name(self):
        """获取Vearch默认数据库名称"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('default_db_name')
    
    def vearch_default_space_name(self):
        """获取Vearch默认空间名称"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('default_space_name')
    
    def vearch_vector_dimension(self):
        """获取Vearch向量维度"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('vector_dimension')
    
    def vearch_search_limit(self):
        """获取Vearch搜索限制"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('search_limit')
    
    def vearch_metric_type(self):
        """获取Vearch度量类型"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('metric_type')
    
    def vearch_index_params(self):
        """获取Vearch索引参数"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('index_params')
    
    def vearch_connection_timeout(self):
        """获取Vearch连接超时时间"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('connection_timeout')
    
    def vearch_retry_attempts(self):
        """获取Vearch重试次数"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('retry_attempts')
    
    def vearch_enable_cache(self):
        """获取Vearch是否启用缓存"""
        vearch_cfg = self.vearch_config()
        return vearch_cfg.get('enable_cache')
    