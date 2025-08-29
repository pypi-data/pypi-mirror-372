"""
语言规则引擎

统一的语言规则引擎，负责管理各种编程语言的识别规则和评估逻辑。
"""

import os
import threading
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .models import LanguageRule, EndpointCandidate
from .matchers import FilePatternMatcher, AnnotationDetector, DirectoryAnalyzer

logger = logging.getLogger(__name__)


class LanguageRuleEngine:
    """统一的语言规则引擎"""
    
    def __init__(self):
        self.rules = self._initialize_language_rules()
        self.file_matcher = FilePatternMatcher()
        self.annotation_detector = AnnotationDetector()
        self.directory_analyzer = DirectoryAnalyzer()
        self.cache = {}
        self.cache_lock = threading.Lock()
    
    def _initialize_language_rules(self) -> Dict[str, LanguageRule]:
        """初始化语言规则"""
        return {
            'java': LanguageRule(
                name='java',
                file_patterns=[
                    '*Controller.java', '*Service.java', '*Consumer.java', 
                    '*ServiceImpl.java', '*Client.java', '*Feign.java',
                    '*RestController.java', '*ApiController.java'
                ],
                annotations=[
                    '@RestController', '@Controller', '@Service', '@Component', 
                    '@Consumer', '@RequestMapping', '@GetMapping', '@PostMapping',
                    '@PutMapping', '@DeleteMapping', '@FeignClient'
                ],
                directories=[
                    'controller', 'service', 'consumer', 'api', 'rest',
                    'web', 'endpoint', 'resource'
                ],
                priority_weight=1.0,
                framework_hints=['spring', 'springboot', 'jersey', 'jax-rs']
            ),
            
            'python': LanguageRule(
                name='python',
                file_patterns=[
                    '*_controller.py', '*_service.py', '*_api.py', '*_handler.py',
                    'views.py', '*_views.py', 'urls.py', '*_routes.py',
                    '*_router.py', '*_endpoint.py', 'main.py', 'app.py',
                    '*_blueprint.py', 'wsgi.py', 'asgi.py', 'orders.py',
                    'users.py', 'products.py', 'auth.py', 'payments.py'
                ],
                annotations=[
                    '@app.route', '@api_view', '@router.get', '@router.post',
                    '@router.put', '@router.delete', '@bp.route', '@api.route',
                    '@router.get(', '@router.post(', '@router.put(', '@router.delete('
                ],
                directories=[
                    'views', 'api', 'controllers', 'handlers', 'routers',
                    'endpoints', 'blueprints', 'resources'
                ],
                priority_weight=1.0,
                framework_hints=['django', 'flask', 'fastapi', 'tornado', 'pyramid']
            ),
            
            'javascript': LanguageRule(
                name='javascript',
                file_patterns=[
                    '*.controller.js', '*.service.js', '*.module.js',
                    '*_routes.js', '*_api.js', '*_handler.js', 'app.js',
                    'server.js', 'index.js', '*_router.js', '*Controller.js',
                    'productController.js', 'userController.js', 'authController.js'
                ],
                annotations=[
                    '@Controller()', '@Get()', '@Post()', '@Injectable()',
                    '@Route()', '@Middleware()', 'router.get(', 'router.post(',
                    'router.put(', 'router.delete(', 'app.get(', 'app.post('
                ],
                directories=[
                    'controllers', 'services', 'routes', 'api', 'handlers',
                    'pages/api', 'app/api', 'src/api', 'middleware'
                ],
                priority_weight=1.0,
                framework_hints=['express', 'nestjs', 'koa', 'hapi', 'nextjs']
            ),
            
            'typescript': LanguageRule(
                name='typescript',
                file_patterns=[
                    '*.controller.ts', '*Controller.ts', '*.service.ts', '*.module.ts',
                    '*_routes.ts', '*_api.ts', '*_handler.ts', 'app.ts',
                    'server.ts', 'main.ts', '*_router.ts', '*Router.ts'
                ],
                annotations=[
                    '@Controller()', '@Get()', '@Post()', '@Injectable()',
                    '@Route()', '@Middleware()', '@ApiTags()', '@Controller',
                    '@Get', '@Post', '@Put', '@Delete', '@Param', '@Body', '@Query'
                ],
                directories=[
                    'controllers', 'services', 'routes', 'api', 'handlers',
                    'pages/api', 'app/api', 'src/api', 'middleware'
                ],
                priority_weight=1.0,
                framework_hints=['nestjs', 'express', 'koa', 'nextjs', 'angular']
            ),
            
            'go': LanguageRule(
                name='go',
                file_patterns=[
                    '*_handler.go', '*_controller.go', '*_server.go', 
                    '*_router.go', '*_service.go', '*_pb.go', '*_client.go',
                    'main.go', 'server.go', 'api.go'
                ],
                annotations=[
                    '// @Router', '// @Summary', '// @Tags', '// @Accept',
                    '// @Produce', '// @Param'
                ],
                directories=[
                    'handlers', 'controllers', 'routers', 'services', 'api',
                    'cmd', 'internal', 'pkg'
                ],
                priority_weight=1.0,
                framework_hints=['gin', 'echo', 'fiber', 'gorilla', 'chi']
            ),
            
            'csharp': LanguageRule(
                name='csharp',
                file_patterns=[
                    '*Controller.cs', '*ApiController.cs', '*Service.cs',
                    'I*Service.cs', '*Middleware.cs', '*Hub.cs', 'Startup.cs',
                    'Program.cs'
                ],
                annotations=[
                    '[ApiController]', '[Route]', '[HttpGet]', '[HttpPost]',
                    '[HttpPut]', '[HttpDelete]', '[Authorize]'
                ],
                directories=[
                    'Controllers', 'Services', 'Api', 'Hubs', 'Middleware',
                    'Areas', 'Features'
                ],
                priority_weight=1.0,
                framework_hints=['aspnet', 'webapi', 'mvc', 'blazor']
            ),
            
            'php': LanguageRule(
                name='php',
                file_patterns=[
                    '*Controller.php', '*Action.php', '*_api.php', 
                    '*_handler.php', 'routes.php', 'api.php', 'web.php'
                ],
                annotations=[
                    '@Route', '@Controller', '@Api', '@Get', '@Post',
                    '@Middleware'
                ],
                directories=[
                    'Controllers', 'Api', 'Http/Controllers', 'routes',
                    'app/Http', 'src/Controller'
                ],
                priority_weight=1.0,
                framework_hints=['laravel', 'symfony', 'codeigniter', 'yii']
            )
        }
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """检测文件语言"""
        ext = Path(file_path).suffix.lower()
        
        language_map = {
            '.java': 'java',
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.go': 'go',
            '.cs': 'csharp',
            '.php': 'php'
        }
        
        return language_map.get(ext)
    
    def evaluate_file(self, file_path: str) -> Optional[EndpointCandidate]:
        """评估文件是否为端点候选项"""
        language = self.detect_language(file_path)
        if not language or language not in self.rules:
            return None
        
        rule = self.rules[language]
        match_reasons = []
        total_score = 0.0
        
        # 1. 文件名模式匹配
        pattern_match, matched_patterns = self.file_matcher.match_file(file_path, rule.file_patterns)
        if pattern_match:
            pattern_score = self.file_matcher.calculate_pattern_score(matched_patterns)
            total_score += pattern_score * 0.5  # 文件名模式权重50%
            match_reasons.extend([f"文件名匹配模式: {p}" for p in matched_patterns])
        
        # 2. 目录结构分析
        dir_patterns, dir_score = self.directory_analyzer.analyze_directory_structure(file_path)
        if dir_patterns:
            total_score += dir_score * 0.25  # 目录结构权重25%
            match_reasons.extend([f"目录结构匹配: {p}" for p in dir_patterns])
        
        # 3. 注解检测
        annotations, annotation_score = self.annotation_detector.detect_annotations(file_path, rule.annotations)
        if annotations:
            total_score += annotation_score * 0.4  # 注解权重40%
            match_reasons.extend([f"注解匹配: {a}" for a in annotations])
        
        # 应用语言优先级权重
        total_score *= rule.priority_weight
        
        # 只有得分超过阈值的文件才被认为是候选项
        if total_score >= 0.1:
            return EndpointCandidate(
                file_path=file_path,
                language=language,
                confidence_score=min(total_score, 1.0),
                match_reasons=match_reasons
            )
        
        return None