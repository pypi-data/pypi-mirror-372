# 知识工程项目 (Knowledge Engineering)

一个基于 LangChain 的智能代码库分析和文档生成工具。本项目提供了完整的代码库克隆、分析、分类、知识库构建和文档生成功能，能够智能识别项目类型（应用程序、框架、库、开发工具等），并自动生成结构化的技术文档。

📖 **开发指南**: 详细的开发说明请参考 [开发文档 (AppDev.md)](docs/AppDev.md)

## 🎯 项目目标

### 第一阶段目标

1. 构建基于*代码库*的知识库，知识库可供研发、产品、测试、业务阅读。 
2. 基于此知识库构建问答，能快速了解业务知识、技术知识，减少沟通成本。 

对知识库的要求：
- 能如实反馈业务流程，能如实反馈业务规则
- 能如实反馈技术架构，技术细节

### 基础知识

- 大模型接入手册：https://joyspace.jd.com/page/q9AY6VwZTxholVXl0E7D
- 大模型网关接口文档：https://joyspace.jd.com/pages/hQTBswr7k3AusgP2k2XZ
- 账号计费情况：https://easybi.jd.com/bi/#/insight?code=EF838CD9A9A58A2BCE840ED68EC79FE773F4FE91E65E8FDEC180F19F4AA03D8B

## 🚀 项目特色

- **智能代码库分析**：基于 LangChain 的智能项目分析和分类系统
- **配置驱动的分类系统**：支持通过 JSON 配置文件动态扩展项目分类类别
- **多维度项目识别**：支持 Android、应用程序、框架、库、开发工具等9大类别的精准分类
- **完整的工作流程**：从代码库克隆到分析报告生成的一站式解决方案
- **强大的工具集合**：目录分析、文件分类、文本读取、项目信息提取等实用工具
- **提示词模板系统**：基于专业的分类提示词模板，确保分析结果的准确性
- **多策略文档生成**：支持 Prompt、Agent、Hybrid 三种生成策略，适应不同复杂度项目

## 📋 功能特性

### 核心功能
- ✅ **代码库克隆**：支持多种 Git 协议的代码库自动克隆
- ✅ **智能分类**：基于 LLM 的项目类型自动识别和分类，支持配置化扩展
- ✅ **项目分析**：深度分析项目结构、技术栈和编程语言分布
- ✅ **文档目录生成**：基于项目分析结果自动生成文档目录结构
- ✅ **RAG检索服务**：完整的检索增强生成功能，支持知识库构建和智能问答
- ✅ **文件处理**：智能文件分类（源码、文档、二进制文件）
- ✅ **多编码支持**：自动检测和处理多种文本编码格式
- ✅ **目录结构生成**：自动生成 Markdown 格式的项目结构图
- ✅ **配置文件解析**：自动识别和解析项目配置文件
- ✅ **批量处理**：支持批量文件读取和处理
- ✅ **多模型支持**：支持 OpenAI GPT-4、Claude、ChatRhino 等多种 AI 模型

### 技术栈
- **核心框架**: LangChain 0.3.26
- **AI 模型**: OpenAI GPT-4 / AWS Claude / ChatRhino-81B-Pro
- **向量存储**: FAISS (Facebook AI Similarity Search)
- **文本嵌入**: OpenAI Embeddings
- **开发语言**: Python 3.12+
- **代码解析**: Tree-sitter (支持20+编程语言)
- **文本处理**: chardet (编码检测)、spaCy (中文NLP)
- **版本控制**: Git (subprocess)
- **Web框架**: Flask + Next.js
- **测试框架**: pytest + unittest
- **依赖管理**: requirements.txt

## 🛠️ 安装指南

### 环境要求
- Python 3.12.7+
- Node.js 16+ (用于Web界面)
- pip 包管理器
- Git (用于代码库克隆)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd knowledge-engineering
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
创建 `.env` 文件并配置以下变量：
```env
# OpenAI 配置 (JDT路由)
OPENAI_BASE_URL=http://gpt-proxy.jd.com/v1
OPENAI_API_KEY=your_api_key

# JDT路由配置
JDT_ROUTER_BASE=http://gpt-proxy.jd.com/v1
JDT_API_KEY=your_jdt_api_key

# JDL路由配置
JDL_ROUTER_BASE=http://airouter.jdl.com
JDL_KIMI_KEY=your_kimi_key
JDL_QWEN_KEY=your_qwen_key

# 智谱AI配置
ZHIPUAI_BASE_URL=http://gpt-proxy.jd.com/v1
ZHIPUAI_API_KEY=your_zhipuai_key

# 测试数据库地址
DATABASE_URL=mysql+pymysql://tarzan_ddl:jJBskPDWlgymGr85svXwUUBp1bZl5S2s@mysql-cn-north-1-be8ff9b3a5d54609.rds.jdcloud.com:3358/db_kb

# OSS对象存储配置 (京东云OSS)
OSS_ACCESS_KEY=JDC_9E27A8FA31BE3A3AE1C5D5A6C9FD
OSS_SECRET_KEY=A44BB95717EE02092F391A22B5B07AAB
OSS_INNER_ENDPOINT=s3-internal.cn-north-1.jdcloud-oss.com
OSS_OUT_ENDPOINT=s3.cn-north-1.jdcloud-oss.com
OSS_BUCKET_NAME=serviceplus-basic
OSS_REGION=cn-north-1
```

5. **安装Web界面依赖**
```bash
cd web && npm install
```

6. **设置CLI工具权限**
```bash
chmod +x bin/kengine_cli
```

## 🎯 使用指南

### kengine_cli 命令行工具

项目的核心工具是 [`kengine_cli`](bin/kengine_cli)，这是一个增强的命令行工具，提供完整的代码库分析和文档生成功能。

#### 工具架构

- **[`bin/kengine_cli`](bin/kengine_cli)**: Bash脚本入口，负责环境检查和Python模块调用
  - 提供彩色日志输出功能
  - 检查Python环境和kengine模块可用性
  - 将所有参数传递给Python CLI模块
  - 提供错误处理和退出码传递

- **[`kengine/cli/cli.py`](kengine/cli/cli.py)**: Python CLI控制器，处理业务逻辑
  - 参数解析和验证
  - 调用核心知识服务
  - 结果展示和错误处理

#### 基本使用

```bash
# 查看帮助信息
./bin/kengine_cli --help

# 基本用法 - 分析项目并生成完整文档
./bin/kengine_cli --repo_group "my-group" --repo_name "my-project"
```

#### 核心参数详解

| 参数 | 必需 | 默认值 | 说明 | 示例 |
|------|------|--------|------|------|
| `--repo_group` | ✅ | - | 代码仓库组名，用于组织项目 | `"wms6.0m"`, `"eclp-pf"` |
| `--repo_name` | ✅ | - | 代码仓库名称，项目的具体名称 | `"Inbound"`, `"open-rts"` |
| `--model_name` | ❌ | `gpt-4.1` | LLM模型名称，影响分析质量和成本 | `"claude-3-5-sonnet"` |
| `--prompt_version` | ❌ | - | 提示词版本，用于A/B测试 | `"2.0"`, `"v1.5"` |
| `--branch` | ❌ | `master` | Git分支，指定要分析的代码分支 | `"develop"`, `"main"` |
| `--force_project_type` | ❌ | - | 强制指定项目类型，跳过自动分类 | `"Android"`, `"Libraries"` |
| `--execute_step` | ❌ | `full` | 执行步骤，控制分析流程 | `"classification"`, `"overview"`, `"catalogue"` `"document"`  |
| `--specify_document_path` | ❌ | `""` | 指定文档路径，用于生成单个文档 | `"docs/api"` |

#### 支持的AI模型

根据 [`config/application_config.json`](config/application_config.json) 配置，系统支持以下模型：

| 模型名称 | 提供商 | 最大Token | 温度 | 适用场景 |
|----------|--------|-----------|------|----------|
| **gpt-4** / **gpt-4.1** | OpenAI | 32,768 | 0.1 | 通用分析，平衡质量和成本 |
| **claude-3-5-sonnet** | AWS | 8,192 | 0.1 | 代码理解，逻辑分析 |
| **claude-sonnet-4** | AWS | 65,536 | 0.1 | 复杂项目，长文档生成 |
| **Chatrhino-81B-Pro** | ChatRhino | 22,528 | 0.1 | 中文优化，本土化场景 |

#### 支持的执行步骤

| 步骤 | 说明 | 输出内容 | 适用场景 |
|------|------|----------|----------|
| `classification` | 仅项目分类 | 项目类型、置信度、分析摘要 | 快速了解项目性质 |
| `overview` | 仅生成概览 | 项目概览文档 | 项目初步了解 |
| `catalogue` | 仅生成目录 | 文档目录结构 | 文档规划 |
| `document` | 仅生成文档 | 详细技术文档 | 深度文档化 |
| `full` | 完整流程 | 分类+概览+目录+文档+RAG知识库 | 完整项目分析 |

#### 详细使用示例

##### 1. 基础项目分析
```bash
# 分析一个基础项目，使用默认设置
./bin/kengine_cli \
  --repo_group "my-team" \
  --repo_name "web-app"
```


##### 2. 分步骤执行
```bash
# 第一步：仅进行项目分类
./bin/kengine_cli \
  --repo_group "my-group" \
  --repo_name "unknown-project" \
  --execute_step "classification"

# 第二步：基于分类结果生成概览
./bin/kengine_cli \
  --repo_group "my-group" \
  --repo_name "unknown-project" \
  --execute_step "overview" \
  --force_project_type "Applications"

# 第三步：生成完整文档
./bin/kengine_cli \
  --repo_group "my-group" \
  --repo_name "unknown-project" \
  --execute_step "full" \
  --force_project_type "Applications"

# 调试单个文档
./bin/kengine_cli \
  --repo_group wms-ng \
  --repo_name wms-pick \
  --prompt_version 0.2 \
  --execute_step document \
  --specify_document_path project-overview/core-business-flow
```

```

##### 3. 增量文档更新
```bash
# 仅更新特定文档部分
./bin/kengine_cli \
  --repo_group "my-group" \
  --repo_name "my-project" \
  --execute_step "document" \
  --specify_document_path "docs/api-reference.md"
```

#### 输出结果解读

成功执行后，工具会显示详细的分析结果：

```bash
🚀 开始生成项目概览...
📁 仓库: my-group/my-project
🤖 使用模型: claude-3-5-sonnet
🌿 Git分支: develop
🎯 强制项目类型: Applications

✅ 项目概览生成成功!
📁 输出路径: /path/to/output
🏷️  项目类型: Applications
⚙️  使用策略: hybrid
🎯 分类置信度: 0.95
🔍 RAG知识库构建完成
📊 概览生成完成
⏱️  生成耗时: 45.32秒
```

#### 错误处理

工具提供了完善的错误处理机制：

1. **环境检查错误**
```bash
[ERROR] Python命令不可用，请确保已安装Python
[ERROR] 无法导入kengine.cli.cli模块
[INFO] 请确保已正确安装项目依赖: pip install -r requirements.txt
```

2. **参数验证错误**
```bash
❌ execute_step参数必须为['classification', 'overview', 'catalogue', 'document', 'full']中的一个
❌ repo_group和repo_name参数不能为空
```

3. **执行过程错误**
```bash
❌ 项目概览生成失败
错误信息: 模型调用超时
失败阶段: classification
⚠️  警告信息:
  - 项目文件过多，建议使用.gitignore过滤
```

### 传统Python入口使用

除了推荐的CLI工具，您也可以直接使用Python入口：

```bash
# 使用main.py（传统模式）
python main.py --repo_group=eclp-pf --repo_name=open-rts --model_name=claude-3-5-sonnet

# 使用Python模块方式
python -m kengine.cli.cli --repo_group "my-group" --repo_name "my-project"
```

### 单独使用各个功能模块

#### 代码库克隆
```python
from kengine.tasks.clone import clone_repository

# 克隆代码库到本地
result = clone_repository(
    repo_url="https://github.com/user/repo.git",
    target_dir="./cloned-repo",
    force=True  # 如果目录存在则强制删除重新克隆
)
print(f"克隆结果: {result}")
```

#### 项目分类
```python
from kengine.tasks.classification import classify_repository

# 分析并分类本地项目
result = classify_repository("./project-directory")
print(f"项目分类: {result['classification']}")
print(f"分析摘要: {result['analysis_summary']}")
```

#### 项目信息提取
```python
from kengine.utils.project_utils import get_project_info_text

# 获取项目详细信息
project_info = get_project_info_text("./project-directory")
print(project_info)
```

#### 文档生成
```python
from kengine.core import KnowledgeService, KnowledgeGenerationRequest
from kengine.core.types import ExecuteStep

# 创建知识服务
service = KnowledgeService()

# 创建生成请求
request = KnowledgeGenerationRequest(
    repo_group="my-group",
    repo_name="my-project",
    model_name="gpt-4.1",
    execute_step=ExecuteStep.FULL
)

# 生成知识文档
result = service.generate_knowledge(request)
if result.success:
    print(f"文档生成成功: {result.output_path}")
else:
    print(f"生成失败: {result.error}")
```

#### RAG检索服务
```python
from kengine.rag import build_knowledge_base_from_directory, RAGConfig

# 创建优化的RAG配置
rag_config = RAGConfig(
    chunk_size=800,
    chunk_overlap=150,
    embedding_model="text-embedding-3-small",
    retrieval_k=3
)

# 构建知识库
rag_service = build_knowledge_base_from_directory(
    "./project-directory",
    "./.kb/project_kb",
    config=rag_config
)

# 执行查询
result = rag_service.query("这个项目的主要功能是什么？")
print(f"答案: {result['answer']}")
print(f"相关文档数量: {len(result['source_documents'])}")
```

## 🎨 项目分类系统

### 支持的分类类别

系统支持 9 种项目分类，能够智能识别不同类型的代码库：

| 分类 | 描述 | 生成策略 | 关键词 |
|------|------|----------|--------|
| **Android** | Android 移动应用项目 | prompt | android, mobile, java, kotlin, gradle |
| **Applications** | 完整的可运行应用程序 | hybrid | web app, mobile app, desktop app, service |
| **Frameworks** | 开发框架和平台 | prompt | framework, platform, architecture, foundation |
| **Libraries** | 可重用的代码库 | agent | library, package, component, utility, module |
| **DevelopmentTools** | 开发辅助工具 | prompt | build tool, compiler, testing, linter |
| **CLITools** | 命令行工具 | prompt | cli, command line, script, terminal, console |
| **DevOpsConfiguration** | 运维配置项目 | prompt | devops, cicd, deployment, configuration |
| **Documentation** | 文档和教育资源 | prompt | documentation, tutorial, guide, knowledge |
| **MobileApps** | 移动应用项目 | agent | mobile, ios, react native, flutter, cordova |

### 文档生成策略

系统采用策略模式支持三种文档生成方式：

1. **Prompt策略** - 基于提示词的快速生成（适用于简单项目）
2. **Agent策略** - 基于智能代理的高级生成（适用于复杂项目）
3. **Hybrid策略** - 混合策略，概览和目录使用Prompt，文档使用Agent

## 🏗️ 核心架构

### 系统组成

项目采用模块化设计，主要包含以下核心模块：

```
kengine/
├── core/                    # 核心服务层
│   ├── knowledge_service.py # 知识生成服务
│   ├── document_service.py  # 文档生成服务
│   ├── strategy_factory.py  # 策略工厂
│   └── types.py            # 核心类型定义
├── cli/                    # 命令行接口
│   └── cli.py             # CLI控制器
├── tasks/                  # 任务处理层
│   ├── classification.py  # 项目分类
│   ├── clone.py           # 代码库克隆
│   ├── rag.py             # RAG检索服务
│   └── llm.py             # LLM调用服务
├── utils/                  # 工具函数库
│   ├── project_utils.py   # 项目分析工具
│   ├── directory_utils.py # 目录处理工具
│   ├── text_reader.py     # 文本读取工具
│   └── git_utils.py       # Git操作工具
├── config/                 # 配置管理
│   ├── application_config.py
│   └── logging_config.py
└── code.skeleton/          # 代码骨架提取
    ├── extractor.py
    └── languages/         # 多语言支持
```

### 入口文件架构

- **[`bin/kengine_cli`](bin/kengine_cli)**: Bash脚本入口，提供环境检查和错误处理
- **[`kengine/cli/cli.py`](kengine/cli/cli.py)**: Python CLI控制器，处理参数解析和业务逻辑
- **[`main.py`](main.py)**: 传统Python入口，保持向后兼容性

## 🌟 应用场景

### 开发团队管理
- **项目分类管理**: 自动识别和分类团队的各种代码库
- **技术栈统计**: 了解团队使用的编程语言和技术分布
- **项目结构分析**: 快速了解新项目的组织结构

### 开源项目研究
- **批量项目分析**: 对大量开源项目进行自动化分类和分析
- **技术趋势研究**: 统计不同类型项目的技术栈使用情况
- **项目质量评估**: 基于项目结构和文档完整性进行初步评估

### 代码库迁移和整理
- **遗留系统分析**: 快速了解老旧项目的结构和技术栈
- **迁移规划**: 为项目迁移提供详细的结构分析报告
- **文档生成**: 自动生成项目结构文档

### 教育和学习
- **项目类型学习**: 通过分析不同类型的项目了解软件架构模式
- **技术栈研究**: 学习不同项目使用的技术组合
- **最佳实践**: 通过分析优秀项目学习项目组织方式

### 智能文档和知识管理
- **自动文档生成**: 基于项目结构自动生成文档目录和框架
- **知识库构建**: 将项目代码和文档转换为可检索的知识库
- **智能问答**: 基于项目内容提供准确的技术问答服务
- **代码理解**: 通过RAG技术快速理解大型项目的架构和实现细节

## 🧪 测试

项目包含完整的测试套件，覆盖所有核心功能。我们提供了统一的测试运行器 [`run_tests.py`](run_tests.py)，支持重组后的测试目录结构，能够方便地运行所有测试或指定模块的测试。

### 使用 run_tests.py 测试运行器

[`run_tests.py`](run_tests.py) 是项目的通用测试运行脚本，支持18个测试模块，提供多种运行选项和命令行参数。

#### 基本用法

```bash
# 运行所有测试（推荐方式）
python run_tests.py

# 运行指定测试模块
python run_tests.py --module core
python run_tests.py --module utils
python run_tests.py --module cli

# 列出所有可用的测试模块
python run_tests.py --list-modules

# 查看帮助信息
python run_tests.py --help
```

#### 支持的命令行参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--module` | `-m` | 指定要运行的测试模块 | `--module core` |
| `--list-modules` | `-l` | 列出所有可用的测试模块 | `--list-modules` |
| `--pytest-only` | - | 只使用 pytest 运行测试 | `--pytest-only` |
| `--unittest-only` | - | 只使用 unittest 运行测试 | `--unittest-only` |
| `--quiet` | `-q` | 静默模式，减少输出 | `--quiet` |

#### 支持的测试模块

脚本支持以下18个测试模块：

| 模块名称 | 路径 | 说明 |
|----------|------|------|
| `agent` | `tests/agent` | 智能代理相关测试 |
| `chat` | `tests/chat` | 聊天服务测试 |
| `cli` | `tests/cli` | 命令行接口测试 |
| `code_analysis` | `tests/code_analysis` | 代码分析测试 |
| `code.skeleton` | `tests/code.skeleton` | 代码骨架提取测试 |
| `config` | `tests/config` | 配置管理测试 |
| `core` | `tests/core` | 核心服务测试 |
| `demo` | `tests/demo` | 演示功能测试 |
| `e2e` | `tests/e2e` | 端到端测试 |
| `integration` | `tests/integration` | 集成测试 |
| `langchain_tools` | `tests/langchain_tools` | LangChain工具测试 |
| `llm` | `tests/llm` | 大语言模型测试 |
| `misc` | `tests/misc` | 杂项功能测试 |
| `optimization` | `tests/optimization` | 性能优化测试 |
| `parsers` | `tests/parsers` | 解析器测试 |
| `prompts` | `tests/prompts` | 提示词测试 |
| `rag` | `tests/rag` | RAG检索测试 |
| `refactoring` | `tests/refactoring` | 重构相关测试 |
| `strategies` | `tests/strategies` | 策略模式测试 |
| `summerize` | `tests/summerize` | 摘要生成测试 |
| `tasks` | `tests/tasks` | 任务处理测试 |
| `tools` | `tests/tools` | 工具函数测试 |
| `utils` | `tests/utils` | 工具类测试 |

#### 使用示例

```bash
# 1. 运行所有测试（默认先尝试pytest，再尝试unittest）
python run_tests.py

# 2. 运行核心模块测试
python run_tests.py --module core

# 3. 运行CLI相关测试
python run_tests.py --module cli

# 4. 只使用pytest运行所有测试
python run_tests.py --pytest-only

# 5. 只使用unittest运行特定模块
python run_tests.py --module utils --unittest-only

# 6. 静默模式运行测试
python run_tests.py --module core --quiet

# 7. 查看所有可用模块及其测试文件统计
python run_tests.py --list-modules
```

#### 测试运行器特性

- **智能测试发现**: 自动验证测试目录结构完整性
- **双重测试支持**: 支持 pytest 和 unittest 两种测试框架
- **详细统计信息**: 显示测试文件数量和模块分布
- **错误处理**: 完善的错误提示和异常处理
- **彩色输出**: 提供清晰的测试结果展示
- **测试覆盖**: 显示每个模块的测试文件覆盖情况

### 传统测试方法

除了推荐的 `run_tests.py` 运行器，您也可以直接使用传统的测试方法：

```bash
# 使用pytest直接运行
python -m pytest tests/test_classification.py -v
python -m pytest tests/test_cli_comprehensive.py -v
python -m pytest tests/test_knowledge_service_comprehensive.py -v

# 运行测试并显示覆盖率
python -m pytest tests/ --cov=kengine --cov-report=html

# 测试CLI工具
python -m pytest tests/test_bash_script.py -v
```

### 主要测试模块

- **CLI测试**: [`tests/test_cli_comprehensive.py`](tests/test_cli_comprehensive.py)
- **Bash脚本测试**: [`tests/test_bash_script.py`](tests/test_bash_script.py)
- **知识服务测试**: [`tests/test_knowledge_service_comprehensive.py`](tests/test_knowledge_service_comprehensive.py)
- **分类系统测试**: [`tests/test_classification.py`](tests/test_classification.py)
- **文档生成测试**: [`tests/test_document_generation.py`](tests/test_document_generation.py)

### 测试CLI工具功能

```bash
# 测试基本功能
./bin/kengine_cli --repo_group "test" --repo_name "sample" --execute_step "classification"

# 测试错误处理
./bin/kengine_cli --repo_group "" --repo_name "test"  # 应该报错

# 测试参数验证
./bin/kengine_cli --repo_group "test" --repo_name "sample" --execute_step "invalid"  # 应该报错
```

## 🌐 Web 文档查看器

项目提供了基于 Next.js 的 Web 界面，用于查看生成的文档：

### 功能特性
- **三栏布局**: 导航面板、内容区域、目录面板
- **Markdown 渲染**: 完整支持 Markdown 语法高亮
- **Mermaid 图表**: 支持流程图和架构图渲染
- **响应式设计**: 适配不同屏幕尺寸
- **实时导航**: 目录实时跟踪当前阅读位置
- **智能对话**: 集成 AI 助手，支持基于项目内容的智能问答

### 启动 Web 服务
```bash
# 安装 Web 依赖
cd web && npm install

# 启动开发服务器
npm run dev

# 或使用便捷脚本
./start-web.sh

# 构建生产版本
npm run build && npm start
```

### 启动 Chat 对话服务
```bash
# 启动 Chat 后端服务（默认端口 8080）
python chat_server.py

# 指定端口和主机
python chat_server.py --port 9000 --host 127.0.0.1

# 启用调试模式
python chat_server.py --debug --log-level DEBUG
```

### Chat 服务功能
- **流式对话**: 支持实时的对话响应
- **上下文记忆**: 维护多轮对话历史
- **思考模式**: 可选的 AI 思考过程展示
- **RAG 集成**: 基于项目代码库的知识检索增强生成
- **多模型支持**: 支持配置文件中定义的多种 AI 模型

使用流程：
1. 使用 `kengine_cli` 分析项目并生成文档
2. 启动 Chat 服务：`python chat_server.py`
3. 启动 Web 服务：`cd web && npm run dev`
4. 在文档页面点击右下角悬浮聊天按钮开始对话

## 🔧 配置说明

### 应用配置

主要配置文件：[`config/application_config.json`](config/application_config.json)

```json
{
  "classifications": {
    "Applications": {
      "name": "Applications",
      "description": "Complete, runnable software applications",
      "generation_strategy": "hybrid"
    }
  },
  "strategy_configs": {
    "prompt": {
      "max_retries": 3,
      "timeout": 300,
      "temperature": 0.7
    },
    "agent": {
      "overview_max_iterations": 25,
      "max_retries": 3,
      "timeout": 600
    }
  },
  "model_configs": {
    "gpt-4": {
      "provider": "openai",
      "model": "gpt-4.1",
      "temperature": 0.1,
      "max_tokens": 32768
    }
  }
}
```

### 环境变量配置

创建 `.env` 文件配置必要的环境变量：

```env
# 必需配置
OPENAI_API_KEY=your_openai_api_key

# 可选配置
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
ANTHROPIC_API_KEY=your_anthropic_api_key
CHATRHINO_API_KEY=your_chatrhino_api_key
```

## 🌟 技术特点

- **智能分类** - 基于 LLM 的多维度项目自动分类
- **策略模式** - 灵活的文档生成策略，支持不同复杂度项目
- **RAG 技术** - 检索增强生成，构建智能知识库
- **智能对话** - 基于项目内容的 AI 助手，支持流式对话和上下文记忆
- **多模型支持** - 支持 OpenAI、AWS Claude、ChatRhino 等多种 AI 模型
- **现代化界面** - 基于 Next.js 的响应式文档查看器
- **完整测试** - 全面的测试覆盖和持续集成
- **多语言解析** - 基于 Tree-sitter 的20+编程语言支持
- **配置驱动** - 灵活的JSON配置系统，支持动态扩展

## 📊 性能优化

### 生成策略选择

系统会根据项目类型自动选择最优的生成策略：

- **简单项目** (CLITools, Documentation): 使用 Prompt 策略，快速生成
- **复杂项目** (Libraries, MobileApps): 使用 Agent 策略，深度分析
- **中等项目** (Applications): 使用 Hybrid 策略，平衡效率和质量

### 缓存机制

- **模型响应缓存**: 避免重复的LLM调用
- **文件分析缓存**: 缓存项目结构分析结果
- **RAG向量缓存**: 复用已构建的向量索引

### 并发处理

- **最大并发数**: 配置文件中可设置 `max_concurrent_generations`
- **超时控制**: 不同策略有独立的超时配置
- **重试机制**: 智能重试失败的LLM调用

## 🚨 故障排除

### 常见问题和解决方案

#### 1. CLI工具无法执行
```bash
# 问题：Permission denied
# 解决：设置执行权限
chmod +x bin/kengine_cli

# 问题：Python模块导入失败
# 解决：检查依赖安装
pip install -r requirements.txt
```

#### 2. 模型调用失败
```bash
# 问题：API密钥错误
# 解决：检查.env文件配置
cat .env | grep API_KEY

# 问题：模型不存在
# 解决：检查config/application_config.json中的模型配置
```

#### 3. 项目分析失败
```bash
# 问题：项目路径不存在
# 解决：确保项目已正确克隆到本地

# 问题：文件编码问题
# 解决：系统会自动检测编码，如仍有问题请检查项目文件
```

#### 4. Web界面无法访问
```bash
# 问题：端口被占用
# 解决：更换端口或停止占用进程
lsof -i :3000
kill -9 <PID>

# 问题：依赖安装失败
# 解决：清理缓存重新安装
cd web && rm -rf node_modules package-lock.json && npm install
```

### 调试模式

启用详细日志输出：

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 运行CLI工具
./bin/kengine_cli --repo_group "test" --repo_name "debug" --execute_step "classification"
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！请参考 [开发文档 (AppDev.md)](docs/AppDev.md) 了解详细的开发指南和贡献流程。

### 快速贡献
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Merge Request

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd knowledge-engineering

# 安装开发依赖
pip install -r requirements.txt
pip install -e .

# 设置CLI工具权限
chmod +x bin/kengine_cli

# 运行测试
python run_tests.py

# 启动开发服务
python chat_server.py &
cd web && npm run dev
```

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 使用类型提示 (Type Hints)
- 编写完整的文档字符串
- 添加适当的单元测试
- 提交前运行测试套件

## 📝 更新日志

### v2.1.0 (最新)
- ✨ 完善了CLI工具文档和使用说明
- ✨ 新增 `classification` 执行步骤支持
- ✨ 优化了错误处理和用户体验
- 📚 重新整理了README文档结构
- 🐛 修复了ExecuteStep枚举定义问题

### v2.0.0
- ✨ 新增统一的CLI工具 `kengine_cli`
- ✨ 支持多种执行步骤 (classification, overview, catalogue, document, full)
- ✨ 新增 ChatRhino-81B-Pro 模型支持
- ✨ 优化了错误处理和用户体验
- 🐛 修复了CLI参数解析的多个问题
- 📚 完善了文档和使用示例

### v1.5.0
- ✨ 新增 Hybrid 生成策略
- ✨ 支持 AWS Claude Sonnet 4 模型
- ✨ 优化了RAG检索性能
- 🐛 修复了多语言文本编码问题

### v1.0.0
- 🎉 首个稳定版本发布
- ✨ 完整的项目分类和文档生成功能
- ✨ Web界面和Chat对话功能
- ✨ 完整的测试套件

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和用户！

---

**项目维护者**: 知识工程团队  
**最后更新**: 2025-08-03  
**版本**: v2.1.0
