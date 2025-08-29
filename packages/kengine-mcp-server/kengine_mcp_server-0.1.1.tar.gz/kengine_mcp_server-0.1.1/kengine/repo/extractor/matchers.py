"""
匹配器类

包含文件模式匹配器、注解检测器和目录分析器等核心匹配功能。
"""

import os
import re
import fnmatch
import logging
from pathlib import Path
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)


class FilePatternMatcher:
    """智能文件名模式匹配器"""
    
    def __init__(self):
        self.compiled_patterns = {}
    
    def compile_patterns(self, patterns: List[str]) -> List[re.Pattern]:
        """编译文件名模式为正则表达式"""
        compiled = []
        for pattern in patterns:
            if pattern not in self.compiled_patterns:
                # 将glob模式转换为正则表达式
                regex_pattern = fnmatch.translate(pattern)
                self.compiled_patterns[pattern] = re.compile(regex_pattern, re.IGNORECASE)
            compiled.append(self.compiled_patterns[pattern])
        return compiled
    
    def match_file(self, file_path: str, patterns: List[str]) -> Tuple[bool, List[str]]:
        """匹配文件路径与模式列表"""
        file_name = os.path.basename(file_path)
        compiled_patterns = self.compile_patterns(patterns)
        matches = []
        
        for i, pattern_obj in enumerate(compiled_patterns):
            if pattern_obj.match(file_name):
                matches.append(patterns[i])
        
        return len(matches) > 0, matches
    
    def calculate_pattern_score(self, matches: List[str]) -> float:
        """计算模式匹配得分"""
        if not matches:
            return 0.0
        
        # 更具体的模式得分更高
        base_score = 0.3
        specificity_bonus = 0.0
        
        for match in matches:
            # 计算模式的具体性
            if '*' not in match:  # 精确匹配，如 "UserController.java"
                specificity_bonus += 0.4
            elif match.count('*') == 1:  # 单通配符，如 "*.controller.js"
                specificity_bonus += 0.2
            else:  # 多通配符，如 "*.*.java"
                specificity_bonus += 0.1
        
        return min(base_score + specificity_bonus, 1.0)


class AnnotationDetector:
    """注解/装饰器识别器"""
    
    def __init__(self):
        self.annotation_cache = {}
    
    def detect_annotations(self, file_path: str, target_annotations: List[str]) -> Tuple[List[str], float]:
        """检测文件中的注解/装饰器"""
        cache_key = f"{file_path}:{hash(tuple(target_annotations))}"
        if cache_key in self.annotation_cache:
            return self.annotation_cache[cache_key]
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            found_annotations = []
            for annotation in target_annotations:
                # 使用正则表达式匹配注解
                pattern = re.escape(annotation).replace(r'\*', '.*')
                if re.search(pattern, content, re.MULTILINE):
                    found_annotations.append(annotation)
            
            # 计算注解匹配得分
            score = len(found_annotations) / len(target_annotations) if target_annotations else 0.0
            
            result = (found_annotations, score)
            self.annotation_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.warning(f"检测注解时出错 {file_path}: {e}")
            return [], 0.0
    
    def extract_endpoint_patterns(self, file_path: str, language: str) -> List[str]:
        """提取端点模式（如路由路径）"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            patterns = []
            
            if language == 'java':
                # Spring Boot 路由模式
                spring_patterns = re.findall(r'@RequestMapping\(["\']([^"\']+)["\']', content)
                spring_patterns.extend(re.findall(r'@GetMapping\(["\']([^"\']+)["\']', content))
                spring_patterns.extend(re.findall(r'@PostMapping\(["\']([^"\']+)["\']', content))
                patterns.extend(spring_patterns)
                
            elif language == 'python':
                # Flask/Django 路由模式
                flask_patterns = re.findall(r'@app\.route\(["\']([^"\']+)["\']', content)
                django_patterns = re.findall(r'path\(["\']([^"\']+)["\']', content)
                patterns.extend(flask_patterns + django_patterns)
                
            elif language in ['javascript', 'typescript']:
                # Express.js 路由模式
                express_patterns = re.findall(r'\.(?:get|post|put|delete)\(["\']([^"\']+)["\']', content)
                patterns.extend(express_patterns)
            
            return patterns
            
        except Exception as e:
            logger.warning(f"提取端点模式时出错 {file_path}: {e}")
            return []


class DirectoryAnalyzer:
    """目录结构分析器"""
    
    def __init__(self):
        self.mvc_patterns = {
            'controller': ['controller', 'controllers', 'ctrl'],
            'service': ['service', 'services', 'svc'],
            'api': ['api', 'apis', 'rest'],
            'handler': ['handler', 'handlers', 'handle'],
            'router': ['router', 'routers', 'routes', 'routing']
        }
    
    def analyze_directory_structure(self, file_path: str) -> Tuple[List[str], float]:
        """分析文件所在目录结构"""
        path_parts = Path(file_path).parts
        matched_patterns = []
        
        for part in path_parts:
            part_lower = part.lower()
            for pattern_type, patterns in self.mvc_patterns.items():
                if any(pattern in part_lower for pattern in patterns):
                    matched_patterns.append(pattern_type)
        
        # 计算目录结构得分
        score = len(matched_patterns) * 0.3  # 每个匹配的目录模式贡献0.3分
        return matched_patterns, min(score, 1.0)