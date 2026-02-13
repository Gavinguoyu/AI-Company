# P6阶段完成 - 快速使用指南

## 🎉 P6阶段已完成！

AI Agent现在可以**真正生成可玩的游戏**了！

---

## 🚀 快速测试

### 方式1: 运行快速验证测试（推荐）

```bash
python tests/test_p6_quick_validation.py
```

**预期结果**: 所有测试项显示 ✅，耗时约5秒

**测试内容**:
- 验证程序员Agent可以写文件
- 验证测试Agent可以执行代码
- 验证游戏类型识别功能

---

### 方式2: 运行完整端到端测试（需要API）

```bash
python tests/test_p6_game_generation.py
```

**预期结果**: 生成完整的游戏文件，耗时约3-5分钟

**注意**: 需要配置Gemini API Key（在.env文件中）

**测试流程**:
1. 创建测试项目 "test_snake_p6"
2. 执行完整的8阶段工作流
3. 生成游戏文件到 `projects/test_snake_p6/output/`
4. 验证游戏文件完整性

---

## 🎮 生成的游戏在哪里？

游戏文件位置: `projects/{项目名}/output/`

例如测试项目: `projects/test_snake_p6/output/index.html`

**如何玩游戏**:
1. 用浏览器打开 `index.html`
2. 点击"开始游戏"按钮
3. 使用方向键控制（贪吃蛇）

---

## 📁 生成的文件结构

```
projects/test_snake_p6/
├── output/
│   ├── index.html    # 游戏入口（用浏览器打开这个文件）
│   └── game.js       # 游戏逻辑代码
├── shared_knowledge/
│   ├── game_design_doc.md
│   ├── tech_design_doc.md
│   ├── bug_tracker.yaml
│   └── ... (其他知识库文件)
└── logs/
    └── ... (工作流日志)
```

---

## 🔧 核心改进

### 1. 程序员Agent现在能：
- ✅ 识别游戏类型（贪吃蛇、打砖块、跑酷等）
- ✅ 自动生成HTML和JavaScript代码
- ✅ 调用file工具实际写入文件
- ✅ 修复测试发现的Bug

### 2. 测试Agent现在能：
- ✅ 读取游戏文件
- ✅ 执行JavaScript代码
- ✅ 检测语法错误
- ✅ 记录Bug到bug_tracker.yaml

### 3. 工作流现在包括：
- ✅ 8个阶段（新增Bug修复阶段）
- ✅ 自动Bug修复循环（最多3次）
- ✅ 完整的文件生成和测试流程

---

## 📊 新增的文件

### 核心功能文件
- `backend/prompts/code_generation_template.py` - 游戏代码模板
- `backend/tools/game_validator.py` - 游戏验证工具

### 增强的文件
- `backend/agents/programmer_agent.py` - 增强代码生成能力
- `backend/agents/tester_agent.py` - 增强测试执行能力
- `backend/workflows/game_dev_workflow.py` - 新增Bug修复阶段

### 测试文件
- `tests/test_p6_quick_validation.py` - 快速验证测试
- `tests/test_p6_game_generation.py` - 端到端测试

---

## 🎯 如何创建自己的游戏项目？

### 通过后端API（需要先启动后端）

1. 启动后端:
```bash
cd backend
python main.py
```

2. 创建项目（使用curl或Postman）:
```bash
curl -X POST http://localhost:8000/api/project/start \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my_game",
    "description": "做一个简单的贪吃蛇游戏"
  }'
```

3. 等待工作流完成（约3-5分钟）

4. 在浏览器打开: `projects/my_game/output/index.html`

---

### 直接使用Python脚本

```python
import asyncio
from backend.workflows.game_dev_workflow import GameDevWorkflow

async def create_game():
    workflow = GameDevWorkflow(
        project_name="my_snake_game",
        project_description="做一个贪吃蛇游戏，用方向键控制"
    )
    await workflow.start()

asyncio.run(create_game())
```

---

## 🐛 常见问题

### Q: 测试提示"工具未注册"？
A: 确保在创建Agent前先注册工具:
```python
from tools.tool_registry import ToolRegistry
from tools.file_tool import FileTool
# ...其他导入

registry = ToolRegistry()
registry.register_tool("file", FileTool())
# ...注册其他工具
```

### Q: 生成的游戏文件是空的？
A: 检查:
1. Gemini API Key是否配置正确
2. 查看日志确认程序员Agent是否执行了_generate_game_files
3. 确认project_name参数是否正确传递

### Q: 游戏在浏览器中打不开？
A: 检查:
1. 文件路径是否正确
2. 使用GameValidator验证游戏文件
3. 查看浏览器控制台的JavaScript错误

### Q: Bug修复循环一直在执行？
A: Bug修复循环最多执行3次，然后会自动结束。如果仍有Bug，可以:
1. 查看bug_tracker.yaml了解Bug详情
2. 手动修改代码
3. 等待P7人类介入机制实现

---

## 📚 相关文档

- **详细报告**: `docs/reports/P6_game_generation_report.md`
- **开发指引**: `docs/stage_guides/P6_指引.md`
- **平台架构**: `docs/platform_constitution.md`

---

## 🎊 下一步

P7阶段将实现**人类介入机制**，允许老板在关键节点做出决策！

---

**文档版本**: v1.0  
**更新日期**: 2026-02-12
