"""
Git代码库克隆功能模块

通过 git clone 命令将给定代码库clone到本地的某个文件夹下
要能够显示clone过程
可以先不考虑权限问题， 假定有clone权限
"""


import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import shutil


class GitCloneError(Exception):
    """Git克隆过程中的异常"""
    pass


class GitCloner:
    """Git代码库克隆器"""
    
    def __init__(self, progress_callback: Optional[Callable[[str], None]] = None):
        """
        初始化Git克隆器
        
        Args:
            progress_callback: 进度回调函数，用于显示克隆过程
        """
        self.progress_callback = progress_callback or self._default_progress_callback
    
    def _default_progress_callback(self, message: str):
        """默认的进度显示回调"""
        print(f"[Git Clone] {message}")
    
    def _check_git_available(self) -> bool:
        """检查系统是否安装了git"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _validate_url(self, repo_url: str) -> bool:
        """验证仓库URL格式"""
        if not repo_url or not isinstance(repo_url, str):
            return False
        
        # 支持的URL格式
        valid_prefixes = [
            'https://',
            'http://',
            'git@',
            'ssh://',
            'git://'
        ]
        
        return any(repo_url.startswith(prefix) for prefix in valid_prefixes)
    
    def _prepare_target_directory(self, target_dir: str, force: bool = False) -> Path:
        """准备目标目录"""
        target_path = Path(target_dir).resolve()
        
        if target_path.exists():
            if not force:
                raise GitCloneError(f"目标目录已存在: {target_path}")
            else:
                self.progress_callback(f"删除已存在的目录: {target_path}")
                shutil.rmtree(target_path)
        
        # 确保父目录存在
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        return target_path
    
    def clone(self, 
              repo_url: str, 
              target_dir: str,
              branch: Optional[str] = None,
              depth: Optional[int] = None,
              recursive: bool = False,
              force: bool = False,
              **kwargs) -> Dict[str, Any]:
        """
        克隆Git仓库
        
        Args:
            repo_url: 仓库URL
            target_dir: 目标目录
            branch: 指定分支（可选）
            depth: 克隆深度，用于浅克隆（可选）
            recursive: 是否递归克隆子模块
            force: 如果目标目录存在是否强制删除
            **kwargs: 其他git clone参数
            
        Returns:
            Dict包含克隆结果信息
            
        Raises:
            GitCloneError: 克隆过程中的错误
        """
        
        # 检查git是否可用
        if not self._check_git_available():
            raise GitCloneError("系统未安装git或git不可用")
        
        # 验证URL
        if not self._validate_url(repo_url):
            raise GitCloneError(f"无效的仓库URL: {repo_url}")
        
        # 检查目标目录是否已存在且为git仓库
        target_path = Path(target_dir).resolve()
        if target_path.exists() and any(target_path.iterdir()):  # 目录存在且非空
            git_dir = target_path / '.git'
            if git_dir.exists():
                # 已经是git仓库，跳过克隆
                self.progress_callback(f"✅ 目标目录已存在git仓库，跳过克隆: {target_path}")
                return {
                    'success': True,
                    'repo_url': repo_url,
                    'target_dir': str(target_path),
                    'branch': branch,
                    'depth': depth,
                    'recursive': recursive,
                    'skipped': True,
                    'reason': '目标目录已存在git仓库',
                    'output': []
                }
        
        # 准备目标目录
        try:
            target_path = self._prepare_target_directory(target_dir, force)
        except Exception as e:
            raise GitCloneError(f"准备目标目录失败，目标目录='{target_dir}', force={force}: {e}")
        
        # 构建git clone命令
        cmd = ['git', 'clone']
        
        # 添加可选参数
        if branch:
            cmd.extend(['--branch', branch])
        
        if depth and depth > 0:
            cmd.extend(['--depth', str(depth)])
        
        if recursive:
            cmd.append('--recursive')
        
        # 添加其他参数
        for key, value in kwargs.items():
            if key.startswith('--'):
                if value is True:
                    cmd.append(key)
                elif value is not False and value is not None:
                    cmd.extend([key, str(value)])
        
        # 添加仓库URL和目标目录
        cmd.extend([repo_url, str(target_path)])
        
        self.progress_callback(f"开始克隆仓库: {repo_url}")
        self.progress_callback(f"目标目录: {target_path}")
        self.progress_callback(f"执行命令: {' '.join(cmd)}")
        
        # 执行克隆命令
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                bufsize=1
            )
            
            # 实时显示输出
            output_lines = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    self.progress_callback(line)
            
            # 等待进程完成
            return_code = process.wait()
            
            if return_code != 0:
                raise GitCloneError(f"Git克隆失败，仓库URL='{repo_url}', 目标目录='{target_path}', 分支='{branch}', 返回码={return_code}")
            
            # 验证克隆结果
            if not target_path.exists() or not (target_path / '.git').exists():
                raise GitCloneError(f"克隆完成但目标目录不包含有效的git仓库，仓库URL='{repo_url}', 目标目录='{target_path}'")
            
            self.progress_callback("✅ 克隆完成!")
            
            # 返回结果信息
            result = {
                'success': True,
                'repo_url': repo_url,
                'target_dir': str(target_path),
                'branch': branch,
                'depth': depth,
                'recursive': recursive,
                'skipped': False,
                'output': output_lines
            }
            
            return result
            
        except subprocess.TimeoutExpired:
            raise GitCloneError(f"克隆操作超时，仓库URL='{repo_url}', 目标目录='{target_path}'")
        except Exception as e:
            raise GitCloneError(f"克隆过程中发生错误，仓库URL='{repo_url}', 目标目录='{target_path}': {e}")


def clone_repository(repo_url: str, 
                    target_dir: str,
                    branch: Optional[str] = None,
                    depth: Optional[int] = None,
                    recursive: bool = False,
                    force: bool = False,
                    progress_callback: Optional[Callable[[str], None]] = None,
                    **kwargs) -> Dict[str, Any]:
    """
    便捷的仓库克隆函数
    
    Args:
        repo_url: 仓库URL
        target_dir: 目标目录
        branch: 指定分支（可选）
        depth: 克隆深度（可选）
        recursive: 是否递归克隆子模块
        force: 如果目标目录存在是否强制删除
        progress_callback: 进度回调函数
        **kwargs: 其他git clone参数
        
    Returns:
        Dict包含克隆结果信息
        
    Raises:
        GitCloneError: 克隆过程中的错误
    """
    cloner = GitCloner(progress_callback)
    return cloner.clone(
        repo_url=repo_url,
        target_dir=target_dir,
        branch=branch,
        depth=depth,
        recursive=recursive,
        force=force,
        **kwargs
    )
    