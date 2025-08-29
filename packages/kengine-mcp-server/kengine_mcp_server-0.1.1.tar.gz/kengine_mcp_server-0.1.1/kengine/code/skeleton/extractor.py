"""
代码骨架提取器主类
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from ..language_loader import get_supported_languages, get_language_for_extension
from ..utils import read_file_content
from .languages import (
    PythonHandler, JavaHandler, JavaScriptHandler, 
    GoHandler, CSharpHandler, CppHandler, KotlinHandler
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from tree_sitter import Parser
except ImportError:
    Parser = None


class CodeSkeletonExtractor:
    """代码骨架提取器"""
    
    def __init__(self):
        """初始化提取器"""
        if not Parser:
            raise ImportError("tree-sitter库未正确安装，请运行: pip install tree-sitter")
        
        # 获取支持的语言映射
        self.supported_languages = get_supported_languages()
        
        # 检查是否有任何语言加载失败
        failed_languages = []
        for ext, (lang_lib, lang_name) in self.supported_languages.items():
            if lang_lib is None:
                failed_languages.append(ext)
        
        if failed_languages:
            raise ValueError(f"以下语言库加载失败: {', '.join(failed_languages)}")
        
        logger.info(f"支持的文件类型: {list(self.supported_languages.keys())}")

    def extract_skeleton(self, code_file_path: str) -> str:
        """
        从code_file_path文件中读取代码，提取代码骨架
        骨架包括 包名，类名，方法定义 以及他们的注释
        支持 Java，js，golang，csharp, c, cc等类型

        Args:
            code_file_path: 代码文件路径

        Returns:
            骨架代码字符串

        Raises:
            FileNotFoundError: 当文件不存在时
            ValueError: 当文件类型不支持时
            Exception: 当解析过程中发生其他错误时
        """
        try:
            # 验证文件路径
            if not code_file_path:
                raise ValueError("代码文件路径不能为空")

            file_path = Path(code_file_path)

            # 检查文件是否存在
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {code_file_path}")

            # 检查文件是否为空
            if file_path.stat().st_size == 0:
                logger.warning(f"文件为空: {code_file_path}")
                return f"# 文件为空: {code_file_path}\n"

            # 获取文件扩展名
            ext = file_path.suffix.lower()
            if file_path.name.lower() == "dockerfile":
                ext = "dockerfile"

            # 检查文件类型是否支持
            if ext not in self.supported_languages:
                supported_exts = list(self.supported_languages.keys())
                raise ValueError(f"不支持的文件类型: {ext}。支持的文件类型: {', '.join(supported_exts)}")

            logger.info(f"开始提取代码骨架: {code_file_path}")

            # 读取文件内容
            code_content = read_file_content(file_path)

            # 获取语言解析器
            lang_lib, lang_name = self.supported_languages[ext]
            parser = Parser(lang_lib)

            # 解析代码
            tree = parser.parse(code_content.encode('utf-8'))

            # 根据语言生成骨架
            skeleton = self._generate_skeleton_by_language(tree, code_content, lang_name, file_path)

            if not skeleton.strip():
                logger.warning(f"未能提取到有效的代码骨架: {code_file_path}")
                return f"# 未能提取到有效的代码骨架\n# 文件: {code_file_path}\n"

            logger.info(f"成功提取代码骨架: {code_file_path}")
            return skeleton

        except FileNotFoundError as e:
            logger.error(f"文件不存在错误: {e}")
            raise
        except ValueError as e:
            logger.error(f"参数错误: {e}")
            raise
        except Exception as e:
            logger.error(f"提取代码骨架时发生未知错误: {e}")
            raise Exception(f"提取代码骨架失败: {str(e)}")

    def _generate_skeleton_by_language(self, tree, code_content: str, lang_name: str, file_path: Path) -> str:
        """根据语言类型生成骨架"""
        try:
            # 获取语言库
            lang_lib, _ = get_language_for_extension(file_path.suffix.lower())
            
            if lang_name == 'python':
                handler = PythonHandler(lang_lib)
                return handler.generate_skeleton(tree, code_content)
            elif lang_name == 'java':
                handler = JavaHandler(lang_lib)
                return handler.generate_skeleton(tree, code_content)
            elif lang_name == 'javascript':
                handler = JavaScriptHandler(lang_lib)
                return handler.generate_skeleton(tree, code_content)
            elif lang_name == 'go':
                handler = GoHandler(lang_lib)
                return handler.generate_skeleton(tree, code_content)
            elif lang_name == 'c_sharp':
                handler = CSharpHandler(lang_lib)
                return handler.generate_skeleton(tree, code_content)
            elif lang_name in ['c', 'cpp']:
                handler = CppHandler(lang_lib, lang_name)
                return handler.generate_skeleton(tree, code_content)
            elif lang_name == 'kotlin':
                handler = KotlinHandler(lang_lib)
                return handler.generate_skeleton(tree, code_content)
            else:
                return f"# 暂不支持的语言类型: {lang_name}\n"
        except Exception as e:
            logger.error(f"生成{lang_name}骨架时发生错误: {e}")
            return f"# 生成{lang_name}骨架时发生错误: {str(e)}\n"