# MCP 服务器

MCP（Model Context Protocol）服务器是一个基于 HTTP 的服务，用于为大型语言模型（如 Claude、GPT 等）提供额外的工具和资源。本文档分为两部分：运维人员部署指南和用户使用指南。

## 第一部分：运维人员部署指南

### 系统要求

- Python 3.8 或更高版本
- 足够的内存和磁盘空间（取决于您的使用场景）
- 网络连接（如果需要访问外部资源）

### 安装方式

#### 方式一：从源码安装

1. 克隆代码库：

```bash
git clone https://github.com/your-organization/knowledge-engineering.git
cd knowledge-engineering
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 启动服务器：

```bash
python -m mcp_server
```

#### 方式二：使用 Docker

1. 构建 Docker 镜像：

```bash
docker build -t mcp-server -f dockers/mcp-server/Dockerfile .
```

2. 运行 Docker 容器：

```bash
docker run -p 8000:8000 mcp-server
```

### 配置

服务器配置可以通过环境变量或配置文件进行设置：

#### 环境变量

- `MCP_PORT`：服务器端口（默认：8000）
- `MCP_HOST`：服务器主机（默认：0.0.0.0）
- `MCP_LOG_LEVEL`：日志级别（默认：INFO）
- `MCP_RAG_ENDPOINT`：RAG 服务端点（如果使用 RAG）

#### 配置文件

创建 `config/mcp_config.json` 文件：

```json
{
  "port": 8000,
  "host": "0.0.0.0",
  "log_level": "INFO",
  "rag_endpoint": "http://localhost:8001"
}
```

### 监控和日志

日志文件位于 `logs/mcp_server.log`。您可以使用标准的日志监控工具（如 ELK Stack）来监控服务器状态。

### 安全性

- 确保服务器在安全的网络环境中运行
- 考虑使用 HTTPS 和身份验证
- 定期更新依赖项以修复安全漏洞

### 故障排除

常见问题及解决方案：

1. **服务器无法启动**：检查端口是否被占用，尝试更改端口
2. **内存使用过高**：调整配置以限制并发请求数
3. **RAG 查询失败**：检查 RAG 服务是否正常运行，网络连接是否正常

## 第二部分：用户使用指南

### 安装客户端

#### 方式一：从 PyPI 安装

```bash
pip install kengine-mcp-server
```

#### 方式二：从源码安装

```bash
git clone https://github.com/your-organization/knowledge-engineering.git
cd knowledge-engineering
pip install -e .
```

### 配置 IDE 集成

#### Claude 集成

1. 创建 `mcp_client_config.json` 文件：

```json
{
  "kengine_mcp_server": {
    "command": "python -m mcp_server",
    "args": [],
    "env": {}
  }
}
```

2. 在 Claude 中使用以下代码配置 MCP 客户端：

```python
from mcp_client import KengineMCPClient

# 创建 MCP 客户端
client = KengineMCPClient("kengine_mcp_server", "mcp_client_config.json")

# 启动 MCP 服务器
client.start_server()

# 获取可用工具列表
tools = client.list_tools()
print(f"可用工具: {tools}")

# 调用工具
result = client.call_tool("get_business_context", {
    "module_name": "example_module",
    "include_prd": True,
    "include_code": True
})
print(f"工具调用结果: {result}")

# 停止 MCP 服务器
client.stop_server()
```

完整示例请参考 `claude_mcp_example.py`。

#### Cursor IDE 集成

1. 安装 Cursor IDE 插件：

```bash
cursor plugin install kengine-mcp
```

2. 在 Cursor IDE 中配置 MCP 服务器：

```
Settings > Extensions > MCP > Server Path: /path/to/mcp_server
```

3. 使用快捷键 `Ctrl+Shift+M` 激活 MCP 工具面板

### 可用工具

#### 1. echo

测试连通性的简单工具，返回发送的消息以及服务器状态信息。

**参数**：
- `message`：要回显的消息内容
- `include_server_info`：是否包含服务器状态信息（默认：true）

**示例**：
```json
{
  "message": "Hello, MCP!",
  "include_server_info": true
}
```

#### 2. get_business_context

获取业务模块、代码方法、函数或类的完整上下文信息。

**参数**：
- `module_name`：业务模块名称
- `field_name`：字段名称（可作为 module_name 的替代）
- `method_name`：方法名称（可选）
- `include_prd`：是否包含 PRD 文档（默认：true）
- `include_code`：是否包含代码实现（默认：true）

**示例**：
```json
{
  "module_name": "user_service",
  "method_name": "get_user_by_id",
  "include_prd": true,
  "include_code": true
}
```

### 常见问题

1. **连接失败**：确保 MCP 服务器正在运行，并且端口配置正确
2. **工具调用失败**：检查参数是否正确，服务器日志中是否有错误信息
3. **性能问题**：考虑增加服务器资源或优化查询参数

### 高级用法

#### 自定义工具

您可以通过创建自定义处理程序来扩展 MCP 服务器的功能：

1. 在 `mcp_server/handlers/` 目录下创建新的处理程序文件
2. 实现处理函数并在 `mcp_server/handlers/__init__.py` 中注册
3. 重启服务器以使新工具生效

#### 批量处理

对于需要处理大量请求的场景，可以使用批处理模式：

```python
results = client.batch_call_tools([
    {"tool": "get_business_context", "params": {"module_name": "module1"}},
    {"tool": "get_business_context", "params": {"module_name": "module2"}}
])
```

### 更多资源

- [API 文档](https://your-organization.github.io/knowledge-engineering/api)
- [示例代码库](https://github.com/your-organization/knowledge-engineering/examples)
- [常见问题解答](https://your-organization.github.io/knowledge-engineering/faq)