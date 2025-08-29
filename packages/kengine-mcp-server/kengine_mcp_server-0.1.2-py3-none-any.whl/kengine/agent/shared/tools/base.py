"""
Agent工具基类模块

包含 BasePathTool 基类，提供通用的路径验证、解析和安全检查功能。
"""

import os
import json
import functools
from pathlib import Path
from typing import Optional, Dict, Any, Callable

from .exceptions import PathValidationError, SecurityError, FileOperationError


class BasePathTool:
    """路径处理基类
    
    提供通用的路径验证、解析和安全检查功能
    """
    
    @staticmethod
    def json_compatible_input(param_mapping: Dict[str, str]) -> Callable:
        """
        JSON兼容输入装饰器
        
        自动检测输入参数是否为JSON格式，并解析映射到方法参数。
        支持递归调用原方法，提供统一的错误处理机制。
        
        Args:
            param_mapping: JSON键到方法参数的映射字典
                          格式: {'json_key': 'method_param_name'}
                          
        Returns:
            装饰器函数
            
        Example:
            @BasePathTool.json_compatible_input({
                'path': 'file_path',
                'content': 'content'
            })
            def write_file(self, file_path: str, content: str):
                pass
                
            # 支持JSON调用: write_file('{"path": "test.txt", "content": "hello"}')
            # 也支持普通调用: write_file("test.txt", "hello")
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 如果没有位置参数，直接调用原方法
                if not args:
                    return func(*args, **kwargs)
                
                # 获取第一个参数（除了self）
                first_arg_index = 1 if args and hasattr(args[0], '__class__') else 0
                if len(args) <= first_arg_index:
                    return func(*args, **kwargs)
                
                first_param = args[first_arg_index]
                
                # 检查是否为JSON格式的字符串
                if not isinstance(first_param, str):
                    return func(*args, **kwargs)
                
                stripped_param = first_param.strip()
                if not (stripped_param.startswith('{') and stripped_param.endswith('}')):
                    return func(*args, **kwargs)
                
                # 尝试解析JSON
                try:
                    json_data = json.loads(stripped_param)
                    if not isinstance(json_data, dict):
                        return func(*args, **kwargs)
                    
                    # 映射JSON参数到方法参数
                    mapped_kwargs = {}
                    for json_key, param_name in param_mapping.items():
                        if json_key in json_data:
                            mapped_kwargs[param_name] = json_data[json_key]
                    
                    # 检查是否有任何映射成功，如果没有则当作普通字符串处理
                    if not mapped_kwargs:
                        return func(*args, **kwargs)
                    
                    # 合并现有的kwargs
                    final_kwargs = {**kwargs, **mapped_kwargs}
                    
                    # 构建新的args（移除JSON参数）
                    new_args = args[:first_arg_index] + args[first_arg_index + 1:]
                    
                    # 递归调用原方法
                    return func(*new_args, **final_kwargs)
                    
                except json.JSONDecodeError as e:
                    # JSON解析失败，抛出FileOperationError
                    tool_name = args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else 'Unknown'
                    raise FileOperationError(
                        f"JSON参数解析失败: {str(e)}",
                        operation="json_parse",
                        tool_name=tool_name,
                        suggestions=[
                            "检查JSON格式是否正确",
                            "确保使用双引号包围键和字符串值",
                            "验证JSON语法的完整性"
                        ]
                    ) from e
                except Exception as e:
                    # 其他异常，也包装为FileOperationError
                    tool_name = args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else 'Unknown'
                    raise FileOperationError(
                        f"JSON兼容处理失败: {str(e)}",
                        operation="json_compatibility",
                        tool_name=tool_name,
                        suggestions=[
                            "检查参数映射配置是否正确",
                            "验证JSON参数格式",
                            "尝试使用普通参数调用"
                        ]
                    ) from e
            
            return wrapper
        return decorator
    
    def __init__(self, base_dir: str):
        """
        初始化基类
        
        Args:
            base_dir: 基础目录路径，必须是有效的目录
            
        Raises:
            PathValidationError: 基础目录无效
        """
        if not base_dir:
            raise PathValidationError("base_dir参数不能为空", tool_name=self.__class__.__name__)
        
        try:
            self.base_dir = Path(base_dir).resolve()
            self._validate_base_directory()
        except Exception as e:
            raise PathValidationError(
                f"{self.__class__.__name__}初始化失败，base_dir={base_dir}: {str(e)}", 
                path=base_dir,
                tool_name=self.__class__.__name__
            ) from e
    
    def _validate_base_directory(self) -> None:
        """
        验证基础目录的有效性
        
        Raises:
            PathValidationError: 基础目录无效
        """
        if not self.base_dir.exists():
            raise PathValidationError(f"基础目录不存在: {self.base_dir}", path=str(self.base_dir))
        if not self.base_dir.is_dir():
            raise PathValidationError(f"基础路径不是目录: {self.base_dir}", path=str(self.base_dir))
    
    def _resolve_path(self, relative_path: str) -> Path:
        """
        智能解析路径为绝对路径
        
        支持多种路径格式：
        1. 绝对路径：如 "/absolute/path/to/file" - 直接使用  
        2. 相对于base_dir的路径：如 "src/main.py" - 相对于项目根目录
        3. 相对于工作目录的路径：如 ".cloned-repo/project/src" - 相对于当前工作目录
        4. 当前目录标识：如 "." 或 "" - 指向项目根目录
        
        Args:
            relative_path: 输入路径
            
        Returns:
            解析后的绝对路径
        """
        if relative_path == "." or relative_path == "":
            return self.base_dir
        
        path_obj = Path(relative_path)
        
        # 如果已经是绝对路径，直接使用
        if path_obj.is_absolute():
            return path_obj.resolve()
        
        # 对于相对路径，我们需要判断它是相对于哪个目录的
        
        # 策略1: 尝试作为相对于base_dir的路径
        base_relative_path = (self.base_dir / relative_path).resolve()
        
        # 策略2: 尝试作为相对于当前工作目录的路径
        cwd_relative_path = (Path(os.getcwd()) / relative_path).resolve()
        
        # 策略3: 修复：对于文件名，尝试在项目根目录下递归搜索
        if not base_relative_path.exists() and not cwd_relative_path.exists():
            # 如果路径不包含目录分隔符，可能是文件名
            if '/' not in relative_path and '\\' not in relative_path:
                # 在项目根目录下递归搜索该文件名
                search_pattern = f"**/{relative_path}"
                try:
                    search_paths = list(self.base_dir.glob(search_pattern))
                    if search_paths:
                        # 返回第一个找到的文件
                        return search_paths[0].resolve()
                except Exception:
                    pass
        
        # 优先选择存在的路径
        if base_relative_path.exists():
            return base_relative_path
        elif cwd_relative_path.exists():
            return cwd_relative_path
        else:
            # 如果都不存在，默认使用base_dir相对路径
            # 这样后续的存在性检查会给出明确的错误信息
            return base_relative_path
    
    def _validate_path_security(self, path: Path) -> None:
        """
        验证路径的安全性，确保不会访问危险区域
        
        Args:
            path: 要验证的路径
            
        Raises:
            SecurityError: 路径不在允许的范围内
        """
        # 解析路径以处理符号链接
        resolved_path = path.resolve()
        resolved_base = self.base_dir.resolve()
        
        # 允许访问base_dir及其子目录
        try:
            resolved_path.relative_to(resolved_base)
            return  # 路径在base_dir内，允许访问
        except ValueError:
            pass  # 路径不在base_dir内，继续检查其他条件
        
        # 对于项目外的路径，进行更宽松的安全检查
        try:
            # 获取用户主目录和工作目录作为安全边界
            cwd = Path(os.getcwd()).resolve()
            
            # 允许访问当前工作目录及其子目录
            try:
                resolved_path.relative_to(cwd)
                # 检查路径不包含危险的目录遍历
                path_parts = resolved_path.parts
                if '..' not in path_parts:
                    return
            except ValueError:
                pass
            
            # 允许访问临时目录（修复临时目录访问问题）
            import tempfile
            temp_dir = Path(tempfile.gettempdir()).resolve()
            try:
                resolved_path.relative_to(temp_dir)
                return  # 临时目录内的路径，允许访问
            except ValueError:
                pass
            
            # 允许访问某些特定的安全目录（如.cloned-repo）
            safe_prefixes = ['.cloned-repo', 'tmp', 'temp']
            for safe_prefix in safe_prefixes:
                safe_path = cwd / safe_prefix
                try:
                    resolved_path.relative_to(safe_path.resolve())
                    return
                except ValueError:
                    continue
                    
        except Exception:
            pass
        
        # 如果都不满足，抛出安全错误
        relative_base = self._get_relative_path(path)
        raise SecurityError(
            f"路径不在允许的目录范围内: {relative_base}",
            path=str(path),
            tool_name=self.__class__.__name__
        )
    
    def _validate_path_exists(self, path: Path, path_type: str = "路径") -> None:
        """
        验证路径是否存在
        
        Args:
            path: 要验证的路径
            path_type: 路径类型描述（用于错误信息）
            
        Raises:
            PathValidationError: 路径不存在
        """
        if not path.exists():
            # 如果是基础目录本身不存在，这是严重错误
            if path == self.base_dir:
                raise PathValidationError(
                    f"基础目录不存在，工具初始化可能有问题: {self.base_dir}",
                    path=str(self.base_dir),
                    tool_name=self.__class__.__name__
                )
            else:
                relative_path = path.relative_to(self.base_dir) if path.is_relative_to(self.base_dir) else path
                raise PathValidationError(
                    f"{path_type}不存在: {relative_path}",
                    path=str(relative_path),
                    tool_name=self.__class__.__name__
                )
    
    def _get_relative_path(self, full_path: Path) -> str:
        """
        获取相对于基础目录的相对路径
        
        Args:
            full_path: 完整路径
            
        Returns:
            相对路径字符串
        """
        try:
            return str(full_path.relative_to(self.base_dir))
        except ValueError:
            # 如果路径不在基础目录内，返回绝对路径
            return str(full_path)
    
    def _validate_file_path(self, file_path: str) -> Path:
        """
        验证文件路径的完整性和安全性
        
        Args:
            file_path: 文件路径
            
        Returns:
            验证后的完整路径
            
        Raises:
            PathValidationError: 路径验证失败
            SecurityError: 路径安全性验证失败
        """
        try:
            full_path = self._resolve_path(file_path)
            self._validate_path_security(full_path)
            self._validate_path_exists(full_path, "文件")
            
            if not full_path.is_file():
                relative_path = self._get_relative_path(full_path)
                raise PathValidationError(
                    f"路径不是文件: {relative_path}",
                    path=relative_path,
                    tool_name=self.__class__.__name__
                )
            
            return full_path
        except (PathValidationError, SecurityError):
            raise
        except Exception as e:
            raise PathValidationError(
                f"文件路径验证失败: {str(e)}",
                path=file_path,
                tool_name=self.__class__.__name__
            ) from e
    
    def _validate_directory_path(self, dir_path: str) -> Path:
        """
        验证目录路径的完整性和安全性
        
        Args:
            dir_path: 目录路径
            
        Returns:
            验证后的完整路径
            
        Raises:
            PathValidationError: 路径验证失败
            SecurityError: 路径安全性验证失败
        """
        try:
            full_path = self._resolve_path(dir_path)
            self._validate_path_security(full_path)
            self._validate_path_exists(full_path, "目录")
            
            if not full_path.is_dir():
                relative_path = self._get_relative_path(full_path)
                raise PathValidationError(
                    f"路径不是目录: {relative_path}",
                    path=relative_path,
                    tool_name=self.__class__.__name__
                )
            
            return full_path
        except (PathValidationError, SecurityError):
            raise
        except Exception as e:
            raise PathValidationError(
                f"目录路径验证失败: {str(e)}",
                path=dir_path,
                tool_name=self.__class__.__name__
            ) from e
        
    def _to_abs(self, file_path: str) -> str:
        """
        将相对路径转换为绝对路径（保持向后兼容）
        
        Args:
            file_path: 文件路径
            
        Returns:
            绝对路径字符串
        """
        if file_path == '.':
            return str(self.base_dir)
        
        if not os.path.isabs(file_path):
            if file_path.startswith('.cloned-repo'):
                # 相对于当前目录， 即项目根目录
                file_path = os.path.abspath(file_path)
            else:    
                file_path = str(self.base_dir / file_path)
        return file_path