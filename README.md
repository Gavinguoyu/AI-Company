# AI 游戏开发公司

> **项目代号**: AI Game Studio  
> **当前版本**: v1.0 (P11 优化完善完成)  
> **最后更新**: 2026-02-13

---

## 🎯 项目简介

这是一个可视化的 **AI 多智能体协作平台**，模拟一家真实的游戏开发公司。

- 🤖 **5 个 AI 员工**：项目经理、策划、程序员、美术、测试
- 💬 **自由交流**：AI 员工之间可以自由对话、协作
- 👀 **实时观察**：在浏览器中看到 AI 公司的运作
- 🎮 **自动开发**：输入创意，AI 自动生成可玩的 HTML5 游戏
- 🎨 **AI美术**：使用 Gemini 图片生成，自动创建游戏素材

---

## 🚀 快速开始

### 1. 环境要求
- Python 3.11+
- Google Gemini API Key

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置API Key
创建 `.env` 文件：
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. 启动服务器
```bash
cd backend
python main.py
```

### 5. 打开浏览器
访问 **http://localhost:8000**

### 6. 创建游戏
1. 点击 **▶ CREATE PROJECT**
2. 填写项目名称和游戏描述
3. 观看AI开发过程
4. 完成后点击 **🎮 PLAY** 试玩

---

## 📊 开发状态

| 阶段 | 状态 | 完成日期 | 关键产出 |
|------|------|---------|---------|
| P0 - 环境搭建 | ✅ 已完成 | 2026-02-11 | 环境配置 |
| P1 - Agent 引擎核心 | ✅ 已完成 | 2026-02-11 | LLM客户端、上下文管理 |
| P2 - 消息总线 + 多 Agent | ✅ 已完成 | 2026-02-11 | 消息路由、5个Agent |
| P3 - 工具系统 | ✅ 已完成 | 2026-02-11 | 文件、代码执行工具 |
| P4 - 游戏开发工作流 | ✅ 已完成 | 2026-02-11 | 7阶段流程 |
| P5 - Web 后端 API | ✅ 已完成 | 2026-02-11 | FastAPI + WebSocket |
| P6 - 前端可视化 | ✅ 已完成 | 2026-02-12 | 办公室场景、状态面板 |
| P7 - 人类介入机制 | ✅ 已完成 | 2026-02-12 | 决策请求、老板面板 |
| P8 - 联调测试 | ✅ 已完成 | 2026-02-12 | 2D像素风办公室 |
| P9 - 美术集成 | ✅ 已完成 | 2026-02-12 | Gemini图片生成 |
| P10 - 端到端测试 | ✅ 已完成 | 2026-02-13 | 端到端测试通过 |
| **P11 - 优化完善** | ✅ **已完成** | **2026-02-13** | **Token优化、体验优化** |

**🎉 项目第一个版本已完成！**

---

## 📚 文档导航

| 文档 | 用途 | 路径 |
|------|------|------|
| 📌 **用户指南** | 快速上手使用 | `docs/user_guide.md` |
| 🔧 **开发者文档** | API、架构、扩展 | `docs/developer_guide.md` |
| 📗 **平台宪法** | 已完成的架构记录 | `docs/platform_constitution.md` |
| 📘 **开发计划** | 项目总纲 | `docs/开发计划.md` |

---

## 🎓 技术栈

### 后端
- Python 3.14
- FastAPI (Web 框架)
- Google Gemini 2.0 Flash (AI 大脑)
- asyncio (异步处理)
- google-genai (图片生成)

### 前端
- HTML5 + CSS + JavaScript
- Canvas 2D (办公室渲染)
- WebSocket (实时通信)

### AI 生成的游戏
- HTML5 + Canvas + JavaScript

---

## 📁 项目结构

```
AI-Company/
├── backend/           # Python 后端
│   ├── engine/        # Agent 引擎核心
│   │   ├── agent.py         # Agent 基类
│   │   ├── llm_client.py    # LLM 客户端
│   │   ├── message_bus.py   # 消息总线
│   │   └── context_cache.py # P11: Context Caching
│   ├── agents/        # 5个具体 Agent
│   ├── tools/         # Agent 工具
│   ├── workflows/     # 游戏开发工作流
│   ├── api/           # HTTP/WebSocket API
│   └── prompts/       # Prompt 模板
│
├── frontend/          # 前端界面
│   ├── js/            # JavaScript 模块
│   └── css/           # 样式
│
├── projects/          # AI 生成的游戏
├── docs/              # 文档
└── tests/             # 测试文件
```

---

## ✨ P11 新特性

### Token 消耗优化
- **Context Caching**: 缓存GDD/TDD等长文档
- **精简版Prompt**: 减少70% Token
- **文档缓存**: 避免重复读取文件

### 前端交互优化
- **加载指示器**: 显示处理状态
- **友好错误提示**: Toast 通知
- **首次使用引导**: 新用户教程

### 稳定性优化
- **WebSocket重试**: 消息发送失败自动重试
- **错误历史记录**: 便于故障排查

---

## 🎮 已验证的游戏类型

- ✅ 计数器游戏
- ✅ 贪吃蛇
- ✅ 打砖块
- ✅ 跑酷游戏
- ✅ 简单互动游戏

---

## 📞 获取帮助

- **用户指南**: `docs/user_guide.md`
- **开发者文档**: `docs/developer_guide.md`
- **API 文档**: http://localhost:8000/api/docs

---

## 🎉 里程碑

- ✅ 2026-02-11: P0-P4 核心 Framework 完成
- ✅ 2026-02-12: P5-P9 前端与集成完成
- ✅ 2026-02-13: P10 端到端测试通过
- ✅ 2026-02-13: **P11 优化完善完成 - v1.0 发布！**

---

**项目启动日期**: 2026-02-11  
**当前版本**: v1.0 (P11 完成)  
**状态**: 🎉 **可演示版本！**
