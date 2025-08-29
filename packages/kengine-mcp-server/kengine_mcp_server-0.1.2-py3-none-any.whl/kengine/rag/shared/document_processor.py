"""
文档处理器模块

该模块负责文档的读取、清理和分块处理。
从原 kengine.tasks.rag 模块重构而来，保持完全的功能完整性。
"""

import logging
from pathlib import Path
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from kengine.rag.config import RAGConfigManager
from kengine.utils import read_text_file
from kengine.utils.dir_utils import classify_files_by_type

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器，负责文档的读取、清理和分块"""
    
    def __init__(self):
        self.config = RAGConfigManager()
        self.text_splitter_options = self.config.text_splitter_options()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.text_splitter_options['chunk_size'],
            chunk_overlap=self.text_splitter_options['chunk_overlap'],
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_documents_from_directory(self, directory_path: str) -> List[Document]:
        """
        从目录加载文档
        
        Args:
            group_name: 仓库组名
            repo_name: 仓库名称
            directory_path: 目录路径

        Returns:
            文档列表
        """
        logger.info(f"开始从目录加载文档: {directory_path}")
        
        # 分类文件
        source_files, doc_files, _ = classify_files_by_type(
            directory_path, recursive=True, include_hidden=False
        )
        
        # 合并源代码文件和文档文件
        all_files = source_files + doc_files

        # 新增：应用项目类型感知过滤
        supported_files = self._filter_files(all_files)
        
        logger.info(f"找到 {len(supported_files)} 个支持的文件")
        
        # 读取文件内容并创建文档
        documents = []
        for file_path in supported_files:
            try:
                content = read_text_file(file_path)
                if content and content.strip():
                    # 创建文档对象，包含元数据
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": file_path,
                            "filename": Path(file_path).name,
                            "file_type": Path(file_path).suffix.lower(),
                            "file_size": len(content)
                        }
                    )
                    documents.append(doc)
                    logger.debug(f"成功加载文件: {file_path}")
                else:
                    logger.warning(f"文件内容为空，跳过: {file_path}")
            except Exception as e:
                logger.error(f"读取文件失败，文件路径='{file_path}', 错误: {e}")
                continue
        
        logger.info(f"成功加载 {len(documents)} 个文档")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        分割文档为小块
        
        Args:
            documents: 原始文档列表
            
        Returns:
            分割后的文档块列表
        """
        logger.info(f"开始分割 {len(documents)} 个文档")
        
        split_docs = []
        for doc in documents:
            try:
                # 分割文档
                chunks = self.text_splitter.split_documents([doc])
                
                # 为每个块添加额外的元数据
                for i, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        "chunk_id": i,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk.page_content)
                    })
                
                split_docs.extend(chunks)
                logger.debug(f"文档 {doc.metadata.get('filename', 'unknown')} 分割为 {len(chunks)} 块")
                
            except Exception as e:
                filename = doc.metadata.get('filename', 'unknown')
                source = doc.metadata.get('source', 'unknown')
                logger.error(f"分割文档失败，文件名='{filename}', 源路径='{source}', 错误: {e}")
                continue
        
        logger.info(f"文档分割完成，共生成 {len(split_docs)} 个文档块")
        return split_docs

    def _filter_files(self, files: List[str]) -> List[str]:
        """
        应用项目类型感知的文件过滤

        Args:
            files: 文件列表
            project_type: 项目类型

        Returns:
            过滤后的文件列表
        """
        filtered_files = [file_path for file_path in files if self.config.should_embedding(file_path)]
        return filtered_files
