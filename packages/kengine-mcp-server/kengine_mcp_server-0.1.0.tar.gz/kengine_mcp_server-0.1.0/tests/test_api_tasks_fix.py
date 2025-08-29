"""
测试 GET /api/tasks API 修复
验证任务列表能够正确从数据库获取
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch

from kengine.gen.server import DocumentGenerationServer
from kengine.core.models.task import Task
from kengine.core.enums import TaskStatus


class TestTasksAPIFix:
    """测试任务API修复"""
    
    def setup_method(self):
        """测试前准备"""
        self.server = DocumentGenerationServer(port=8082)
        self.app = self.server.app.test_client()
    
    @patch('kengine.core.services.task_service.TaskService')
    def test_list_tasks_from_database(self, mock_task_repo_class):
        """测试从数据库获取任务列表"""
        # 模拟数据库中的任务
        mock_task1 = Mock(spec=Task)
        mock_task1.id = 1
        mock_task1.status = TaskStatus.COMPLETED.value
        mock_task1.repo_group = "test-org"
        mock_task1.repo_name = "test-repo"
        mock_task1.created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_task1.progress_percentage = 100.0
        mock_task1.completed_documents = 5
        mock_task1.total_documents = 5
        mock_task1.error_message = None
        mock_task1.output_path = "/path/to/output"
        
        mock_task2 = Mock(spec=Task)
        mock_task2.id = 2
        mock_task2.status = TaskStatus.RUNNING.value
        mock_task2.repo_group = "test-org"
        mock_task2.repo_name = "another-repo"
        mock_task2.created_at = datetime(2024, 1, 2, 12, 0, 0)
        mock_task2.progress_percentage = 50.0
        mock_task2.completed_documents = 2
        mock_task2.total_documents = 4
        mock_task2.error_message = None
        mock_task2.output_path = None
        
        # 配置mock service
        mock_service_instance = Mock()
        mock_service_instance.get_all_tasks.return_value = [mock_task1, mock_task2]
        mock_task_repo_class.return_value = mock_service_instance
        
        # 重新创建server以使用mock
        server = DocumentGenerationServer(port=8082)
        app = server.app.test_client()
        
        # 发送请求
        response = app.get('/api/tasks')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'tasks' in data
        assert len(data['tasks']) == 2
        
        # 验证第一个任务
        task1 = data['tasks'][0]
        assert task1['task_id'] == 1
        assert task1['status'] == TaskStatus.COMPLETED.value
        assert task1['repo_group'] == "test-org"
        assert task1['repo_name'] == "test-repo"
        assert task1['overall_progress'] == 100.0
        assert task1['completed_documents'] == 5
        assert task1['total_documents'] == 5
        assert task1['output_path'] == "/path/to/output"
        
        # 验证第二个任务
        task2 = data['tasks'][1]
        assert task2['task_id'] == 2
        assert task2['status'] == TaskStatus.RUNNING.value
        assert task2['overall_progress'] == 50.0
        assert task2['completed_documents'] == 2
        assert task2['total_documents'] == 4
        
        # 验证调用了正确的service方法
        mock_service_instance.get_all_tasks.assert_called_once_with(order_by='created_at', desc_order=True)
    
    @patch('kengine.core.services.task_service.TaskService')
    def test_get_task_from_database(self, mock_task_repo_class):
        """测试从数据库获取单个任务"""
        # 模拟数据库中的任务
        mock_task = Mock(spec=Task)
        mock_task.id = 1
        mock_task.status = TaskStatus.COMPLETED.value
        mock_task.repo_group = "test-org"
        mock_task.repo_name = "test-repo"
        mock_task.created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_task.started_at = datetime(2024, 1, 1, 12, 5, 0)
        mock_task.completed_at = datetime(2024, 1, 1, 12, 30, 0)
        mock_task.progress_percentage = 100.0
        mock_task.completed_documents = 5
        mock_task.total_documents = 5
        mock_task.error_message = None
        mock_task.output_path = "/path/to/output"
        mock_task.project_path = "/path/to/project"
        mock_task.branch = "main"
        mock_task.model_name = "gpt-4"
        
        # 配置mock service
        mock_service_instance = Mock()
        mock_service_instance.get_task_by_id.return_value = mock_task
        mock_task_repo_class.return_value = mock_service_instance
        
        # 重新创建server以使用mock
        server = DocumentGenerationServer(port=8082)
        app = server.app.test_client()
        
        # 发送请求
        response = app.get('/api/tasks/1')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['task_id'] == 1
        assert data['status'] == TaskStatus.COMPLETED.value
        assert data['repo_group'] == "test-org"
        assert data['repo_name'] == "test-repo"
        assert data['branch'] == "main"
        assert data['model_name'] == "gpt-4"
        assert data['overall_progress'] == 100.0
        assert data['completed_documents'] == 5
        assert data['total_documents'] == 5
        assert data['output_path'] == "/path/to/output"
        assert data['project_path'] == "/path/to/project"
        
        # 验证调用了正确的service方法
        mock_service_instance.get_task_by_id.assert_called_once_with(1)
    
    @patch('kengine.core.services.task_service.TaskService')
    def test_get_nonexistent_task(self, mock_task_repo_class):
        """测试获取不存在的任务"""
        # 配置mock service返回None
        mock_service_instance = Mock()
        mock_service_instance.get_task_by_id.return_value = None
        mock_task_repo_class.return_value = mock_service_instance
        
        # 重新创建server以使用mock
        server = DocumentGenerationServer(port=8082)
        app = server.app.test_client()
        
        # 发送请求
        response = app.get('/api/tasks/999')
        
        # 验证响应
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == "任务不存在"
    
    @patch('kengine.core.services.task_service.TaskService')
    def test_cancel_task_from_database(self, mock_task_repo_class):
        """测试从数据库取消任务"""
        # 模拟取消后的任务
        mock_cancelled_task = Mock(spec=Task)
        mock_cancelled_task.id = 1
        mock_cancelled_task.status = TaskStatus.CANCELLED.value
        
        # 配置mock service
        mock_service_instance = Mock()
        mock_service_instance.cancel_task.return_value = mock_cancelled_task
        mock_task_repo_class.return_value = mock_service_instance
        
        # 重新创建server以使用mock
        server = DocumentGenerationServer(port=8082)
        app = server.app.test_client()
        
        # 发送请求
        response = app.delete('/api/tasks/1')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "任务已取消"
        
        # 验证调用了正确的service方法
        mock_service_instance.cancel_task.assert_called_once_with(1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])