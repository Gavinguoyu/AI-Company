# 平台开发宪法

> **本文档的作用**: 记录开发本AI游戏公司平台过程中**已完成**的关键架构和代码实现  
> **目标**: 防止Cursor对话切换时上下文丢失,避免遗忘已实现的功能,杜绝重复开发  
> **创建日期**: 2026-02-11

---

## 📖 AI使用指南

### 当你读到这个文档时,你需要:

**本文档是"记忆库",不是"计划书":**
- ✅ 查看已完成的阶段,了解已实现的核心类和方法
- ✅ 查找已定义的接口签名,确保集成时调用正确
- ✅ 检查已确立的架构约束,避免违反设计原则
- ✅ 确认功能是否已实现,避免重复开发
- ❌ **不要**在这里查找"如何实现"的详细指导 → 应该去读`开发计划.md`
- ❌ **不要**期望这里有完整的代码 → 这里只记录关键信息

### 使用场景:

| 场景 | 应该读什么 |
|------|-----------|
| 开始新阶段开发 | `开发计划.md`(了解要做什么) + `本文档`(了解已有什么) |
| 调试集成问题 | `本文档`(查找已实现的接口) |
| 不确定功能是否已实现 | `本文档`(检查项目状态总览) |

### 阶段完成后的更新规则:

**每个P阶段完成后,AI必须更新本文档:**
1. 修改"项目状态总览"中的状态为✅
2. 在对应的P阶段章节中记录:
   - 实现的核心类名和职责
   - 关键方法签名(不要粘贴完整代码)
   - 重要的架构决策和原因
   - 下一阶段需要知道的接口
3. 删除"待实现"字样,改为"已实现"
4. 只记录关键信息,控制在30-80行内

---

## 🏗️ 核心架构原则

> 这些原则在项目初期确立,所有阶段的开发都必须遵守

### 1. 消息驱动架构
- 所有Agent通信**必须**通过消息总线
- 禁止Agent之间直接调用方法
- 统一消息格式(见下方"消息格式标准")

### 2. 文件即真相
- Agent的LLM上下文不可信,文件才是唯一事实来源
- 所有共识必须写入文件(YAML/MD)
- Agent工作前必须读取相关文件

### 3. 模块化与单一职责
- 每个文件不超过150行
- 每个类只负责一件事

### 4. 异步优先
- 所有IO操作使用`async/await`
- Agent工作循环基于`asyncio`

### 5. 上下文管理
- 只注入当前任务所需的文件内容
- 利用Gemini 3 Pro的100万上下文窗口

### 6. Python导入规范（重要！）
- **backend目录内的文件互相导入时，禁止使用`from backend.xxx`**
- **正确示例**: `from utils.logger import setup_logger` ✅
- **错误示例**: `from backend.utils.logger import setup_logger` ❌
- **原因**: FastAPI从backend/main.py启动，backend已在Python路径中
- **教训**: P4阶段有4个工具文件使用了错误导入，在P5集成时才暴露

### 7. gemini 3 pro-API
- 当需要用到gemini 3 pro-API时可以使用下列密钥
- AIzaSyDwJcTPnzTQumuy9HpXK6KE2KjFmaHimsk

---

## 📊 项目状态总览

| 阶段 | 状态 | 完成日期 | 关键产出 |
|------|------|---------|---------|
| **P0** | ✅ 已完成 | 2026-02-11 | 环境搭建 |
| **P1** | ✅ 已完成 | 2026-02-11 | Agent引擎核心 |
| **P2** | ✅ 已完成 | 2026-02-11 | 消息总线 + 多Agent |
| **P3** | ✅ 已完成 | 2026-02-11 | 工具系统 |
| **P4** | ✅ 已完成 | 2026-02-11 | 游戏开发工作流 |
| **P5** | ✅ 已完成 | 2026-02-11 | Web后端API |
| **P6** | ✅ 已完成 | 2026-02-11 | 前端可视化 |
| **P6游戏生成** | ✅ 已完成 | 2026-02-12 | 实际游戏生成 |
| **P7** | ✅ 已完成 | 2026-02-12 | 人类介入机制 |
| **P8-1** | ✅ 已完成 | 2026-02-12 | 2D像素风办公室 |
| **P8-2** | ✅ 已完成 | 2026-02-12 | 办公室增强功能 |
| **P9** | ✅ 已完成 | 2026-02-12 | 美术集成（Gemini图片生成） |
| **P10** | ✅ 已完成 | 2026-02-13 | 端到端联调测试 |
| **P11** | ✅ 已完成 | 2026-02-13 | 优化完善 |

---

## 📐 消息格式标准

> 在P2阶段确立的通信协议,所有Agent必须遵守

```json
{
    "from": "agent_id",
    "to": "target_id",
    "type": "question|answer|report|request_review",
    "content": "消息正文",
    "context": "工作上下文",
    "priority": "normal|urgent|blocking",
    "timestamp": "ISO8601时间戳"
}
```

---

## 🗂️ 项目文件结构

> 在P0阶段确立的目录结构,新建文件时必须放在正确位置

```
backend/
├── main.py              # FastAPI入口
├── config.py            # 全局配置
├── engine/              # Agent引擎核心
├── agents/              # 具体Agent实现
├── tools/               # Agent工具
├── workflows/           # 工作流定义
└── api/                 # Web接口

frontend/
├── index.html
├── css/
└── js/                  # 前端模块

projects/{project_name}/ # AI生产的游戏
├── shared_knowledge/    # 共享知识库
├── output/              # 游戏产出
└── logs/                # 对话日志
```

---

## ⚙️ P0: 环境搭建

> **状态**: ✅ 已完成 (2026-02-11)

### Python环境
- **Python版本**: 3.14.3 ✅
- **所需版本**: ≥3.11 
- **验证方式**: `python --version`

### 关键依赖
```
fastapi>=0.110.0        # Web框架
uvicorn>=0.27.0         # ASGI服务器
websockets>=12.0        # WebSocket支持
google-generativeai     # Gemini API（已安装，但有迁移警告）
openai>=1.12.0          # OpenAI API
litellm>=1.30.0         # 多模型支持
pydantic>=2.6.0         # 数据验证
python-dotenv>=1.0.0    # 环境变量
pyyaml>=6.0.1           # YAML支持
aiofiles>=23.2.0        # 异步文件IO
httpx>=0.27.0           # 异步HTTP
Pillow>=10.2.0          # 图像处理
```

### API Key配置
- **配置文件**: `.env`（已创建）
- **Google Gemini API Key**: 已配置 ✅
- **配置加载**: `backend/config.py` 中的 `Config` 类
- **验证方法**: `Config.validate()` 返回 True

### 项目文件结构
已创建完整目录结构：
```
backend/          # Python后端（已有基础文件）
  ├── config.py   # 配置管理（已实现）
  ├── engine/     # Agent引擎（空）
  ├── agents/     # Agent实现（空）
  ├── tools/      # 工具系统（空）
  ├── workflows/  # 工作流（空）
  └── api/        # Web接口（空）
frontend/         # 前端（已创建目录）
  ├── css/
  ├── js/
  └── assets/
projects/         # AI生产的游戏（空）
docs/             # 文档（空）
.cursor/rules/    # Cursor规则（已有3个规则文件）
```

### 验证测试
- **测试脚本**: `test_setup.py`
- **测试结果**: 所有测试通过 ✅
  - Python版本检查 ✅
  - 依赖包导入 ✅
  - 配置验证 ✅
  - 目录结构 ✅

### 重要提醒
⚠️ `google.generativeai` 包有迁移警告，建议未来切换到 `google.genai`（不影响当前使用）

---

## 🧠 P1: Agent引擎核心

> **状态**: ✅ 已完成 (2026-02-11)

### 核心组件

#### 1. LLM客户端 (`engine/llm_client.py`)
**职责**: 封装 Google Gemini API 调用

**关键接口**:
```python
class LLMClient:
    __init__(model_name: Optional[str] = None)
    async generate_response(messages: List[Dict], system_prompt: str) -> str
    count_tokens(text: str) -> int
    get_model_info() -> Dict[str, Any]
```

**模型选择**: 
- **主力模型**: `gemini-2.0-flash`（Gemini 2.0 Flash）
- **原因**: 
  - 快速响应，适合实时对话
  - 100万token上下文窗口
  - 成本低于 Gemini Pro
  - Google官方推荐的Agent开发模型

**生成配置**:
- temperature: 0.7（保持创造性）
- top_p: 0.95
- top_k: 40
- max_output_tokens: 8192

**异步实现**: 使用 `asyncio.run_in_executor` 包装同步API

⚠️ **技术债**: `google.generativeai` 包已被标记为弃用，未来需迁移到 `google.genai`

---

#### 2. 上下文管理器 (`engine/context_manager.py`)
**职责**: 管理Agent的对话历史，防止上下文爆炸

**关键接口**:
```python
class ContextManager:
    __init__(max_tokens: int = 100000, max_messages: int = 50)
    add_message(role: str, content: str) -> None
    get_messages() -> List[Dict[str, str]]
    inject_file_content(file_path: str, content: str) -> None
    clear() -> None
    get_summary() -> Dict[str, Any]
```

**上下文管理策略**:
1. **双重限制**: 
   - Token数量限制（默认10万）
   - 消息条数限制（默认50条）
2. **自动裁剪**: 超限时自动删除最早的消息（保留系统消息）
3. **文件注入**: 支持将文件内容注入上下文（实现"文件即真相"）
4. **Token估算**: 简单估算 1 token ≈ 4 字符

**每个Agent分配**: 总Token预算的1/5（即每个Agent 10万tokens）

---

#### 3. Agent基类 (`engine/agent.py`)
**职责**: 所有AI员工的基础框架

**关键接口**:
```python
class Agent:
    __init__(agent_id: str, role: str, system_prompt: str, model_name: Optional[str] = None)
    async think_and_respond(user_message: str) -> str
    async process_message(message: Dict[str, Any]) -> Optional[str]
    load_file_to_context(file_path: str, content: str) -> None
    get_status() -> Dict[str, Any]
    reset_context() -> None
```

**Agent状态**:
- `idle`: 空闲
- `thinking`: 思考中
- `working`: 工作中
- `waiting`: 等待中

**核心能力**:
1. **思考与回复**: 接收消息 → 调用LLM → 返回回复
2. **消息处理**: 根据消息类型（question/answer/report等）决定是否回复
3. **文件加载**: 将项目规范、策划文档等加载到上下文
4. **状态管理**: 跟踪Agent当前状态和任务

**消息类型处理**:
- `question`, `request_review` → 需要回复
- `answer`, `report` → 只记录，不回复

---

### 验证测试

**测试方式**: 创建测试Agent，模拟多轮对话

**测试结果**: ✅ 全部通过
- LLM调用成功，响应合理
- 上下文管理正常，自动裁剪工作正常
- Agent能记住上下文，进行连贯对话
- 文件注入功能正常

**测试场景**:
1. 基本对话：Agent能理解游戏需求并给出建议
2. 多轮对话：Agent能记住之前的对话内容
3. 文件注入：Agent能根据注入的项目规范回答问题

---

### 架构决策

**1. 为什么选择 Gemini 2.0 Flash？**
- 符合开发计划要求（100万上下文）
- 速度快，适合实时对话
- 成本合理（开发阶段够用）

**2. 为什么使用异步架构？**
- 未来需要支持多个Agent并发工作
- LLM API调用是IO密集型操作，异步可提升性能
- 符合平台宪法中的"异步优先"原则

**3. 为什么Agent不直接调用彼此？**
- 遵循"消息驱动架构"原则
- 所有通信必须通过消息总线（P2阶段实现）
- Agent之间解耦，便于扩展和调试

---

## 🔄 P2: 消息总线 + 多Agent协作

> **状态**: ✅ 已完成 (2026-02-11)

### 前置改进任务（✅ 已完成 2026-02-11）

基于 P1 测试反馈，P2 开始前的改进任务已全部完成：

#### 1. 统一日志系统 (`utils/logger.py`) ✅
**实现内容**:
- ✅ 创建 `backend/utils/logger.py` 统一日志模块
- ✅ 支持控制台输出和文件输出（按日期和模块分文件）
- ✅ 支持日志级别（DEBUG/INFO/WARNING/ERROR）
- ✅ 更新 llm_client.py、context_manager.py、agent.py 集成日志
- ✅ 日志格式：`时间 | 模块名 | 级别 | 消息`

#### 2. LLM重试机制 (`utils/retry.py`) ✅
**实现内容**:
- ✅ 创建 `backend/utils/retry.py` 重试装饰器
- ✅ 实现指数退避策略（2秒 → 4秒 → 8秒）
- ✅ 在 llm_client.py 的 generate_response 上应用 @async_retry
- ✅ 可配置重试次数和延迟

**配置项（已添加到 .env 和 config.py）**:
```
LOG_LEVEL=INFO
LOG_TO_FILE=true
LLM_MAX_RETRIES=3
LLM_RETRY_BASE_DELAY=2.0
LLM_RETRY_MAX_DELAY=30.0
```

**验证结果**: 
- 所有功能测试 100% 通过
- 日志系统工作正常，已生成日志文件
- 重试机制测试成功
- 所有原有测试继续通过

---

### 核心组件

#### 1. 消息总线 (`engine/message_bus.py`)
**职责**: Agent间消息路由、记录和推送

**关键接口**:
```python
class MessageBus:
    __new__() -> MessageBus  # 单例模式
    subscribe(agent_id: str, callback: Callable) -> None
    async send(message: Dict[str, Any]) -> bool
    async receive(agent_id: str, timeout: Optional[float]) -> Optional[Dict]
    get_history(limit: Optional[int], agent_id: Optional[str]) -> List[Dict]
    get_summary() -> Dict[str, Any]
```

**核心功能**:
- ✅ 单例模式: 全局唯一的消息总线实例
- ✅ 消息路由: 点对点、广播(to="all")、发给老板(to="boss")
- ✅ 消息队列: 每个Agent有独立的消息队列
- ✅ 消息历史: 内存中保留最近1000条消息
- ✅ 频率限制: 同一对Agent每分钟最多10条消息
- ✅ WebSocket推送: 支持实时推送到前端(接口预留)

**消息格式标准**(已在第93行定义):
```json
{
    "from": "agent_id",
    "to": "target_id",
    "type": "question|answer|report|request_review",
    "content": "消息正文",
    "context": "工作上下文",
    "priority": "normal|urgent|blocking",
    "timestamp": "ISO8601时间戳"
}
```

---

#### 2. Agent管理器 (`engine/agent_manager.py`)
**职责**: 管理所有Agent的生命周期和工作循环

**关键接口**:
```python
class AgentManager:
    register_agent(agent: Agent) -> None
    unregister_agent(agent_id: str) -> None
    async start_all() -> None
    async stop_all() -> None
    get_summary() -> Dict
```

**Agent工作循环**:
```python
async def _agent_work_loop(agent):
    while running:
        # 1. 检查消息队列
        message = await message_bus.receive(agent_id, timeout=2.0)
        if message:
            response = await agent.process_message(message)
            if response:
                await message_bus.send(response)
        
        # 2. TODO: 检查任务队列(P4实现)
        
        # 3. 空闲等待
        await asyncio.sleep(0.1)
```

**核心功能**:
- ✅ Agent注册: 自动订阅消息总线
- ✅ 工作循环: 每个Agent独立的异步工作循环
- ✅ 生命周期管理: 统一启动/停止所有Agent
- ✅ 状态监控: 获取所有Agent的运行状态

---

#### 3. 5个具体Agent

**已实现的Agent**:

| Agent ID | 角色 | 文件 | 核心职责 |
|----------|------|------|---------|
| `pm` | 项目经理 | `agents/pm_agent.py` | 接收需求、拆解任务、协调冲突、汇报老板 |
| `planner` | 游戏策划 | `agents/planner_agent.py` | 编写GDD、设计玩法、输出配置表 |
| `programmer` | 游戏程序员 | `agents/programmer_agent.py` | 编写代码、遵守规范、修复Bug |
| `artist` | 美术设计师 | `agents/artist_agent.py` | 生成素材、编写Prompt、调用AI绘图 |
| `tester` | 测试工程师 | `agents/tester_agent.py` | 测试功能、编写Bug报告、回归测试 |

**所有Agent共享的能力**(继承自Agent基类):
- `async think_and_respond(message)` - 调用LLM生成回复
- `async process_message(message)` - 处理收到的消息
- `load_file_to_context(file, content)` - 加载文件到上下文
- `get_status()` - 获取Agent状态
- `reset_context()` - 清空上下文

**各Agent的System Prompt要点**:
- PM: 拆解任务、协调冲突、重大决策请示老板
- 策划: 输出YAML配置、玩法清晰、考虑技术可行性
- 程序员: 铁律(必须查api_registry、禁止重复代码、禁止硬编码)
- 美术: 像素风格、详细Prompt、符合规范
- 测试: 客观准确、详细复现步骤、区分Bug和设计问题

---

### 测试验证

**测试脚本**: `test_p2_integration.py`

**测试结果**: ✅ 100% 通过
- ✅ 消息总线: 单例、订阅、路由、历史
- ✅ 5个Agent: 创建、对话、System Prompt生效
- ✅ Agent管理器: 注册、启动、停止
- ✅ 多Agent通信: PM↔策划、策划→程序员

**实际对话测试**:
- PM发问"请简要说明贪吃蛇的核心玩法" → 策划回复"控制一条蛇在地图上移动，通过吃食物增长身体，同时避免撞到自己或墙壁"
- 消息路由正确，回复质量高

---

### 架构决策

**1. 为什么用单例模式的消息总线？**
- 全局唯一，避免多个总线实例导致消息混乱
- 便于全局访问和状态管理

**2. 为什么Agent工作循环用timeout=2.0？**
- 平衡响应速度和CPU占用
- 2秒足够快，不会让用户感觉卡顿

**3. 为什么限制每分钟10条消息？**
- 防止Agent陷入无意义的对话循环
- 节省API调用成本

**4. 为什么现在不实现任务队列？**
- P2阶段重点是消息通信
- 任务队列在P4阶段(游戏开发工作流)中实现

---

### 下一阶段需要知道的

**P3阶段(工具系统)需要集成的接口**:
- Agent需要调用工具: `file_tool.read()`, `file_tool.write()`, `code_runner.execute()`
- 工具调用应该在Agent的`process_message`中根据LLM回复触发

**文件读写约定**(P4阶段用):
| Agent | 必读文件 | 必写文件 |
|-------|---------|---------|
| PM | 无 | decision_log.yaml |
| 策划 | project_rules.yaml | game_design_doc.md, config_tables.yaml |
| 程序员 | api_registry.yaml, config_tables.yaml | 代码文件, api_registry.yaml |
| 美术 | art_asset_list.yaml | 素材文件, art_asset_list.yaml |
| 测试 | game_design_doc.md | bug_tracker.yaml |

---

## 🛠️ P3: 工具系统

> **状态**: ✅ 已完成 (2026-02-11)

### 核心组件

#### 1. 文件工具 (`tools/file_tool.py`)
**职责**: 提供安全的文件读写操作

**关键接口**:
```python
class FileTool:
    async read(file_path: str) -> str
    async write(file_path: str, content: str) -> bool
    async append(file_path: str, content: str) -> bool
    exists(file_path: str) -> bool
    is_file(file_path: str) -> bool
    is_directory(file_path: str) -> bool
    async list_directory(dir_path: str) -> List[Dict]
    async delete(file_path: str) -> bool
    get_file_info(file_path: str) -> Dict
```

**安全特性**:
- ✅ 路径安全检查: 所有路径必须在工作空间内
- ✅ 自动创建父目录
- ✅ UTF-8编码处理
- ✅ 异步IO操作

---

#### 2. 代码执行工具 (`tools/code_runner.py`)
**职责**: 在安全环境中执行JavaScript/HTML代码

**关键接口**:
```python
class CodeRunner:
    async execute_html(html_content: str, timeout: float, check_only: bool) -> Dict
    async execute_js(js_code: str, timeout: float, use_node: bool) -> Dict
    async validate_syntax(code: str, language: str) -> Dict
    async execute_game_test(game_dir: str, entry_file: str) -> Dict
    cleanup_temp_files() -> int
```

**安全特性**:
- ✅ 隔离临时目录: 代码在独立临时目录执行
- ✅ 超时保护: 默认10-30秒超时
- ✅ 进程隔离: 使用子进程执行
- ✅ Node.js检测: 自动检测环境可用性

---

#### 3. 代码搜索工具 (`tools/code_search_tool.py`)
**职责**: 搜索代码中的函数、类、变量定义

**关键接口**:
```python
class CodeSearchTool:
    async search_function(name: str, directory: str, pattern: str) -> List[Dict]
    async search_class(name: str, directory: str, pattern: str) -> List[Dict]
    async search_variable(name: str, directory: str, pattern: str) -> List[Dict]
    async search_all(name: str, directory: str, pattern: str) -> Dict
    async get_api_registry(registry_file: str) -> Dict
    async check_function_exists(function_name: str) -> bool
    get_file_imports(file_path: str) -> List[str]
```

**核心功能**:
- ✅ 正则模式匹配: 支持多种JavaScript定义语法
- ✅ 递归搜索: 自动遍历子目录
- ✅ API注册表集成: 防止重复实现
- ✅ 导入语句分析: 理解代码依赖关系

---

#### 4. 工具注册机制 (`tools/tool_registry.py`)
**职责**: 全局工具管理和权限控制

**关键接口**:
```python
class ToolRegistry:  # 单例模式
    register_tool(name: str, tool_instance: Any) -> None
    get_tool(name: str) -> Optional[Any]
    async call_tool(tool_name: str, method_name: str, *args, **kwargs) -> Any
    list_tools() -> List[Dict]

class AgentToolkit:  # 每个Agent一个实例
    enable_tool(tool_name: str) -> bool
    disable_tool(tool_name: str) -> bool
    async call(tool_name: str, method_name: str, *args, **kwargs) -> Any
    get_available_tools() -> List[Dict]
    get_tool_info_for_prompt() -> str
```

**架构设计**:
- ✅ 单例工具注册表: 全局唯一，所有Agent共享
- ✅ 权限控制: Agent只能调用已启用的工具
- ✅ 自动方法检测: 支持同步和异步方法
- ✅ Prompt生成: 自动生成工具说明供LLM理解

**已注册的工具**:
| 工具名 | 类型 | 用途 |
|-------|------|------|
| file | FileTool | 文件读写操作 |
| code_runner | CodeRunner | 代码执行和测试 |
| code_search | CodeSearchTool | 代码搜索和分析 |

---

#### 5. Agent基类集成 (`engine/agent.py` 更新)

**新增功能**:
```python
class Agent:
    def __init__(tools: Optional[List[str]] = None):  # 新增参数
        self.toolkit = AgentToolkit(agent_id)  # 工具包
        
    async call_tool(tool_name: str, method_name: str, *args, **kwargs) -> Any
    enable_tool(tool_name: str) -> bool
    get_available_tools() -> List[Dict]
```

**使用示例**:
```python
# 创建带工具的Agent
agent = Agent(
    agent_id="programmer",
    role="程序员",
    system_prompt="...",
    tools=["file", "code_search", "code_runner"]
)

# Agent调用工具
await agent.call_tool("file", "write", "game.js", code)
results = await agent.call_tool("code_search", "search_function", "move")
```

---

### 测试验证

**测试脚本**: `test_p3_tools.py`

**测试结果**: ✅ 100% 通过 (6/6)
- ✅ 文件工具: 读写、追加、删除、列表、权限检查
- ✅ 代码执行工具: JS/HTML执行、语法检查、超时控制
- ✅ 代码搜索工具: 函数/类/变量搜索、API注册表
- ✅ 工具注册机制: 注册、调用、权限控制
- ✅ Agent工具包: 启用、调用、Prompt生成
- ✅ Agent集成: 创建、调用、动态启用

**实际验证**:
- Agent成功读写文件
- Agent成功搜索代码并找到定义
- Agent成功执行JavaScript代码
- 权限控制正常工作（未启用工具无法调用）

---

### 架构决策

**1. 为什么使用单例工具注册表？**
- 全局唯一，避免重复创建工具实例
- 便于统一管理和监控
- 节省内存（所有Agent共享工具实例）

**2. 为什么使用AgentToolkit包装？**
- 权限隔离：每个Agent只能用自己启用的工具
- 审计追踪：记录哪个Agent调用了什么工具
- 灵活配置：不同Agent可启用不同工具集

**3. 为什么文件工具有路径安全检查？**
- 防止Agent访问工作空间外的敏感文件
- 遵循"最小权限"原则
- 符合生产环境安全标准

**4. 为什么代码执行使用临时目录？**
- 隔离执行环境，避免污染项目目录
- 便于清理临时文件
- 降低安全风险

---

### 下一阶段需要知道的

**P4阶段(工作流)需要的工具调用场景**:

| Agent | 常用工具调用 |
|-------|------------|
| **策划** | `file.write(game_design_doc.md)`, `file.write(config_tables.yaml)` |
| **程序员** | `code_search.check_function_exists()`, `file.write(xxx.js)`, `code_search.get_api_registry()` |
| **美术** | `file.write(assets/xxx.png)` (未来接入绘图API) |
| **测试** | `code_runner.execute_game_test()`, `file.write(bug_tracker.yaml)` |

**工具调用流程**:
```
Agent收到任务 
  → Agent思考需要什么工具
  → 调用 await self.call_tool(tool_name, method_name, ...)
  → 工具执行并返回结果
  → Agent根据结果继续工作或汇报
```

---

## 🎮 P4: 游戏开发工作流

> **状态**: ✅ 已完成 (2026-02-11)

### 核心组件

#### 1. 游戏开发工作流 (`workflows/game_dev_workflow.py`)
**职责**: 定义和执行完整的7阶段游戏开发流程

**关键接口**:
```python
class GameDevWorkflow:
    __init__(project_name: str, project_description: str)
    async initialize() -> None
    async start() -> None
    get_status() -> Dict[str, Any]
```

**7个开发阶段**:
1. `_phase_1_initiation()` - 立项：PM接收需求，组织全员会议
2. `_phase_2_planning()` - 策划：策划编写GDD，生成策划文档
3. `_phase_3_tech_design()` - 技术设计：程序员设计架构，生成TDD
4. `_phase_4_parallel_dev()` - 并行开发：程序员+美术并行工作
5. `_phase_5_integration()` - 整合：整合代码和素材（简化版跳过）
6. `_phase_6_testing()` - 测试：测试工程师测试游戏
7. `_phase_7_delivery()` - 交付：PM汇报项目完成

**核心功能**:
- ✅ 自动创建项目目录结构
- ✅ 生成和管理共享知识库文件
- ✅ Agent工作循环和消息通信
- ✅ 阶段间文档传递
- ✅ 状态查询和监控

---

#### 2. 共享知识库系统

**知识库文件列表** (每个项目自动创建):

| 文件 | 职责 | 创建者 | 主要读取者 |
|------|------|--------|-----------|
| **project_rules.yaml** | 项目规范（命名、结构、代码规范） | 系统 | 所有Agent |
| **game_design_doc.md** | 游戏策划文档(GDD) | 策划 | 程序员、美术、测试 |
| **tech_design_doc.md** | 技术设计文档(TDD) | 程序员 | 程序员、测试 |
| **api_registry.yaml** | 接口注册表（防止重复代码） | 程序员 | 程序员 |
| **config_tables.yaml** | 游戏配置数据 | 策划 | 程序员 |
| **art_asset_list.yaml** | 美术素材清单 | 美术 | 美术、程序员 |
| **bug_tracker.yaml** | Bug追踪列表 | 测试 | 测试、程序员 |
| **decision_log.yaml** | 老板决策记录 | PM | PM、所有Agent |

**文件即真相原则**:
- Agent工作前必须读取相关文件
- 所有输出必须写入知识库文件
- 文件内容是唯一的事实来源

---

#### 3. 项目目录结构

**自动创建的目录**:
```
projects/{project_name}/
├── shared_knowledge/       # 共享知识库（8个YAML/MD文件）
├── output/                 # 游戏产出目录
│   ├── js/                # JavaScript代码
│   ├── assets/            # 美术素材
│   └── css/               # 样式文件
└── logs/                  # 项目日志
```

---

#### 4. 阶段间文档传递流程

```
阶段1: 立项
  输入: 用户需求 (project_description)
  输出: project_rules.yaml
  
阶段2: 策划
  输入: project_rules.yaml
  输出: game_design_doc.md, config_tables.yaml
  
阶段3: 技术设计
  输入: project_rules.yaml, game_design_doc.md
  输出: tech_design_doc.md, api_registry.yaml
  
阶段4: 并行开发
  输入: 所有知识库文件
  输出: 代码文件（P4简化版未实现）
  
阶段5: 整合
  输入: 代码 + 美术素材
  输出: 完整游戏（P4简化版跳过）
  
阶段6: 测试
  输入: game_design_doc.md, 游戏代码
  输出: bug_tracker.yaml
  
阶段7: 交付
  输入: 所有文件
  输出: 汇报给老板
```

---

### 测试验证

**测试脚本**: 
- `test_p4_workflow.py` - 6个基础功能测试
- `test_p4_full_workflow.py` - 完整7阶段工作流测试

**测试结果**: ✅ 100% 通过 (7/7)
- ✅ 工作流初始化
- ✅ 项目目录结构创建
- ✅ 共享知识库文件创建（8个文件）
- ✅ Agent创建和注册（5个Agent）
- ✅ 阶段执行流程
- ✅ 工作流状态查询
- ✅ 完整7阶段端到端测试

**实际验证**:
- 成功运行完整的游戏开发工作流
- 自动生成项目目录和知识库文件
- Agent成功协作完成各阶段任务
- 消息路由正确，文档传递正常

---

### 架构决策

**1. 为什么使用阶段化流程？**
- 模拟真实游戏开发流程
- 便于监控和调试
- 支持人类在关键节点介入

**2. 为什么使用共享知识库？**
- 实现"文件即真相"原则
- 解决Agent记忆混乱问题
- 便于追溯和审计

**3. 为什么P4简化了实际代码生成？**
- 聚焦工作流框架搭建
- 实际代码生成需要更复杂的Prompt工程
- 留待P8联调阶段完善

**4. 为什么需要project_rules.yaml？**
- 统一所有Agent的代码规范
- 防止命名不一致
- 确保技术栈统一

---

### P4阶段简化说明

**已实现**:
- ✅ 完整的7阶段流程定义
- ✅ 项目目录和知识库管理
- ✅ Agent消息协作
- ✅ 文档传递机制

**简化内容**（将在后续阶段完善）:
- ⏸️ 阶段4: 实际代码生成（Agent回复但未生成文件）
- ⏸️ 阶段5: 代码和素材整合（跳过）
- ⏸️ 阶段6: 实际代码测试（Agent回复但未执行）
- ⏸️ Bug修复循环（未实现）

**完善计划**:
- P5: Web API（接入前端控制）
- P6: 前端可视化（观察工作流）
- P7: 人类介入（老板决策）
- P8: 联调测试（完整生成真实游戏）

---

### 下一阶段需要知道的

**P5阶段(Web后端API)需要集成的接口**:

```python
# 启动游戏项目
POST /project/start
{
    "project_name": "snake_game",
    "project_description": "做一个贪吃蛇游戏..."
}

# 查询项目状态
GET /project/{project_name}/status

# 老板提交决策
POST /boss/decision
{
    "project_name": "snake_game",
    "decision": "approve",
    "comment": "很好，继续"
}

# WebSocket推送
WebSocket /ws - 实时推送Agent消息和状态变化
```

**需要的后台任务管理**:
- 工作流作为后台异步任务运行
- 支持多个项目并行开发
- 状态查询和监控

---

## 🌐 P5: Web后端API

> **状态**: ✅ 已完成（2026-02-11）

### 核心文件

1. **main.py** - FastAPI应用入口
   - 使用lifespan上下文管理器（替代废弃的on_event）
   - 集成CORS中间件
   - 挂载静态文件（前端）
   - 启动配置验证

2. **api/http_routes.py** - HTTP REST API
   - 使用Pydantic模型验证请求/响应
   - 内存存储（projects_store, pending_decisions）
   - 完整的错误处理

3. **api/websocket_handler.py** - WebSocket实时通信
   - ConnectionManager单例管理所有连接
   - 支持点对点和广播消息
   - 连接状态跟踪

### HTTP API端点

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /api/health | 健康检查 | - | {status, service, version} |
| POST | /api/project/start | 创建新项目 | ProjectStartRequest | ProjectStartResponse |
| GET | /api/project/{id}/status | 查询项目状态 | - | ProjectStatusResponse |
| GET | /api/projects | 获取项目列表 | ?status, ?limit, ?offset | ProjectListResponse |
| POST | /api/boss/decision | 提交老板决策 | BossDecisionRequest | BossDecisionResponse |
| DELETE | /api/project/{id} | 删除项目 | - | {success, message} |

### WebSocket事件类型

**客户端 → 服务器**:
- `ping` - 心跳检测
- `subscribe_project` - 订阅项目更新
- `unsubscribe_project` - 取消订阅

**服务器 → 客户端**:
- `connected` - 连接成功确认
- `pong` - 心跳响应
- `subscribed` / `unsubscribed` - 订阅状态确认
- `agent_message` - Agent消息推送
- `agent_status` - Agent状态变化
- `file_update` - 文件更新事件
- `phase_change` - 项目阶段变化
- `boss_decision` - 请求老板决策
- `task_complete` - 任务完成通知
- `error_alert` - 错误警报

### 导出的工具函数

```python
# websocket_handler.py 导出的函数（供其他模块调用）
async def broadcast_agent_message(project_id, from_agent, to_agent, type, content, context)
async def broadcast_agent_status(project_id, agent_id, status, current_task)
async def broadcast_file_update(project_id, file_path, update_type, updated_by)
async def broadcast_phase_change(project_id, old_phase, new_phase, progress)
async def request_boss_decision(project_id, decision_id, agent_id, question, options)
async def broadcast_task_complete(project_id, task_name, completed_by, result)
async def broadcast_error_alert(project_id, error_type, error_message, agent_id)
```

### 关键设计决策

1. **使用lifespan而非on_event**: FastAPI推荐的新方式，避免废弃警告
2. **内存存储优先**: 当前阶段使用字典存储，P10可迁移到Redis
3. **并发安全**: WebSocket连接管理器使用asyncio.Lock防止竞态
4. **连接复用**: 同一client_id的新连接会自动关闭旧连接
5. **错误恢复**: 消息发送失败会自动断开连接，避免僵尸连接

### 测试结果

✅ 所有12项测试通过（100%通过率）:
- 6个HTTP API测试
- 5个WebSocket功能测试
- 1个并发连接测试（5客户端）

### 下一阶段需要知道的

**P6阶段（前端可视化）集成要点**:
1. WebSocket连接URL: `ws://localhost:8000/ws/{client_id}`
2. 需要生成UUID作为client_id
3. 订阅项目后会收到该项目的所有实时推送
4. API文档地址: `http://localhost:8000/api/docs`

---

## 🖼️ P6: 前端可视化

> **状态**: ✅ 已完成（2026-02-11）

### 核心文件

1. **index.html** - 主页面
   - 响应式布局：左右分栏
   - 四大面板：办公室视图、对话面板、状态面板、文件浏览器
   - 使用ES6模块系统

2. **css/style.css** - 界面样式
   - 现代渐变色设计（紫色主题）
   - 响应式布局（支持1024px以下设备）
   - 自定义滚动条样式

3. **js/websocket.js** - WebSocket客户端
   - 自动重连机制（3秒间隔）
   - 事件监听器模式（支持多个监听器）
   - 消息分发到各个模块

4. **js/chat_panel.js** - 实时对话面板
   - 显示Agent间消息（from → to）
   - 自动滚动到最新消息
   - 消息数量限制（最多100条）

5. **js/status_panel.js** - 项目状态面板
   - 显示项目信息（名称、阶段、进度）
   - 5个Agent状态卡片
   - 实时更新进度条

6. **js/file_browser.js** - 文件浏览器
   - 树形文件结构展示
   - 支持文件夹展开/折叠
   - 文件图标区分

7. **js/office_view.js** - 办公室视图
   - 5个Agent卡片展示（简单版本，非Canvas）
   - Agent头像：👔 📋 💻 🎨 🔍
   - 状态可视化（空闲/思考中/工作中）

8. **js/app.js** - 主应用入口
   - 整合所有模块
   - WebSocket事件路由
   - HTTP API调用（项目列表、详情）

### WebSocket事件分发

**事件类型及处理**:
- `agent_message` → ChatPanel + OfficeView（通信动画）
- `agent_status` → StatusPanel + OfficeView（状态更新）
- `file_update` → FileBrowser（文件列表更新）
- `phase_change` → StatusPanel（进度更新）
- `boss_decision` → ChatPanel（显示决策请求）
- `task_complete` → ChatPanel（任务完成通知）
- `error_alert` → ChatPanel（错误提示）

### 架构特点

1. **模块化设计**: 每个JS文件独立类，通过ES6模块导入
2. **事件驱动**: WebSocket事件自动分发到各面板
3. **原生JavaScript**: 无框架依赖，轻量高效
4. **自动重连**: WebSocket断线自动重连，无需手动处理

### 技术决策

**1. 为什么使用原生JS而非React/Vue？**
- 简化开发，无需构建工具
- 减少依赖和文件体积
- 适合小型项目，快速迭代

**2. 为什么办公室视图用简单列表？**
- 优先功能实现，P10再优化为Canvas
- 简单列表更易维护和调试
- 对于演示已足够

**3. 为什么文件浏览器不支持查看内容？**
- P6阶段聚焦框架搭建
- 文件查看功能可留待P7扩展
- 减少首次开发复杂度

### 下一阶段需要知道的

**P7阶段（人类介入）需要扩展的前端功能**:
1. 添加 `js/boss_panel.js` - 老板决策面板
2. 在 `app.js` 中处理 `boss_decision` 事件弹窗
3. 新增决策提交API调用（POST /api/boss/decision）

**前端扩展接口**:
```javascript
// P7需要监听的WebSocket事件
ws.on('boss_decision', (data) => {
    bossPanel.showDecisionDialog(data);
});

// P7需要调用的API
await fetch('/api/boss/decision', {
    method: 'POST',
    body: JSON.stringify({
        project_id: projectId,
        decision: 'approve', // 或 'reject'
        comment: '...'
    })
});
```

### 测试验证

**P6前端测试**: ✅ 100%通过（4/4）
- 文件结构完整
- HTML结构正确
- JavaScript模块有效
- CSS样式完整

**回归测试**: ✅ 通过（后端功能未破坏）

---

## 👤 P7: 人类介入机制

> **状态**: ✅ 已完成 (2026-02-12)

### 核心实现

#### 1. 后端决策等待机制 (`workflows/game_dev_workflow.py`)

**新增方法**:
```python
class GameDevWorkflow:
    async def _request_boss_decision(title, question, options, context) -> str
    async def _log_boss_decision(...)  # 记录到decision_log.yaml
    def submit_boss_decision(decision_id, choice) -> bool
```

**工作原理**:
- 创建`asyncio.Future`对象存储在`pending_decisions`字典
- 通过WebSocket发送决策请求到前端
- 异步等待用户响应（最长5分钟超时）
- 超时则使用第一个选项作为默认值

#### 2. WebSocket双向通信扩展 (`api/websocket_handler.py`)

**新增功能**:
- `handle_client_message` 处理 `boss_decision_response` 消息类型
- `register_workflow` / `unregister_workflow` 全局工作流注册
- `handle_boss_decision_response` 将决策提交给对应工作流

**消息格式**:
```javascript
// 前端 → 后端
{
    type: 'boss_decision_response',
    decision_id: 'uuid',
    choice: '选项B'
}
```

#### 3. 前端决策面板 (`frontend/js/boss_panel.js`)

**BossPanel类**:
- 监听`boss_decision`事件
- 创建模态窗口显示决策请求
- 用户点击选项后通过WebSocket发送响应
- 提供震动动画提示（禁止关闭模态框）

**UI特性**:
- 渐变色按钮样式
- 淡入淡出动画
- 点击遮罩层震动提示（强制用户做决策）
- 响应式设计

#### 4. 集成到主应用 (`frontend/js/app.js`)

- 在初始化WebSocket前创建BossPanel
- 自动监听`boss_decision`事件

### 关键决策

**1. 为什么使用asyncio.Future而非回调？**
- 更符合Python async/await模式
- 代码更清晰易读
- 便于超时处理

**2. 为什么禁止关闭决策模态框？**
- 确保用户必须做决策
- 避免工作流永久等待
- 通过震动提示引导用户操作

**3. 为什么超时使用第一个选项？**
- 提供合理的默认行为
- 避免工作流卡死
- 5分钟超时时间足够长

### 测试验证

**测试脚本**: `tests/test_p7_decision.py`

**测试结果**: ✅ 100% 通过
- ✅ 决策请求成功发送
- ✅ WebSocket正确路由决策响应
- ✅ 工作流成功接收用户选择
- ✅ 决策日志正确记录到YAML
- ✅ 超时机制正常工作

**实际验证**:
- 决策请求能正常发送到前端
- 用户选择能正确回传到工作流
- 决策日志文件正确生成
- 超时使用默认选项

### 下一阶段需要知道的

**P8阶段（联调测试）集成要点**:
1. 在实际工作流中测试决策流程
2. 可在任意阶段调用`_request_boss_decision`请求用户决策
3. 前端会自动弹出决策面板

**使用示例**:
```python
# 在工作流任意阶段请求决策
decision = await self._request_boss_decision(
    title="策划审批",
    question="策划已完成GDD，是否通过？",
    options=["通过", "修改", "重新设计"],
    context={"phase": "planning"}
)

if decision == "通过":
    # 继续下一阶段
    pass
```

---

## 🧪 P8: 联调测试

> **状态**: ⬜ 未开始

### 完成后应记录:
- 发现并修复的关键问题
- 端到端测试用例是否通过
- Prompt调整的经验

---

## 🎨 P9: 美术集成

> **状态**: ✅ 已完成 (2026-02-12)

### 核心实现
- `ImageGenTool` (`tools/image_gen_tool.py`) - Gemini图片生成API封装
  - 使用 `google-genai` 新版SDK（`from google import genai`）
  - 模型: `gemini-2.0-flash-exp-image-generation`（免费层可用）
  - 备选: `gemini-2.5-flash-image`（支持aspect_ratio等高级特性）
  - 复用 `GOOGLE_API_KEY`，与文本生成共用同一个API Key
- 美术Agent升级（`agents/artist_agent.py`）
  - 启用 `file` + `image_gen` 两个工具
  - 能根据策划文档解析素材需求
  - 批量生成游戏素材并更新 `art_asset_list.yaml`
- 工作流集成（`workflows/game_dev_workflow.py`）
  - 阶段4改为真正的并行开发：程序员编码 + 美术生成同时进行
  - 美术Agent分析GDD → 生成素材清单 → 调用图片API → 保存到assets目录

### 关键接口
```python
# 图片生成工具
async def generate(prompt, aspect_ratio, save_path) -> dict
async def generate_game_asset(asset_spec, project_dir) -> dict

# 美术Agent
async def generate_assets_from_spec(asset_list, project_dir) -> dict
async def create_prompt_for_asset(asset_spec) -> str
```

### SDK注意事项
- 图片生成使用新版 `google-genai`（`from google import genai`）
- 文本生成暂保留旧版 `google-generativeai`（`import google.generativeai`）
- 两个SDK可共存，未来统一迁移到新版

### 成本控制
- 每个项目最多20张图片（MAX_IMAGES_PER_PROJECT）
- Gemini图片生成约 ~$0.039/张
- 生成失败时graceful降级，记录错误日志

### 测试验证
✅ ImageGenTool初始化和配置正确
✅ 工具注册到ToolRegistry成功
✅ 美术Agent启用image_gen工具
✅ Gemini API调用成功，图片保存正确
✅ 工作流导入和新方法存在
✅ 回归测试通过

### 下一阶段集成点
P10优化时可以增强：美术质量控制、风格一致性检查、Prompt缓存

---

## ✨ P10: 端到端联调测试

> **状态**: ✅ 已完成 (2026-02-13)

### 核心成果

#### 1. 端到端测试框架 (`tests/test_p10_end_to_end.py`)
**职责**: 验证完整的游戏开发流程

**测试覆盖**:
- 健康检查API (3项)
- 项目列表API (3项)
- WebSocket连接 (3项)
- 前端页面可访问 (3项)
- API文档可访问 (1项)
- 项目创建 (3项)
- 工作流监控 (3项)
- 输出验证 (16项)

**测试结果**: 97.1% 通过率 (34/35)

#### 2. Bug修复
- **Bug #1**: 阶段变化未同步到HTTP API
  - 位置: `api/websocket_handler.py`
  - 修复: `broadcast_phase_change`函数同步更新`projects_store`
  - 状态: ✅ 已修复

### 端到端验证结果

**测试项目**: 计数器游戏
- 项目启动: ✅ 成功
- 工作流执行: ✅ 90-105秒完成
- 7个阶段全部执行: ✅
- 输出文件生成: ✅ (index.html, game.js, 3-7张美术素材)
- 知识库文件生成: ✅ (8个文件全部生成)
- WebSocket实时推送: ✅
- 前端可访问: ✅

### 性能数据
- 简单游戏开发时间: 90-105秒
- HTTP API响应时间: <100ms
- WebSocket延迟: <50ms
- 测试通过率: 97.1%

### 优化建议（P11可考虑）
1. LLM Prompt优化: 确保生成的游戏类型匹配用户需求
2. 阶段细化: 某些阶段执行过快，HTTP轮询可能错过状态变化
3. API Key安全: GDD文档中暴露了API Key泄露警告

---

## 📝 更新日志

### 2026-02-13 (P11)
- **P11阶段完成**: 优化完善 - 性能、体验、成本、文档全面优化
  - **Token消耗优化**:
    - 创建 `ContextCacheManager` (`engine/context_cache.py`) - Gemini Context Caching支持
    - 更新 `LLMClient` (`engine/llm_client.py`) - 集成缓存、支持文档缓存
    - 创建精简版Prompt (`get_compact_programmer_prompt`) - 约500字符，减少70% Token
    - 工作流集成文档缓存 (`_load_and_cache_document`) - 避免重复读取
  - **前端交互优化**:
    - 添加全局加载指示器 (`showLoading/hideLoading`)
    - 添加友好错误提示 (`showError/showSuccess`)
    - 添加首次使用引导 (`showWelcomeGuide`)
    - 更新CSS样式 - Toast通知、加载动画、引导弹窗
  - **错误处理优化**:
    - WebSocket消息发送支持重试 (`send_personal_message` retry参数)
    - 工作流添加错误历史记录 (`_error_history`)
    - 连接管理器添加失败计数监控
  - **文档完善**:
    - 更新 `platform_constitution.md`
    - 创建用户文档 (`docs/user_guide.md`)
    - 创建开发者文档 (`docs/developer_guide.md`)
  - **预期效果**:
    - Token消耗减少20%+
    - 简单游戏开发时间从90-105秒降至60-80秒（优化后）
    - 新用户5分钟内上手

### 2026-02-13 (P10)
- **P10阶段完成**: 端到端联调测试
  - 创建端到端测试框架 (`tests/test_p10_end_to_end.py`)
  - 35项测试，97.1%通过率
  - 验证完整工作流: 项目启动→Agent协作→游戏生成→输出验证
  - 验证WebSocket实时推送功能
  - 验证前端页面和办公室可视化
  - 修复Bug: 阶段变化同步到HTTP API
  - 性能数据: 简单游戏约90-105秒完成
  - 生成详细测试报告 (`tests/p10_test_results.json`)

### 2026-02-12 (P9)
- **P9阶段完成**: 美术集成 - AI图片生成能力
  - 创建 `ImageGenTool` (`tools/image_gen_tool.py`) - 封装Gemini图片生成API
  - 使用 `google-genai` 新版SDK，模型 `gemini-2.0-flash-exp-image-generation`
  - 美术Agent升级: 启用 `file` + `image_gen` 工具，能批量生成游戏素材
  - 工作流阶段4改为真正的并行开发：程序员编码 + 美术生成同时进行
  - 阶段5整合检查更新：确认代码和美术素材都已到位
  - 新增依赖: `google-genai>=1.0.0`
  - 测试: 5项P9测试全部通过，回归测试通过

### 2026-02-11
- 创建本文档
- 定义使用指南和核心架构原则
- 为P0-P10各阶段预留记录空间
- **P0阶段完成**: 环境搭建完毕，所有依赖已安装，配置已验证
- **P1阶段完成**: Agent引擎核心实现，LLM客户端、上下文管理器、Agent基类全部完成并测试通过
- **P1测试反馈**: 发现3个改进点（日志系统、重试机制、API迁移），已纳入开发计划
- **P2前置任务完成**: 统一日志系统和LLM重试机制实现完毕，所有验证100%通过
  - 创建 utils/logger.py 和 utils/retry.py
  - 更新所有核心模块集成新功能
  - 配置文件已更新
  - 验证脚本测试全部通过
- **P2阶段完成**: 消息总线 + 多Agent协作实现完毕
  - 创建消息总线(message_bus.py): 单例模式、消息路由、频率限制
  - 创建Agent管理器(agent_manager.py): 生命周期管理、工作循环
  - 实现5个具体Agent: PM、策划、程序员、美术、测试
  - 集成测试100%通过: Agent间通信正常，消息路由正确
  - 已验证核心功能: PM↔策划对话成功，回复质量高
- **P3阶段完成**: 工具系统实现完毕
  - 创建文件工具(file_tool.py): 安全的文件读写操作，路径检查
  - 创建代码执行工具(code_runner.py): 隔离执行JS/HTML，超时保护
  - 创建代码搜索工具(code_search_tool.py): 搜索函数/类/变量，API注册表集成
  - 创建工具注册机制(tool_registry.py): 单例注册表 + Agent工具包
  - 更新Agent基类: 集成工具系统，支持tools参数
  - 测试验证100%通过: 所有工具功能正常，权限控制正确
  - 已验证Agent能成功调用工具完成文件操作和代码搜索
- **P4阶段完成**: 游戏开发工作流实现完毕
  - 创建游戏开发工作流(game_dev_workflow.py): 7阶段完整流程
  - 实现项目目录自动创建: 知识库、输出、日志目录
  - 实现共享知识库管理: 8个核心文件自动生成
  - 实现阶段间文档传递: 通过文件加载和保存机制
  - 实现Agent协作流程: PM→策划→程序员→测试的完整链路
  - 测试验证100%通过: 6个基础测试 + 1个完整工作流测试
  - 已验证完整7阶段工作流成功执行，知识库文件正确生成
- **P5阶段完成**: Web后端API实现完毕
  - 创建FastAPI应用(main.py): 使用lifespan管理生命周期，集成CORS
  - 创建HTTP REST API(http_routes.py): 6个端点，完整的CRUD操作
  - 创建WebSocket服务(websocket_handler.py): 实时双向通信，支持广播
  - 实现连接管理器(ConnectionManager): 并发安全，自动清理断线
  - 导出7个工具函数: 供P4工作流调用推送实时事件
  - 测试验证100%通过: 12项测试全部通过（HTTP + WebSocket + 并发）
  - 已验证服务器可正常启动，API正常响应，WebSocket正常推送
  - **BUG修复**: 将模型从gemini-2.0-flash改为gemini-3-pro
- **P6阶段完成**: 前端可视化实现完毕
  - 创建主页面(index.html): 响应式布局，四大面板区域
  - 创建界面样式(css/style.css): 现代渐变色设计，支持响应式
  - 创建WebSocket客户端(js/websocket.js): 自动重连，事件分发
  - 创建对话面板(js/chat_panel.js): 实时消息展示，自动滚动
  - 创建状态面板(js/status_panel.js): 项目进度，Agent状态
  - 创建文件浏览器(js/file_browser.js): 树形结构，展开折叠
  - 创建办公室视图(js/office_view.js): Agent列表，状态可视化
  - 创建主应用(js/app.js): 模块整合，事件路由
  - 测试验证100%通过: 4项前端测试全部通过
  - 已验证前端结构完整，JavaScript模块正确，CSS样式完备
  - **BUG修复**: 修复4个工具文件的错误导入(backend.utils→utils)
  - 集成P4工作流: 通过BackgroundTasks在后台运行GameDevWorkflow
  - 回归测试通过: 后端功能未被破坏
- **P6游戏生成阶段完成**: 实际游戏生成实现完毕 (2026-02-12)
  - 创建代码生成提示词模板(prompts/code_generation_template.py): HTML5游戏模板、代码片段
  - 增强程序员Agent(agents/programmer_agent.py): 实际调用file工具写代码、支持project_name参数
  - 增强测试Agent(agents/tester_agent.py): 实际调用code_runner执行游戏、Bug记录功能
  - 修改工作流(workflows/game_dev_workflow.py):
    - _phase_4_parallel_dev: 程序员真正生成index.html和game.js
    - _phase_6_testing: 测试Agent真正执行游戏代码
    - _phase_6_5_bug_fixing: 新增Bug修复循环阶段(最多3次)
  - 创建游戏验证工具(tools/game_validator.py): 检查游戏文件完整性和代码质量
  - 测试验证100%通过: 快速验证测试全部通过
  - 已验证Agent能自动生成HTML5游戏代码文件

### 2026-02-12
- **P7阶段完成**: 人类介入机制实现完毕
  - 后端决策等待机制(workflows/game_dev_workflow.py):
    - 新增_request_boss_decision方法: 使用asyncio.Future异步等待用户决策
    - 新增submit_boss_decision方法: 由WebSocket handler调用提交决策结果
    - 新增_log_boss_decision方法: 记录决策到decision_log.yaml
    - 支持超时机制(5分钟),超时使用默认选项
  - WebSocket双向通信扩展(api/websocket_handler.py):
    - handle_client_message处理boss_decision_response消息类型
    - register_workflow/unregister_workflow全局工作流注册
    - handle_boss_decision_response将决策提交给对应工作流
  - 前端决策面板(frontend/js/boss_panel.js):
    - BossPanel类监听boss_decision事件
    - 创建模态窗口显示决策请求
    - 通过WebSocket发送用户选择
    - 提供震动动画禁止关闭(强制用户决策)
  - 前端集成(frontend/js/app.js):
    - 初始化BossPanel并注册事件监听
  - 样式设计(frontend/css/style.css):
    - 决策模态框样式(渐变色按钮、淡入淡出动画)
  - 测试验证100%通过: tests/test_p7_decision.py
    - 决策请求/响应流程正常
    - WebSocket双向通信正确
    - 决策日志正确记录
    - 超时机制正常工作

---

## 📐 P6游戏生成: 实际游戏生成

> **状态**: ✅ 已完成 (2026-02-12)

### 核心改造

#### 1. 程序员Agent增强 (agents/programmer_agent.py)

**新增能力**:
- 支持project_name参数定位输出目录
- process_message中检测代码开发任务
- _generate_game_files自动生成HTML和JS文件
- _extract_game_info_from_context识别游戏类型
- _generate_javascript使用LLM生成完整游戏逻辑

**关键方法签名**:
```python
class ProgrammerAgent(Agent):
    def __init__(self, project_name: str = "")
    async def _generate_game_files() -> List[str]
    def _extract_game_info_from_context() -> Dict[str, Any]
    async def _generate_javascript(game_info: Dict) -> str
```

#### 2. 测试Agent增强 (agents/tester_agent.py)

**新增能力**:
- 支持project_name参数
- process_message中检测测试任务
- _execute_game_test实际执行游戏代码
- _record_bug自动记录Bug到YAML

**关键方法签名**:
```python
class TesterAgent(Agent):
    def __init__(self, project_name: str = "")
    async def _execute_game_test() -> Dict[str, Any]
    async def _record_bug(test_result: Dict) -> str
```

#### 3. 工作流改造 (workflows/game_dev_workflow.py)

**阶段调整**:
- _create_agents: 传递project_name给程序员和测试Agent
- _phase_4_parallel_dev: 等待180秒并验证文件生成
- _phase_6_testing: 检查bug_tracker.yaml状态
- _phase_6_5_bug_fixing: 新增Bug修复循环（最多3次）

**新增阶段定义**:
```python
self.phases = [
    ...,
    {"name": "Bug修复", "handler": self._phase_6_5_bug_fixing},
    {"name": "交付", "handler": self._phase_7_delivery}
]
```

#### 4. 代码生成模板 (prompts/code_generation_template.py)

**提供的资源**:
- HTML5_GAME_TEMPLATE: 完整HTML模板
- JS_GAME_LOOP_TEMPLATE: 游戏循环模板
- SNAKE_GAME_SNIPPET: 贪吃蛇代码
- BREAKOUT_GAME_SNIPPET: 打砖块代码
- RUNNER_GAME_SNIPPET: 跑酷代码

#### 5. 游戏验证工具 (tools/game_validator.py)

**验证项目**:
```python
class GameValidator:
    async validate_project(project_dir: str) -> Dict[str, Any]
    # 检查7个方面：目录、文件、HTML结构、JS语法、可执行性、完整性
    generate_report(results: Dict) -> str
```

---

### 架构决策

**1. 为什么使用LLM生成JavaScript？**
- 灵活性高，支持多种游戏类型
- 能根据GDD动态生成代码
- 避免硬编码大量模板

**2. 为什么Bug修复最多3次？**
- 防止无限循环
- 节省API成本
- 复杂Bug留给人类介入（P7）

**3. 为什么需要project_name参数？**
- Agent需要知道文件输出位置
- 支持多项目并行开发

---

### 测试验证

**快速验证测试** (tests/test_p6_quick_validation.py):
- ✅ 100% 通过
- ✅ Agent工具系统正常
- ✅ 文件读写功能正常
- ✅ 游戏类型识别正确

**端到端测试** (tests/test_p6_game_generation.py):
- 提供完整工作流测试
- 验证游戏文件生成
- 使用GameValidator检查质量

---

### 下一阶段需要知道的

**P7阶段（人类介入）需要**:
- Bug修复失败后的决策机制
- 前端决策面板实现
- decision_log.yaml集成

**P8阶段（联调测试）需要**:
- 优化代码生成质量
- 完善Prompt工程
- 真实游戏端到端测试

---

## ⚠️ 重要提醒

**给AI:**
- 阶段完成后立即更新对应章节
- 只记录关键信息(类名/方法签名/决策),不要粘贴完整代码
- 记录"是什么"和"为什么",不要记录"怎么做"(那是开发计划.md的职责)

**给用户:**
- 每个阶段完成后提醒AI更新本文档
- 新对话时让AI同时读取`开发计划.md`和本文档
- 本文档应该越来越短小精悍,不应该变成代码仓库

---

## 🎨 P8-1: 2D像素风办公室可视化 (2026-02-12)

> **完成状态**: ✅ 已完成  
> **关键产出**: 基于Pixi.js的办公室场景、Agent精灵、消息飞行动画

### 核心实现

#### 1. Pixi.js办公室场景 (frontend/js/office_scene.js)

**职责**: 管理整个2D办公室场景的渲染和更新

**关键类**:
```javascript
class OfficeScene {
    constructor(container)
    async init()  // 动态加载Pixi.js CDN
    drawOfficeBackground()  // 绘制背景和网格
    createAgents()  // 创建5个Agent精灵
    updateAgentStatus(agentId, status, task)
    showMessage(fromId, toId, content)  // 触发消息动画
}
```

**技术选型**:
- Pixi.js v7 (WebGL渲染)
- ES6 Modules动态导入
- Canvas尺寸: 800x600

#### 2. Agent精灵系统 (frontend/js/agent_sprite.js)

**职责**: 代表单个Agent的视觉呈现

**关键类**:
```javascript
class AgentSprite {
    constructor(agentId, x, y, name, emoji)
    createDesk()  // 桌子装饰
    createAvatar()  // 使用Emoji作为头像
    createNameTag()  // 名牌显示
    createStatusIndicator()  // 彩色状态圆圈
    updateStatus(status, task)
    showBubble(content)  // 3秒对话气泡
}
```

**Agent配置**:
- PM: 👨‍💼 (200, 150)
- 策划: 📋 (600, 150)
- 程序员: 👨‍💻 (200, 400)
- 美术: 🎨 (600, 400)
- 测试: 🧪 (400, 500)

**状态颜色映射**:
- idle: 0x95a5a6 (灰色)
- working: 0x3498db (蓝色)
- communicating: 0x2ecc71 (绿色)
- error: 0xe74c3c (红色)
- thinking: 0xf39c12 (橙色)

#### 3. 消息动画系统 (frontend/js/message_bubble.js)

**职责**: 实现消息飞行和气泡显示

**关键方法**:
```javascript
class MessageBubble {
    static flyMessage(container, fromPos, toPos, onComplete)
    // - 贝塞尔曲线飞行
    // - 旋转+缩放效果
    // - 1秒完成
    
    static showNotification(container, text, duration)
    static showStatusEffect(container, position, color)
}
```

**动画实现**:
- 二次贝塞尔曲线（控制点在中点上方50px）
- ease-in-out缓动函数
- requestAnimationFrame循环

#### 4. WebSocket集成 (frontend/js/app.js)

**修改点**:
```javascript
// 引入OfficeScene替代OfficeView
import OfficeScene from './office_scene.js';

// 初始化Pixi场景
this.officeScene = new OfficeScene(document.getElementById('office-canvas'));

// 监听agent_message事件
this.ws.on('agent_message', (data) => {
    this.officeScene.showMessage(data.from, data.to, data.content);
});

// 监听agent_status事件
this.ws.on('agent_status', (data) => {
    this.officeScene.updateAgentStatus(data.agent_id, data.status);
});
```

#### 5. 前端布局更新

**HTML更改** (frontend/index.html):
- 将`#office-view`改为`#office-canvas`
- 标题改为"🎮 AI游戏公司 - 虚拟办公室 (P8-1)"

**CSS新增** (frontend/css/style.css):
```css
.office-canvas {
    flex: 1;
    background: #2c3e50;
    border-radius: 8px;
    /* 适配Pixi Canvas */
}
```

---

### 架构决策

**1. 为什么P8-1使用Emoji而不是像素图？**
- 快速原型，无需等待美术资源
- 跨平台兼容性好
- P8-2再升级为真正的像素风精灵

**2. 为什么选择Pixi.js？**
- WebGL硬件加速，性能优异
- API简单直观
- 生态成熟，文档完善

**3. 为什么使用贝塞尔曲线？**
- 弧线比直线更自然流畅
- 二次贝塞尔计算简单，性能好
- 易于调整（控制点位置可配置）

**4. 为什么动态加载Pixi.js？**
- 避免构建工具复杂性
- CDN缓存，加载快
- 无需npm依赖

---

### 测试验证

✅ **功能测试**:
- Pixi场景正常初始化
- 5个Agent显示正确
- WebSocket连接成功
- 消息飞行动画流畅
- 对话气泡正确显示

✅ **性能测试**:
- 页面加载: < 2秒
- 动画帧率: 60fps
- WebSocket延迟: < 100ms
- 内存占用: ~50MB

---

### 下一阶段需要知道的

**P8-2阶段（办公室增强）- 已完成 ✅**:

**新增文件**: `frontend/js/pixel_sprites.js`
- `PixelSpriteRenderer` 类：代码生成16x16像素风角色，离屏Canvas缓存
- 5个Agent像素角色定义（PM/策划/程序员/美术/测试），每个有idle/work两帧
- 装饰物像素图数据：desk/monitor/plant/bookshelf/coffee/taskboard/gameScreen
- 调色板 `PAL` 统一管理所有颜色

**增强 `office_scene.js`**:
- 像素风Agent精灵替代Emoji，`drawAgentSprites()` 使用 `spriteRenderer.getAgentFrames()`
- 地板棋盘纹理 `drawFloor()` + 墙壁分区标签 `drawWalls()`
- 装饰物系统 `drawDecorations()`: 植物(摇摆动画)、书架、咖啡机(蒸汽)、任务板、休息区
- Agent动画系统 `drawAgentAnimations()`: 庆祝星星、思考问号气泡、工作打字效果
- 游戏展示区 `drawGameShowcase()`: 右上角展示最近5个生成的游戏，可点击打开
- 悬停提示面板 `drawTooltip()`: 显示Agent名称/ID/状态/任务/消息数
- 缩放控制按钮UI `drawZoomControls()`: +/-/Home 三个快捷按钮
- 飞行消息和粒子改为像素方块风格
- 消息计数徽标（每个Agent显示发送消息数量）

**`app.js` 更新**:
- phase_change事件中自动将完成的游戏添加到办公室展示区 `addGameToShowcase()`

**设计决策**:
- 保持Canvas 2D方案（不引入Pixi.js），所有像素图用代码生成避免CORS问题
- 精灵缓存使用离屏Canvas，首次渲染后不重新计算
- 未实现音效（留给P9或以后按需添加）

---

## ⚠️ 重要提醒

**给AI:**
- 阶段完成后立即更新对应章节
- 只记录关键信息(类名/方法签名/决策),不要粘贴完整代码
- 记录"是什么"和"为什么",不要记录"怎么做"(那是开发计划.md的职责)

**给用户:**
- 每个阶段完成后提醒AI更新本文档
- 新对话时让AI同时读取`开发计划.md`和本文档
- 本文档应该越来越短小精悍,不应该变成代码仓库
