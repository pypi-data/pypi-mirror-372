"""
dir_utils 包

提供目录工具功能的统一接口，包括：
- 文件分类功能
- 目录树构建功能（支持智能压缩）
- Markdown 生成功能（支持智能压缩）
- 智能目录压缩算法

重构自原有的 directory_utils.py 和 _dir_utils.py 模块，
按职责分离代码到不同模块，提高代码复用性和可维护性。

v2.0.0 重构亮点：
- 新增共享的智能压缩算法模块
- tree_builder 和 markdown_generator 复用相同的压缩逻辑
- 支持 Maven 项目结构、Java 包结构、通用单链路径压缩
- 保持向后兼容性
"""

from .classifier import classify_files_by_type
from .tree_builder import get_directory_tree, get_compressed_tree_structure, extract_compressed_paths
from .markdown_generator import generate_directory_markdown
import os

base_dir  = os.path.dirname( 
   # kengine
   os.path.dirname(      
      # utils
      os.path.dirname(
         # dir_utils
         os.path.dirname(os.path.abspath(__file__))
      )
   )
)

# 导出核心功能函数
__all__ = [
   "base_dir",
    # 原有功能
    'classify_files_by_type',
    'get_directory_tree', 
    'generate_directory_markdown',
    
    # 新增压缩功能
    'get_compressed_tree_structure',
    'extract_compressed_paths']

# 版本信息
__version__ = '2.0.0'

# 模块说明
__doc__ = """
dir_utils 包提供了完整的目录工具功能：

1. classify_files_by_type: 按文件类型分类文件
   - 支持递归遍历
   - 支持隐藏文件处理
   - 基于文件扩展名智能分类

2. get_directory_tree: 获取目录树结构
   - 支持深度限制
   - 支持 gitignore 规则
   - 支持文件大小信息
   - 支持扩展名过滤
   - 新增：支持智能目录压缩（enable_compression=True）

3. generate_directory_markdown: 生成目录的 Markdown 格式输出
   - 智能路径压缩（默认启用）
   - Maven 项目结构优化
   - Java 包结构压缩
   - 树状结构显示
   - 新增：可控制压缩功能（enable_compression参数）

4. 新增压缩功能：
   - get_compressed_tree_structure: 获取带压缩的目录树（便捷函数）
   - extract_compressed_paths: 提取所有压缩路径

压缩算法支持：
- Maven 标准目录结构：src/main/java, src/test/resources 等
- Java 包结构：com/company/project, org/apache/commons 等
- 通用单链路径：任何只有单一子目录的连续结构

使用示例:

基础功能：
    from kengine.utils.dir_utils import classify_files_by_type, get_directory_tree, generate_directory_markdown
    
    # 文件分类
    source_files, doc_files, binary_files = classify_files_by_type('/path/to/project')
    
    # 获取目录树（不压缩）
    tree = get_directory_tree('/path/to/project', max_depth=3)
    
    # 获取目录树（启用压缩）
    compressed_tree = get_directory_tree('/path/to/project', max_depth=3, enable_compression=True)
    
    # 生成 Markdown（默认启用压缩）
    markdown = generate_directory_markdown('/path/to/project', max_depth=2)
    
    # 生成 Markdown（禁用压缩）
    markdown_no_compression = generate_directory_markdown('/path/to/project', max_depth=2, enable_compression=False)

压缩功能：
    from kengine.utils.dir_utils import get_compressed_tree_structure, extract_compressed_paths
    
    # 便捷获取压缩树
    compressed_tree = get_compressed_tree_structure('/path/to/project', max_depth=3)
    
    # 提取所有压缩路径
    compressed_paths = extract_compressed_paths(compressed_tree)
    print("压缩路径:", compressed_paths)
    # 输出示例: ['src/main/java', 'src/test/resources', 'com/company/project']

"""