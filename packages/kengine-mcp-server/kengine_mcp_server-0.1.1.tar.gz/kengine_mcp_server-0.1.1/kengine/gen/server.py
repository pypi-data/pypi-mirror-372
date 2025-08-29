"""
文档生成HTTP服务器实现
"""

import json
import logging
import threading
from datetime import datetime
from typing import Any, Dict, Optional, List
from flask import Flask, request, Response, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import os

from .models import DocumentGenerationRequest, ProgressUpdate, TaskInfo
from ..core.enums import ProgressType
from ..core.types import KnowledgeGenerationRequest
from ..core.progress import progress_manager
from ..scheduler.schedule import get_knowledge_scheduler

logger = logging.getLogger(__name__)


class DocumentGenerationServer:
    """文档生成HTTP服务器"""
    
    def __init__(self, port: int = 8081):
        self.app = Flask(__name__)
        CORS(self.app)  # 启用CORS支持
        
        self.knowledge_scheduler = get_knowledge_scheduler()
        self.port = port
        
        # 任务管理
        self.tasks: Dict[int, TaskInfo] = {}
        self._tasks_lock = threading.Lock()
        
        # 数据库任务服务
        from ..core.services import task_service
        self.task_service = task_service
        
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """健康检查"""
            return jsonify({"status": "healthy", "service": "document_generation"})
        
        @self.app.route('/', methods=['GET'])
        def index():
            """主页"""
            template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                return jsonify({"error": "前端页面未找到"}), 404
        
        @self.app.route('/api/generate', methods=['POST'])
        def generate_documents():
            """文档生成接口"""
            try:
                # 解析请求
                data = request.get_json()
                if not data:
                    return jsonify({"error": "请求体不能为空"}), 400
                
                doc_request = DocumentGenerationRequest.from_dict(data)
                
                # 验证必要参数
                if not doc_request.repo_group or not doc_request.repo_name:
                    return jsonify({"error": "仓库组和仓库名不能为空"}), 400
                
                # 创建知识生成请求
                knowledge_request = KnowledgeGenerationRequest(
                    repo_group=doc_request.repo_group,
                    repo_name=doc_request.repo_name,
                    branch=doc_request.branch
                )
                
                # 启动文档生成任务 - 使用 KnowledgeScheduler
                task_id = self.knowledge_scheduler.schedule_generation_task(knowledge_request)
                
                # 在HTTP API层创建任务信息用于状态跟踪
                from .models import TaskInfo
                with self._tasks_lock:
                    self.tasks[task_id] = TaskInfo(
                        task_id=task_id,
                        status="created",
                        repo_group=knowledge_request.repo_group,
                        repo_name=knowledge_request.repo_name,
                        created_at=datetime.now().isoformat()
                    )
                
                return jsonify({
                    "task_id": task_id,
                    "status": "created",
                    "message": "文档生成任务已创建"
                })
                    
            except ValueError as e:
                logger.error(f"请求参数错误: {e}")
                return jsonify({"error": f"参数错误: {str(e)}"}), 400
            except Exception as e:
                logger.error(f"文档生成失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/tasks', methods=['GET'])
        def list_tasks():
            """获取任务列表"""
            try:
                # 从数据库获取任务列表
                db_tasks = self.task_service.get_all_tasks(order_by='created_at', desc_order=True)
                
                # 转换为API响应格式
                tasks = []
                for db_task in db_tasks:
                    task_dict = {
                        'task_id': db_task.id,
                        'status': db_task.status,
                        'repo_group': db_task.repo_group,
                        'repo_name': db_task.repo_name,
                        'created_at': db_task.created_at.isoformat() if db_task.created_at else None,
                        'overall_progress': db_task.progress_percentage,
                        'current_stage': None,  # 可以从进度记录中获取
                        'completed_documents': db_task.completed_documents or 0,
                        'total_documents': db_task.total_documents or 0,
                        'error': db_task.error_message,
                        'output_path': db_task.output_path,
                        'llm_stats': None  # 可以从关联的统计数据中获取
                    }
                    tasks.append(task_dict)
                
                return jsonify({"tasks": tasks})
                
            except Exception as e:
                logger.error(f"获取任务列表失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/tasks/<task_id>', methods=['GET'])
        def get_task(task_id: int):
            """获取任务详情"""
            try:
                # 转换task_id为整数
                task_id = int(task_id)
                
                # 从数据库获取任务详情
                db_task = self.task_service.get_task_by_id(task_id)
                
                if not db_task:
                    return jsonify({"error": "任务不存在"}), 404
                
                # 转换为API响应格式
                task_dict = {
                    'task_id': db_task.id,
                    'status': db_task.status,
                    'repo_group': db_task.repo_group,
                    'repo_name': db_task.repo_name,
                    'created_at': db_task.created_at.isoformat() if db_task.created_at else None,
                    'started_at': db_task.started_at.isoformat() if db_task.started_at else None,
                    'completed_at': db_task.completed_at.isoformat() if db_task.completed_at else None,
                    'overall_progress': db_task.progress_percentage,
                    'current_stage': None,  # 可以从进度记录中获取
                    'completed_documents': db_task.completed_documents or 0,
                    'total_documents': db_task.total_documents or 0,
                    'error': db_task.error_message,
                    'output_path': db_task.output_path,
                    'project_path': db_task.project_path,
                    'branch': db_task.branch,
                    'model_name': db_task.model_name,
                    'llm_stats': None  # 可以从关联的统计数据中获取
                }
                
                return jsonify(task_dict)
                
            except Exception as e:
                logger.error(f"获取任务详情失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/tasks/<task_id>/progress', methods=['GET'])
        def get_task_progress_stream(task_id: int):
            """获取任务进度流"""
            try:
                # 转换task_id为整数
                task_id = int(task_id)
                
                # 检查任务是否存在于数据库中
                db_task = self.task_service.get_task_by_id(task_id)
                if not db_task:
                    return jsonify({"error": "任务不存在"}), 404
                
                return self._handle_progress_stream(task_id)
                
            except Exception as e:
                logger.error(f"获取进度流失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/tasks/<task_id>', methods=['DELETE'])
        def cancel_task(task_id: int):
            """取消任务"""
            try:
                # 转换task_id为整数
                task_id = int(task_id)
                
                # 从数据库取消任务
                cancelled_task = self.task_service.cancel_task(task_id)
                if not cancelled_task:
                    return jsonify({"error": "任务不存在"}), 404
                
                return jsonify({"message": "任务已取消"})
                
            except Exception as e:
                logger.error(f"取消任务失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/tasks/<task_id>/llm-stats', methods=['GET'])
        def get_task_llm_stats(task_id: int):
            """获取任务的大模型调用统计信息"""
            try:
                # 转换task_id为整数
                task_id = int(task_id)
                
                # 检查任务是否存在于数据库中
                db_task = self.task_service.get_task_by_id(task_id)
                if not db_task:
                    return jsonify({"error": "任务不存在"}), 404
                
                # 从进度管理器获取大模型统计信息
                progress_info = progress_manager.get_progress(task_id)
                if not progress_info or not progress_info.llm_stats:
                    return jsonify({
                        "task_id": task_id,
                        "llm_stats": None,
                        "message": "暂无大模型调用统计信息"
                    })
                
                # 转换为字典格式
                llm_stats_dict = progress_info.llm_stats.to_dict()
                
                return jsonify({
                    "task_id": task_id,
                    "llm_stats": llm_stats_dict
                })
                
            except Exception as e:
                logger.error(f"获取大模型统计失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/tasks/<task_id>/llm-stats/summary', methods=['GET'])
        def get_task_llm_stats_summary(task_id: int):
            """获取任务的大模型调用统计摘要"""
            try:
                # 转换task_id为整数
                task_id = int(task_id)
                
                # 检查任务是否存在于数据库中
                db_task = self.task_service.get_task_by_id(task_id)
                if not db_task:
                    return jsonify({"error": "任务不存在"}), 404
                
                # 从进度管理器获取大模型统计信息
                progress_info = progress_manager.get_progress(task_id)
                if not progress_info or not progress_info.llm_stats:
                    return jsonify({
                        "task_id": task_id,
                        "summary": {
                            "total_calls": 0,
                            "total_tokens": 0,
                            "total_cost": 0.0,
                            "success_rate": 0.0,
                            "avg_response_time": 0.0
                        }
                    })
                
                # 获取统计摘要
                stats = progress_info.llm_stats
                summary = {
                    "total_calls": stats.total_calls,
                    "total_tokens": stats.total_input_tokens + stats.total_output_tokens,
                    "total_input_tokens": stats.total_input_tokens,
                    "total_output_tokens": stats.total_output_tokens,
                    "total_cost": stats.total_cost,
                    "success_rate": stats.success_rate,
                    "avg_response_time": stats.avg_response_time,
                    "call_types": {call_type.value: count for call_type, count in stats.call_type_counts.items()},
                    "stage_count": len(stats.stage_stats)
                }
                
                return jsonify({
                    "task_id": task_id,
                    "summary": summary
                })
                
            except Exception as e:
                logger.error(f"获取大模型统计摘要失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/llm-stats/global', methods=['GET'])
        def get_global_llm_stats():
            """获取全局大模型调用统计信息"""
            try:
                # 收集所有任务的大模型统计信息
                all_stats = []
                with self._tasks_lock:
                    for task_id in self.tasks.keys():
                        progress_info = progress_manager.get_progress(task_id)
                        if progress_info and progress_info.llm_stats:
                            stats_dict = progress_info.llm_stats.to_dict()
                            stats_dict['task_id'] = task_id
                            all_stats.append(stats_dict)
                
                # 计算全局统计
                if not all_stats:
                    global_summary = {
                        "total_tasks": 0,
                        "total_calls": 0,
                        "total_tokens": 0,
                        "total_cost": 0.0,
                        "avg_success_rate": 0.0,
                        "avg_response_time": 0.0
                    }
                else:
                    total_calls = sum(stats['total_calls'] for stats in all_stats)
                    total_tokens = sum(stats['total_input_tokens'] + stats['total_output_tokens'] for stats in all_stats)
                    total_cost = sum(stats['total_cost'] for stats in all_stats)
                    avg_success_rate = sum(stats['success_rate'] for stats in all_stats) / len(all_stats)
                    avg_response_time = sum(stats['avg_response_time'] for stats in all_stats) / len(all_stats)
                    
                    global_summary = {
                        "total_tasks": len(all_stats),
                        "total_calls": total_calls,
                        "total_tokens": total_tokens,
                        "total_cost": total_cost,
                        "avg_success_rate": avg_success_rate,
                        "avg_response_time": avg_response_time
                    }
                
                return jsonify({
                    "global_summary": global_summary,
                    "task_stats": all_stats
                })
                
            except Exception as e:
                logger.error(f"获取全局大模型统计失败: {e}")
                return jsonify({"error": f"服务器错误: {str(e)}"}), 500
    
    
    def _handle_progress_stream(self, task_id: int) -> Response:
        """处理进度流"""
        def generate():
            try:
                # 发送初始状态
                with self._tasks_lock:
                    task = self.tasks.get(task_id)
                    if task:
                        initial_update = ProgressUpdate(
                            type=ProgressType.STAGE_START,
                            task_id=task_id,
                            message=f"任务状态: {task.status}",
                            overall_progress=task.overall_progress,
                            current_stage=task.current_stage,
                            completed_documents=task.completed_documents,
                            total_documents=task.total_documents
                        )
                        yield f"data: {initial_update.to_json_string()}\n\n"
                
                # 持续发送进度更新
                last_progress = -1
                while True:
                    try:
                        # 从进度管理器获取最新进度
                        progress_info = progress_manager.get_progress(task_id)
                        if progress_info and progress_info.overall_progress != last_progress:
                            # 确定更新类型
                            if progress_info.error:
                                update_type = ProgressType.ERROR
                            elif progress_info.overall_progress >= 100.0:
                                update_type = ProgressType.COMPLETE
                            else:
                                update_type = ProgressType.STAGE_PROGRESS
                            
                            progress_update = ProgressUpdate.from_progress_info(
                                progress_info, task_id, update_type
                            )
                            
                            # 如果有大模型统计信息，添加到更新中
                            if progress_info.llm_stats:
                                progress_update.llm_stats = progress_info.llm_stats.to_dict()
                            
                            yield f"data: {progress_update.to_json_string()}\n\n"
                            last_progress = progress_info.overall_progress
                            
                            # 如果任务完成或出错，结束流
                            if progress_info.overall_progress >= 100.0 or progress_info.error:
                                break
                        
                        # 检查任务状态
                        with self._tasks_lock:
                            task = self.tasks.get(task_id)
                            if task and task.status in ["completed", "failed", "cancelled"]:
                                break
                        
                        # 短暂等待
                        import time
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"进度流生成错误: {e}")
                        error_update = ProgressUpdate(
                            type=ProgressType.ERROR,
                            task_id=task_id,
                            error=str(e),
                            message=f"进度获取失败: {str(e)}"
                        )
                        yield f"data: {error_update.to_json_string()}\n\n"
                        break
                        
            except Exception as e:
                logger.error(f"进度流处理失败: {e}")
                error_update = ProgressUpdate(
                    type=ProgressType.ERROR,
                    task_id=task_id,
                    error=str(e),
                    message=f"流处理失败: {str(e)}"
                )
                yield f"data: {error_update.to_json_string()}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )
    
    
    
    def run(self, host: str = '0.0.0.0', debug: bool = False):
        """启动服务器"""
        logger.info(f"启动文档生成服务器: http://{host}:{self.port}")
        self.app.run(host=host, port=self.port, debug=debug, threaded=True)


def create_doc_server(port: int = 8081) -> DocumentGenerationServer:
    """创建文档生成服务器的便捷函数"""
    return DocumentGenerationServer(port=port)


if __name__ == "__main__":
    # 直接运行时启动服务器
    import sys
    
    port = 8081
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("端口号必须是整数")
            sys.exit(1)
    
    server = create_doc_server(port=port)
    server.run(debug=True)