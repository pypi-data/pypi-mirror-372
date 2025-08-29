import re
from typing import Optional


def source_to_git_repo_url(source_path: str, branch: str = "master") -> str:
    """
        source_path 格式为 .cloned_repo/group/repo/filepath.java 或 .cloned-repo/group/repo/filepath.java
        要返回的git repo url格式
        master分支：
        http://xingyun.jd.com/codingRoot/group/repo/blob/master/filepath.java
        非master分支：
        http://xingyun.jd.com/codingRoot/group/repo/blob/branch/filepath.java
        其中 http://xingyun.jd.com/codingRoot/ 是固定的url前缀
        group, repo 需要从 source_path 中拆解出来
    """
    # 参数验证
    if not isinstance(source_path, str):
        raise TypeError(f"source_path 参数必须是字符串类型，但收到了 {type(source_path).__name__} 类型")
    
    if not isinstance(branch, str):
        raise TypeError(f"branch 参数必须是字符串类型，但收到了 {type(branch).__name__} 类型")
    
    if not source_path or not source_path.strip():
        raise ValueError("source_path 参数不能为空或只包含空白字符")
    
    if not branch or not branch.strip():
        raise ValueError("branch 参数不能为空或只包含空白字符")
    
    # 清理路径
    source_path = source_path.strip()
    branch = branch.strip()
    
    # 使用正则表达式解析 source_path
    # 匹配格式：.cloned_repo/group/repo/filepath 或 .cloned-repo/group/repo/filepath
    pattern = r'^\.cloned[-_]repo/([^/]+)/([^/]+)/(.+)'
    match = re.match(pattern, source_path)
    
    if not match:
        raise ValueError(f"source_path 格式不正确: '{source_path}'，期望格式为: .cloned_repo/group/repo/filepath 或 .cloned-repo/group/repo/filepath")
    
    # 提取 group、repo 和 filepath
    group, repo, filepath = match.groups()
    
    # 构建 git repo URL
    base_url = "http://xingyun.jd.com/codingRoot"
    git_repo_url = f"{base_url}/{group}/{repo}/blob/{branch}/{filepath}"
    
    return git_repo_url



def convert_git_url_to_http(git_url: str, branch: str = "master") -> str:
    """
    将 Git URL 转换为可访问的 HTTP URL，支持指定分支
    
    转换规则：
    - 输入示例：git@coding.jd.com:jdl-public/knowledge-engineering.git
    - 输出示例：http://xingyun.jd.com/codingRoot/jdl-public/knowledge-engineering/blob/{branch}/
    
    Args:
        git_url (str): SSH 格式的 Git URL
        branch (str): 分支名称，默认为 "master"
        
    Returns:
        str: 转换后的 HTTP URL
        
    Raises:
        TypeError: 当参数类型不正确时抛出
        ValueError: 当参数格式不正确时抛出
    """
    # 参数类型检查
    if not isinstance(git_url, str):
        raise TypeError(f"git_url 参数必须是字符串类型，但收到了 {type(git_url).__name__} 类型")
    
    if not isinstance(branch, str):
        raise TypeError(f"branch 参数必须是字符串类型，但收到了 {type(branch).__name__} 类型")
    
    # 参数格式检查
    if not git_url or not git_url.strip():
        raise ValueError("git_url 参数不能为空或只包含空白字符")
    
    # 验证分支名称的有效性
    if not branch or not branch.strip():
        raise ValueError("branch 参数不能为空或只包含空白字符")
    
    # 检查分支名称是否包含特殊字符（简单验证）
    branch = branch.strip()
    if re.search(r'[<>:"|?*\\\s]', branch):
        raise ValueError(f"分支名称 '{branch}' 包含无效字符，不能包含以下字符: < > : \" | ? * \\ 或空格")
    
    # 匹配 SSH 格式的 Git URL: git@host:user/repo.git
    ssh_pattern = r'^git@([^:]+):([^/]+)/([^/]+)\.git$'
    match = re.match(ssh_pattern, git_url.strip())
    
    if not match:
        raise ValueError(f"Git URL 格式不正确: '{git_url}'，期望格式为: git@host:user/repo.git")
    
    host, user, repo = match.groups()
    
    # 特殊处理：将 coding.jd.com 转换为 xingyun.jd.com
    if host == 'coding.jd.com':
        http_host = 'xingyun.jd.com'
        # 构建 HTTP URL，使用指定的分支名称
        http_url = f"http://{http_host}/codingRoot/{user}/{repo}/blob/{branch}/"
    else:
        # 对于其他主机，使用通用转换规则
        http_url = f"http://{host}/{user}/{repo}/blob/{branch}/"
    
    return http_url


def validate_git_url(git_url: str) -> bool:
    """
    验证 Git URL 格式是否正确
    
    Args:
        git_url (str): 待验证的 Git URL
        
    Returns:
        bool: 如果格式正确返回 True，否则返回 False
    """
    if not git_url or not isinstance(git_url, str):
        return False
    
    ssh_pattern = r'^git@[^:]+:[^/]+/[^/]+\.git$'
    return bool(re.match(ssh_pattern, git_url.strip()))


def extract_repo_info(git_url: str) -> Optional[dict]:
    """
    从 Git URL 中提取仓库信息
    
    Args:
        git_url (str): Git URL
        
    Returns:
        Optional[dict]: 包含 host, user, repo 信息的字典，失败时返回 None
    """
    if not validate_git_url(git_url):
        raise ValueError(f"url {git_url} is invalid.")
    
    ssh_pattern = r'^git@([^:]+):([^/]+)/([^/]+)\.git$'
    match = re.match(ssh_pattern, git_url.strip())
    
    if match:
        host, user, repo = match.groups()
        return {
            'host': host,
            'user': user,
            'repo': repo
        }
    
    raise ValueError(f"url format error {git_url}")
