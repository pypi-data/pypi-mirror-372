"""
主提取器

代码库端点提取器的主要实现，负责协调各个组件完成端点提取任务。
"""

import os
import re
import time
import hashlib
import threading
import logging
from pathlib import Path
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import EndpointCandidate
from .rule_engine import LanguageRuleEngine
from ...code.skeleton import extract_skeleton, validate_file_for_skeleton_extraction

logger = logging.getLogger(__name__)


class RepoEndpointExtractor:
    """代码库端点提取器主类"""
    
    def __init__(self, max_workers: int = 4, enable_cache: bool = True):
        self.rule_engine = LanguageRuleEngine()
        self.max_workers = max_workers
        self.enable_cache = enable_cache
        self.file_cache = {}
        self.cache_lock = threading.Lock()
    
    def _get_file_hash(self, file_path: str) -> str:
        """获取文件内容哈希值用于缓存"""
        try:
            stat = os.stat(file_path)
            return hashlib.md5(f"{file_path}:{stat.st_mtime}:{stat.st_size}".encode()).hexdigest()
        except:
            return ""
    
    def _collect_source_files(self, repo_path: str) -> List[str]:
        """收集代码库中的源代码文件"""
        source_files = []
        supported_extensions = {'.java', '.py', '.js', '.ts', '.go', '.cs', '.php'}
        
        try:
            for root, dirs, files in os.walk(repo_path):
                # 获取当前目录的末级路径名
                base_dir_name = os.path.basename(root).lower()
                
                # 跳过常见的非源码目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and
                          d not in {'node_modules', 'target', 'build', 'dist', '__pycache__', 'vendor'}]
                
                for file in files:
                    if Path(file).suffix.lower() in supported_extensions:
                        file_path = os.path.join(root, file)
                        
                        # 检查文件路径是否是测试文件 (更精确的匹配)
                        # 排除 tests/ 目录下的文件，或者文件名以 test_ 开头或 _test 结尾的文件
                        if (re.search(r'/tests?/', file_path, re.IGNORECASE) or
                            re.search(r'[/\\]?test_[^/\\]*\.[^/\\]+$', file_path, re.IGNORECASE) or
                            re.search(r'[/\\]?[^/\\]*_test\.[^/\\]+$', file_path, re.IGNORECASE)):
                            logger.debug(f"排除测试相关文件: {file_path}")
                            continue
                            
                        source_files.append(file_path)
        
        except Exception as e:
            logger.error(f"收集源文件时出错: {e} at {repo_path}")
        
        return source_files
    
    def _process_file_batch(self, files: List[str]) -> List[EndpointCandidate]:
        """批量处理文件"""
        candidates = []
        
        for file_path in files:
            try:
                # 检查缓存
                if self.enable_cache:
                    file_hash = self._get_file_hash(file_path)
                    with self.cache_lock:
                        if file_hash in self.file_cache:
                            cached_result = self.file_cache[file_hash]
                            if cached_result:
                                candidates.append(cached_result)
                            continue
                
                # 评估文件
                candidate = self.rule_engine.evaluate_file(file_path)
                
                # 更新缓存
                if self.enable_cache and file_hash:
                    with self.cache_lock:
                        self.file_cache[file_hash] = candidate
                
                if candidate:
                    candidates.append(candidate)
                    
            except Exception as e:
                logger.warning(f"处理文件时出错 {file_path}: {e}")
        
        return candidates
    
    def _extract_skeletons_for_candidates(self, candidates: List[EndpointCandidate]) -> List[EndpointCandidate]:
        """为候选项提取详细的代码骨架信息"""
        def extract_skeleton_info(candidate: EndpointCandidate) -> EndpointCandidate:
            try:
                # 验证文件是否支持骨架提取
                is_valid, validation_msg = validate_file_for_skeleton_extraction(candidate.file_path)
                if is_valid:
                    skeleton = extract_skeleton(candidate.file_path)
                    candidate.skeleton = skeleton
                    
                    # 提取端点模式
                    endpoint_patterns = self.rule_engine.annotation_detector.extract_endpoint_patterns(
                        candidate.file_path, candidate.language
                    )
                    if endpoint_patterns:
                        # 将端点模式添加到骨架信息中
                        candidate.skeleton += f"\n\n# 端点模式:\n# {', '.join(endpoint_patterns)}"
                else:
                    logger.warning(f"文件验证失败 {candidate.file_path}: {validation_msg}")
                        
            except Exception as e:
                logger.warning(f"提取骨架时出错 {candidate.file_path}: {e}")
            
            return candidate
        
        # 并行提取骨架信息
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix='repo-extractor-') as executor:
            future_to_candidate = {executor.submit(extract_skeleton_info, candidate): candidate 
                                 for candidate in candidates}
            
            results = []
            for future in as_completed(future_to_candidate):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.warning(f"并行提取骨架时出错: {e}")
        
        return results
    
    def extract_endpoints(self, repo_path: str) -> Dict[str, Any]:
        """提取代码库端点定义"""
        start_time = time.time()
        
        if not os.path.exists(repo_path):
            error_msg = f'代码库路径不存在: {repo_path}'
            logger.error(error_msg)
            return {
                'error': error_msg,
                'timestamp': time.time()
            }
            
        # 1. 收集源文件
        logger.info(f"🔍 扫描代码库: {repo_path}")
        source_files = self._collect_source_files(repo_path)
        logger.info(f"📁 发现 {len(source_files)} 个源文件")
        
        if not source_files:
            logger.warning("未发现任何源文件")
            return {
                'repo_path': repo_path,
                'total_files': 0,
                'candidates': [],
                'summary': {'total_candidates': 0, 'languages': {}},
                'processing_time': time.time() - start_time,
                'timestamp': time.time()
            }
        
        # 2. 并行评估文件
        logger.info("🔍 评估端点候选文件...")
        candidates = []
        
        # 将文件分批处理
        batch_size = max(1, len(source_files) // self.max_workers)
        file_batches = [source_files[i:i + batch_size] 
                        for i in range(0, len(source_files), batch_size)]
        
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix='repo-extractor-endpoints-') as executor:
            future_to_batch = {executor.submit(self._process_file_batch, batch): batch 
                                for batch in file_batches}
            
            for future in as_completed(future_to_batch):
                try:
                    batch_candidates = future.result()
                    candidates.extend(batch_candidates)
                except Exception as e:
                    logger.warning(f"批量处理时出错: {e}")
        
        logger.info(f"✅ 发现 {len(candidates)} 个端点候选文件")
        
        # 3. 按置信度排序
        candidates.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # 4. 提取详细骨架信息
        if candidates:
            logger.info("📝 提取详细代码骨架...")
            candidates = self._extract_skeletons_for_candidates(candidates)
            
            # 5. 按 文本相似度 去重
            from kengine.utils.similarity_calc import deduplicate_by_text_similarity
            candidates = deduplicate_by_text_similarity(candidates, lambda o : o.skeleton, 0.95)
            
            # 6. 如果候选项数量超过文件总数的 1/5， 只取 1/5, 如果大于100只取100个
            # 对于小项目（<10个文件），保留所有候选文件
            if len(source_files) < 10:
                max_candidates_count = min(100, len(candidates))
            else:
                max_candidates_count = min(100, max(1, int(len(source_files) / 5)))
            
            if len(candidates) > max_candidates_count:
                logger.info(f'候选文件数量 {len(candidates)} > {len(source_files)}/5 or 100, 保留 {max_candidates_count} 个')
                candidates = candidates[:max_candidates_count]
        
        
        processing_time = time.time() - start_time
        logger.info(f"⏱️  处理完成，耗时: {processing_time:.2f}秒")
        
        return {
            'repo_path': repo_path,
            'total_files': len(source_files),
            'candidates': [self._candidate_to_dict(c) for c in candidates],
            'processing_time': processing_time,
            'timestamp': time.time()
        }
    
    def _candidate_to_dict(self, candidate: EndpointCandidate) -> Dict[str, Any]:
        """将候选项转换为字典格式"""
        return {
            'file_path': candidate.file_path,
            'language': candidate.language,
            'confidence_score': candidate.confidence_score,
            'match_reasons': candidate.match_reasons,
            'framework': candidate.framework,
            'skeleton': candidate.skeleton
        }