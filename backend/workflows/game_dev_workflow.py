"""
文件: workflows/game_dev_workflow.py
职责: 游戏开发工作流 - 定义完整的7个阶段流程
依赖: engine/agent_manager.py, tools/file_tool.py
被依赖: api/http_routes.py (未来P5实现)

关键接口:
  - GameDevWorkflow(project_name, project_description) - 创建工作流
  - async start() - 启动工作流
  - async get_status() - 获取当前状态
"""

import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys
from datetime import datetime
import uuid

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from config import Config
from engine.agent_manager import AgentManager
from engine.message_bus import MessageBus
from tools.file_tool import FileTool
from agents.pm_agent import PMAgent
from agents.planner_agent import PlannerAgent
from agents.programmer_agent import ProgrammerAgent
from agents.artist_agent import ArtistAgent
from agents.tester_agent import TesterAgent
from utils.logger import setup_logger

# 导入工具类用于注册
from tools.code_runner import CodeRunner
from tools.code_search_tool import CodeSearchTool
from tools.image_gen_tool import ImageGenTool
from tools.tool_registry import ToolRegistry

# 导入WebSocket广播函数（延迟导入以避免循环依赖）
from api.websocket_handler import (
    broadcast_agent_message,
    broadcast_agent_status,
    broadcast_phase_change,
    request_boss_decision,
    broadcast_agent_output
)


class GameDevWorkflow:
    """
    游戏开发工作流
    
    实现完整的7个阶段:
    1. 立项 - PM接收需求
    2. 策划 - 策划编写GDD
    3. 技术设计 - 程序员设计架构
    4. 并行开发 - 程序员+美术同时工作
    5. 整合 - 程序员整合代码和素材
    6. 测试 - 测试运行游戏
    7. 交付 - PM汇报项目完成
    """
    
    def __init__(self, project_name: str, project_description: str):
        """
        初始化工作流
        
        Args:
            project_name: 项目名称（如"snake_game"）
            project_description: 项目描述（用户输入的需求）
        """
        self.project_name = project_name
        self.project_description = project_description
        self.current_phase = 0
        self.status = "未开始"
        
        # 项目目录
        self.project_dir = Config.PROJECTS_DIR / project_name
        self.knowledge_base_dir = self.project_dir / "shared_knowledge"
        self.output_dir = self.project_dir / "output"
        self.logs_dir = self.project_dir / "logs"
        
        # 核心组件
        self.agent_manager = AgentManager()
        self.message_bus = MessageBus()
        self.file_tool = FileTool()
        
        # 日志器
        self.logger = setup_logger(f"workflow_{project_name}")
        
        # Agent 实例
        self.agents: Dict[str, Any] = {}
        
        # 决策等待存储 - 存储待决策的请求和结果
        self.pending_decisions: Dict[str, asyncio.Future] = {}
        
        # 阶段定义
        self.phases = [
            {"name": "立项", "handler": self._phase_1_initiation},
            {"name": "策划", "handler": self._phase_2_planning},
            {"name": "技术设计", "handler": self._phase_3_tech_design},
            {"name": "并行开发", "handler": self._phase_4_parallel_dev},
            {"name": "整合", "handler": self._phase_5_integration},
            {"name": "测试", "handler": self._phase_6_testing},
            {"name": "Bug修复", "handler": self._phase_6_5_bug_fixing},
            {"name": "交付", "handler": self._phase_7_delivery}
        ]
        
        self.logger.info(f"工作流初始化成功: {project_name}")
    
    async def _register_global_tools(self):
        """注册全局工具到工具注册表"""
        self.logger.info("注册全局工具...")
        
        # 获取工具注册表单例
        registry = ToolRegistry()
        
        # 注册file工具（使用已有的self.file_tool）
        registry.register_tool("file", self.file_tool)
        self.logger.info("  ✓ file工具已注册")
        
        # 注册code_runner工具
        code_runner = CodeRunner()
        registry.register_tool("code_runner", code_runner)
        self.logger.info("  ✓ code_runner工具已注册")
        
        # 注册code_search工具
        code_search = CodeSearchTool()
        registry.register_tool("code_search", code_search)
        self.logger.info("  ✓ code_search工具已注册")
        
        # 注册图片生成工具（P9新增 - Gemini 2.5 Flash Image）
        image_gen = ImageGenTool()
        registry.register_tool("image_gen", image_gen)
        self.logger.info("  ✓ image_gen工具已注册")
        
        self.logger.info("全局工具注册完成")
        
        # 让workflow自己也订阅消息总线，用于接收Agent的回复
        self.message_bus.subscribe("workflow", lambda msg: None)  # 不需要回调，只需要队列
        self.logger.info("  ✓ workflow已订阅消息总线")
    
    def _create_task_message(self, to: str, content: str, context: str, priority: str = "normal") -> Dict:
        """
        创建任务消息的辅助函数
        
        Args:
            to: 目标Agent ID
            content: 消息内容
            context: 工作上下文
            priority: 优先级
        
        Returns:
            消息字典
        """
        return {
            "from": "pm",
            "to": to,
            "type": "request_review",
            "content": content,
            "context": context,
            "priority": priority,
            "reply_to": "workflow",  # 回复给workflow而不是pm
            "timestamp": datetime.now().isoformat()
        }
    
    async def initialize(self):
        """初始化工作流环境"""
        self.logger.info("开始初始化工作流环境...")
        
        # 0. 先注册全局工具（关键！）
        await self._register_global_tools()
        
        # 1. 创建项目目录结构
        await self._create_project_structure()
        
        # 2. 创建和注册所有Agent
        await self._create_agents()
        
        # 3. 启动Agent管理器
        await self.agent_manager.start_all()
        
        # 4. 订阅消息总线的WebSocket推送
        self.logger.info("🔧 准备设置WebSocket集成...")
        try:
            await self._setup_websocket_integration()
            self.logger.info("🔧 WebSocket集成设置完成")
        except Exception as e:
            self.logger.error(f"🔧 WebSocket集成设置失败: {e}", exc_info=True)
        
        self.logger.info("工作流环境初始化完成")
    
    async def _create_project_structure(self):
        """创建项目目录结构"""
        self.logger.info("创建项目目录结构...")
        
        # 创建主要目录
        directories = [
            self.project_dir,
            self.knowledge_base_dir,
            self.output_dir,
            self.output_dir / "js",
            self.output_dir / "assets",
            self.output_dir / "css",
            self.logs_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"  ✓ {directory.relative_to(Config.PROJECTS_DIR)}")
        
        # 创建初始知识库文件
        await self._create_initial_knowledge_base()
        
        self.logger.info("项目目录结构创建完成")
    
    async def _create_initial_knowledge_base(self):
        """创建初始共享知识库文件"""
        self.logger.info("创建初始知识库文件...")
        
        # 1. project_rules.yaml - 项目规范
        project_rules = f"""# 项目规范
# ==========================================
# 项目名称: {self.project_name}
# 创建时间: {datetime.now().isoformat()}
# ==========================================

项目信息:
  名称: {self.project_name}
  描述: {self.project_description}
  技术栈: HTML5 + Canvas + JavaScript
  目标平台: 浏览器
  
命名规范:
  文件名: 小写字母和下划线（如: snake_game.js）
  类名: 大驼峰（如: SnakeGame）
  函数名: 小驼峰（如: moveSnake）
  变量名: 小驼峰（如: currentScore）
  常量名: 全大写下划线（如: MAX_SPEED）
  
文件结构:
  入口文件: index.html
  脚本目录: js/
  素材目录: assets/
  样式目录: css/
  
代码规范:
  - 所有数值配置必须从config.js读取，禁止硬编码
  - 新建函数前必须先查api_registry.yaml，避免重复
  - 所有文件必须有文件头注释说明职责
  - 函数必须有注释说明参数和返回值
  
美术规范:
  风格: 像素风
  图片格式: PNG（透明背景）
  命名: 小写字母下划线（如: player_sprite.png）
"""
        
        await self.file_tool.write(
            str(self.knowledge_base_dir / "project_rules.yaml"),
            project_rules
        )
        
        # 2. game_design_doc.md - 游戏策划文档（占位）
        await self.file_tool.write(
            str(self.knowledge_base_dir / "game_design_doc.md"),
            f"# {self.project_name} 游戏策划文档\n\n待策划填写...\n"
        )
        
        # 3. tech_design_doc.md - 技术设计文档（占位）
        await self.file_tool.write(
            str(self.knowledge_base_dir / "tech_design_doc.md"),
            f"# {self.project_name} 技术设计文档\n\n待程序员填写...\n"
        )
        
        # 4. api_registry.yaml - 接口注册表（空）
        api_registry = f"""# API接口注册表
# ==========================================
# 项目名称: {self.project_name}
# 说明: 程序员写代码前【必须】查阅此表
#       写完代码后【必须】更新此表
# ==========================================

最后更新时间: {datetime.now().isoformat()}
更新人: 待定

模块列表: []
"""
        
        await self.file_tool.write(
            str(self.knowledge_base_dir / "api_registry.yaml"),
            api_registry
        )
        
        # 5. config_tables.yaml - 配置表（空）
        await self.file_tool.write(
            str(self.knowledge_base_dir / "config_tables.yaml"),
            f"# 游戏配置表\n# 项目名称: {self.project_name}\n\n配置: {{}}\n"
        )
        
        # 6. art_asset_list.yaml - 美术素材清单（空）
        await self.file_tool.write(
            str(self.knowledge_base_dir / "art_asset_list.yaml"),
            f"# 美术素材清单\n# 项目名称: {self.project_name}\n\n素材列表: []\n"
        )
        
        # 7. bug_tracker.yaml - Bug追踪器（空）
        await self.file_tool.write(
            str(self.knowledge_base_dir / "bug_tracker.yaml"),
            f"# Bug追踪器\n# 项目名称: {self.project_name}\n\nBug列表: []\n"
        )
        
        # 8. decision_log.yaml - 决策日志（空）
        await self.file_tool.write(
            str(self.knowledge_base_dir / "decision_log.yaml"),
            f"# 老板决策日志\n# 项目名称: {self.project_name}\n\n决策记录: []\n"
        )
        
        self.logger.info("知识库文件创建完成")
    
    async def _create_agents(self):
        """创建和注册所有Agent"""
        self.logger.info("创建和注册Agent...")
        
        # 创建5个Agent实例（传入project_name以便Agent能写文件到正确位置）
        self.agents["pm"] = PMAgent()
        self.agents["planner"] = PlannerAgent()
        self.agents["programmer"] = ProgrammerAgent(project_name=self.project_name)
        self.agents["artist"] = ArtistAgent()
        self.agents["tester"] = TesterAgent(project_name=self.project_name)
        
        # 注册到Agent管理器
        for agent_id, agent in self.agents.items():
            self.agent_manager.register_agent(agent)
            self.logger.info(f"  ✓ {agent.role} ({agent_id})")
        
        self.logger.info(f"已注册 {len(self.agents)} 个Agent")
    
    async def _setup_websocket_integration(self):
        """设置WebSocket集成，将消息总线的消息推送到前端"""
        self.logger.info("设置WebSocket集成...")
        
        # 创建WebSocket回调函数
        async def websocket_callback(message: Dict[str, Any]):
            """
            当消息总线发送消息时，自动推送到WebSocket
            
            Args:
                message: 消息总线的消息字典
            """
            try:
                # 推送Agent消息到前端
                await broadcast_agent_message(
                    project_id=self.project_name,
                    from_agent=message.get('from', 'unknown'),
                    to_agent=message.get('to', 'unknown'),
                    message_type=message.get('type', 'message'),
                    content=message.get('content', ''),
                    context=message.get('context', '')
                )
                
                # 更新发送者Agent状态为"工作中"
                if message.get('from') and message.get('from') != 'boss':
                    await broadcast_agent_status(
                        project_id=self.project_name,
                        agent_id=message.get('from'),
                        status='working',
                        current_task=f"发送消息给 {message.get('to', 'unknown')}"
                    )
                
            except Exception as e:
                self.logger.error(f"WebSocket推送失败: {e}", exc_info=True)
        
        # 订阅消息总线
        self.message_bus.subscribe_websocket(websocket_callback)
        
        self.logger.info("✓ WebSocket集成已完成")
    
    async def start(self):
        """启动工作流"""
        self.logger.info("="*60)
        self.logger.info(f"启动游戏开发工作流: {self.project_name}")
        self.logger.info("="*60)
        
        self.status = "运行中"
        
        try:
            # 初始化环境
            await self.initialize()
            
            # 逐个执行7个阶段
            for i, phase in enumerate(self.phases):
                old_phase = self.phases[self.current_phase - 1]["name"] if self.current_phase > 0 else "未开始"
                self.current_phase = i + 1
                new_phase = phase['name']
                progress = (self.current_phase / len(self.phases)) * 100
                
                self.logger.info("")
                self.logger.info("="*60)
                self.logger.info(f"阶段 {self.current_phase}/{len(self.phases)}: {new_phase}")
                self.logger.info("="*60)
                
                # 广播阶段变化到前端
                await broadcast_phase_change(
                    project_id=self.project_name,
                    old_phase=old_phase,
                    new_phase=new_phase,
                    progress=progress
                )
                
                # 执行阶段处理函数
                await phase["handler"]()
                
                self.logger.info(f"✅ 阶段 {self.current_phase} 完成: {new_phase}")
            
            self.status = "已完成"
            self.logger.info("")
            self.logger.info("="*60)
            self.logger.info("🎉 工作流执行完成！")
            self.logger.info("="*60)
            
            # 广播最终阶段变化（100%完成）
            await broadcast_phase_change(
                project_id=self.project_name,
                old_phase=self.phases[-1]["name"],
                new_phase="完成",
                progress=100.0
            )
            
            # 更新所有Agent状态为空闲
            for agent_id in self.agents.keys():
                await broadcast_agent_status(
                    project_id=self.project_name,
                    agent_id=agent_id,
                    status="idle",
                    current_task="项目已完成"
                )
            
        except Exception as e:
            self.status = "失败"
            self.logger.error(f"工作流执行失败: {e}", exc_info=True)
            
            # 广播错误到前端
            from api.websocket_handler import broadcast_error_alert
            await broadcast_error_alert(
                project_id=self.project_name,
                error_type="workflow_error",
                error_message=str(e)
            )
            
            # 更新所有Agent状态为空闲
            for agent_id in self.agents.keys():
                await broadcast_agent_status(
                    project_id=self.project_name,
                    agent_id=agent_id,
                    status="idle",
                    current_task=""
                )
            
            raise
        finally:
            # 停止所有Agent
            await self.agent_manager.stop_all()
    
    async def _phase_1_initiation(self):
        """阶段1: 立项 - PM接收需求"""
        self.logger.info("PM接收项目需求并组织全员会议...")
        
        # 广播PM状态：开始工作
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="working",
            current_task="接收并分析项目需求"
        )
        
        # PM接收需求
        pm = self.agents["pm"]
        
        # 给PM加载项目规范
        project_rules = await self.file_tool.read(
            str(self.knowledge_base_dir / "project_rules.yaml")
        )
        pm.load_file_to_context("project_rules.yaml", project_rules)
        
        # PM分析需求（使用_create_task_message确保reply_to=workflow）
        message = self._create_task_message(
            to="pm",
            content=f"我想做一个游戏：{self.project_description}。请分析需求并拆解为具体任务。",
            context="项目立项"
        )
        # 标记来自boss
        message["from"] = "boss"
        
        # 发送消息给PM
        await self.message_bus.send(message)
        
        # 等待PM回复
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="thinking",
            current_task="正在分析需求并拆解任务..."
        )
        
        response = await self._wait_for_response("pm", timeout=90.0)
        
        if response:
            self.logger.info(f"PM回复: {response['content'][:200]}...")
        
        # PM组织全员会议（广播）
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="working",
            current_task="组织全员会议"
        )
        
        meeting_message = {
            "from": "pm",
            "to": "all",
            "type": "report",
            "content": f"项目启动！项目名称: {self.project_name}。需求: {self.project_description}",
            "context": "全员会议",
            "priority": "normal",
            "timestamp": datetime.now().isoformat()
        }
        
        await self.message_bus.send(meeting_message)
        await asyncio.sleep(2)  # 等待消息传递
        
        # PM任务完成，状态更新为空闲
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="idle",
            current_task=""
        )
        
        # 【决策点1】立项确认 - PM分析完需求后,请求老板确认项目方向
        self.logger.info("🤔 请求老板决策: 立项确认")
        decision = await self._request_boss_decision(
            title="项目立项确认",
            question=f"PM已分析需求并拆解任务,是否确认项目方向?\n\n项目名称: {self.project_name}\n需求描述: {self.project_description}",
            options=["确认,开始策划", "修改需求", "取消项目"],
            context={"phase": "initiation", "project_name": self.project_name}
        )
        
        if decision == "取消项目":
            self.logger.error("❌ 老板取消了项目")
            raise Exception("老板取消了项目")
        elif decision == "修改需求":
            self.logger.warning("⚠️ 老板要求修改需求,但当前版本不支持重新立项,将继续执行")
            # TODO: 未来版本可以实现重新走立项流程
    
    async def _phase_2_planning(self):
        """阶段2: 策划 - 策划编写GDD"""
        self.logger.info("策划开始编写游戏策划文档...")
        
        # 广播策划状态：开始工作
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="planner",
            status="working",
            current_task="准备编写游戏策划文档"
        )
        
        planner = self.agents["planner"]
        
        # 加载项目规范
        project_rules = await self.file_tool.read(
            str(self.knowledge_base_dir / "project_rules.yaml")
        )
        planner.load_file_to_context("project_rules.yaml", project_rules)
        
        # PM分配任务给策划
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="working",
            current_task="分配任务给策划"
        )
        
        task_message = self._create_task_message(
            to="planner",
            content=f"请编写游戏策划文档(GDD)和配置表。游戏需求: {self.project_description}",
            context="策划阶段"
        )
        
        await self.message_bus.send(task_message)
        
        # PM任务完成
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="idle",
            current_task=""
        )
        
        # 策划开始思考
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="planner",
            status="thinking",
            current_task="正在编写游戏策划文档..."
        )
        
        # 等待策划回复
        response = await self._wait_for_response("planner", timeout=90.0)
        
        if response:
            self.logger.info(f"策划回复: {response['content'][:200]}...")
            
            # 策划正在保存文档
            await broadcast_agent_status(
                project_id=self.project_name,
                agent_id="planner",
                status="working",
                current_task="保存游戏策划文档"
            )
            
            # 提取策划文档内容（简化版：让策划直接生成）
            # TODO: 未来可以改进为解析LLM回复中的文档内容
            gdd_content = f"""# {self.project_name} 游戏策划文档

## 1. 游戏概述
{self.project_description}

## 2. 核心玩法
{response['content']}

## 3. 技术要求
- 技术栈: HTML5 + Canvas + JavaScript
- 平台: 浏览器
- 风格: 像素风

## 4. 配置说明
详见 config_tables.yaml

---
文档版本: 1.0
创建时间: {datetime.now().isoformat()}
创建人: 策划Agent
"""
            
            # 保存GDD
            await self.file_tool.write(
                str(self.knowledge_base_dir / "game_design_doc.md"),
                gdd_content
            )
            
            self.logger.info("✓ 游戏策划文档已保存")
            
            # 广播产出事件
            await broadcast_agent_output(
                project_id=self.project_name,
                agent_id="planner",
                file_path="shared_knowledge/game_design_doc.md",
                file_type="document",
                summary="游戏策划文档(GDD)已完成"
            )
            
            # 策划任务完成
            await broadcast_agent_status(
                project_id=self.project_name,
                agent_id="planner",
                status="idle",
                current_task=""
            )
        
        # 【决策点2】策划审批 - 策划文档完成后,请求老板审批
        self.logger.info("🤔 请求老板决策: 策划审批")
        decision = await self._request_boss_decision(
            title="策划文档审批",
            question=f"策划已完成游戏策划文档(GDD),是否批准进入技术设计阶段?\n\n游戏名称: {self.project_name}\nGDD已保存至: shared_knowledge/game_design_doc.md",
            options=["批准,进入技术设计", "需要修改策划"],
            context={"phase": "planning", "gdd_path": str(self.knowledge_base_dir / "game_design_doc.md")}
        )
        
        if decision == "需要修改策划":
            self.logger.warning("⚠️ 老板要求修改策划,但当前版本不支持重新策划,将继续执行")
            # TODO: 未来版本可以让策划重新编写
    
    async def _phase_3_tech_design(self):
        """阶段3: 技术设计 - 程序员设计架构"""
        self.logger.info("程序员开始设计技术架构...")
        
        # 广播程序员状态：开始工作
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="programmer",
            status="working",
            current_task="准备设计技术架构"
        )
        
        programmer = self.agents["programmer"]
        
        # 加载相关文档
        project_rules = await self.file_tool.read(
            str(self.knowledge_base_dir / "project_rules.yaml")
        )
        gdd = await self.file_tool.read(
            str(self.knowledge_base_dir / "game_design_doc.md")
        )
        
        programmer.load_file_to_context("project_rules.yaml", project_rules)
        programmer.load_file_to_context("game_design_doc.md", gdd)
        
        # PM分配任务
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="working",
            current_task="分配技术设计任务给程序员"
        )
        
        task_message = self._create_task_message(
            to="programmer",
            content="请根据策划文档设计技术架构，确定文件结构和模块划分，并更新api_registry.yaml",
            context="技术设计阶段"
        )
        
        await self.message_bus.send(task_message)
        
        # PM任务完成
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="idle",
            current_task=""
        )
        
        # 程序员开始思考
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="programmer",
            status="thinking",
            current_task="正在设计技术架构..."
        )
        
        # 等待程序员回复
        response = await self._wait_for_response("programmer", timeout=90.0)
        
        if response:
            self.logger.info(f"程序员回复: {response['content'][:200]}...")
            
            # 程序员正在保存文档
            await broadcast_agent_status(
                project_id=self.project_name,
                agent_id="programmer",
                status="working",
                current_task="保存技术设计文档"
            )
            
            # 保存技术设计文档
            tdd_content = f"""# {self.project_name} 技术设计文档

## 1. 架构设计
{response['content']}

## 2. 文件结构
```
output/
├── index.html      # 入口文件
├── js/             # JavaScript文件
│   ├── game.js     # 主游戏逻辑
│   └── config.js   # 配置文件
├── assets/         # 美术素材
└── css/            # 样式文件
```

## 3. 模块划分
详见 api_registry.yaml

---
文档版本: 1.0
创建时间: {datetime.now().isoformat()}
创建人: 程序员Agent
"""
            
            await self.file_tool.write(
                str(self.knowledge_base_dir / "tech_design_doc.md"),
                tdd_content
            )
            
            self.logger.info("✓ 技术设计文档已保存")
            
            # 广播产出事件
            await broadcast_agent_output(
                project_id=self.project_name,
                agent_id="programmer",
                file_path="shared_knowledge/tech_design_doc.md",
                file_type="document",
                summary="技术设计文档(TDD)已完成"
            )
            
            # 程序员任务完成
            await broadcast_agent_status(
                project_id=self.project_name,
                agent_id="programmer",
                status="idle",
                current_task=""
            )
    
    async def _phase_4_parallel_dev(self):
        """阶段4: 并行开发 - 程序员+美术同时工作"""
        self.logger.info("程序员和美术并行开发...")
        
        # P9版本: 程序员生成代码文件 + 美术Agent生成图片素材
        # 两者并行执行，提高效率
        
        # 并行启动程序员编码和美术生成
        programmer_task = asyncio.create_task(
            self._phase_4_programmer_coding()
        )
        artist_task = asyncio.create_task(
            self._phase_4_artist_assets()
        )
        
        # 等待两者都完成
        await asyncio.gather(programmer_task, artist_task)
        
        # 【决策点3】开发验收 - 代码和素材生成完成后,请求老板验收
        self.logger.info("🤔 请求老板决策: 开发验收")
        
        # 检查文件生成情况
        html_exists = (self.output_dir / "index.html").exists()
        js_exists = (self.output_dir / "game.js").exists()
        assets_dir = self.output_dir / "assets"
        asset_count = len(list(assets_dir.glob("*.png"))) if assets_dir.exists() else 0
        
        file_status = (
            f"HTML文件: {'✅已生成' if html_exists else '❌未生成'}\n"
            f"JS文件: {'✅已生成' if js_exists else '❌未生成'}\n"
            f"美术素材: {asset_count}张图片已生成"
        )
        
        decision = await self._request_boss_decision(
            title="开发阶段验收",
            question=f"程序员和美术已完成开发,是否进入测试阶段?\n\n{file_status}\n输出目录: {self.output_dir}",
            options=["进入测试", "先让我看看代码"],
            context={"phase": "development", "output_dir": str(self.output_dir)}
        )
        
        if decision == "先让我看看代码":
            self.logger.info("⏸️ 老板选择先查看代码,等待5秒后继续...")
            await asyncio.sleep(5)  # 给老板时间查看
    
    async def _phase_4_programmer_coding(self):
        """阶段4子任务: 程序员编码"""
        # 广播程序员状态：开始编码
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="programmer",
            status="working",
            current_task="准备编写游戏代码"
        )
        
        programmer = self.agents["programmer"]
        
        # 加载所有必要文档
        files_to_load = [
            "project_rules.yaml",
            "game_design_doc.md",
            "tech_design_doc.md",
            "api_registry.yaml",
            "config_tables.yaml"
        ]
        
        for filename in files_to_load:
            content = await self.file_tool.read(
                str(self.knowledge_base_dir / filename)
            )
            programmer.load_file_to_context(filename, content)
        
        # PM分配编码任务
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="working",
            current_task="分配编码任务给程序员"
        )
        
        task_message = self._create_task_message(
            to="programmer",
            content=f"请根据设计文档编写游戏代码。游戏描述: {self.project_description}。请生成index.html和game.js文件。",
            context="开发阶段"
        )
        
        await self.message_bus.send(task_message)
        
        # PM任务完成
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="idle",
            current_task=""
        )
        
        # 程序员开始编码
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="programmer",
            status="thinking",
            current_task="正在编写游戏代码..."
        )
        
        # 等待程序员回复（增加超时时间因为要生成代码）
        response = await self._wait_for_response("programmer", timeout=180.0)
        
        if response:
            self.logger.info(f"程序员回复: {response['content'][:200]}...")
            
            # 检查代码文件是否已生成
            html_path = self.output_dir / "index.html"
            js_path = self.output_dir / "game.js"
            
            if html_path.exists() and js_path.exists():
                self.logger.info("✅ 游戏代码文件已生成")
                self.logger.info(f"  - {html_path}")
                self.logger.info(f"  - {js_path}")
                
                # 广播产出事件
                await broadcast_agent_output(
                    project_id=self.project_name,
                    agent_id="programmer",
                    file_path="output/index.html",
                    file_type="code",
                    summary="游戏入口HTML文件"
                )
                await broadcast_agent_output(
                    project_id=self.project_name,
                    agent_id="programmer",
                    file_path="output/game.js",
                    file_type="code",
                    summary="游戏主逻辑代码"
                )
            else:
                self.logger.warning("⚠️ 游戏代码文件未完全生成")
            
            # 程序员任务完成
            await broadcast_agent_status(
                project_id=self.project_name,
                agent_id="programmer",
                status="idle",
                current_task=""
            )
    
    async def _phase_4_artist_assets(self):
        """阶段4子任务: 美术素材生成（P9新增）"""
        self.logger.info("🎨 美术Agent开始生成游戏素材...")
        
        # 广播美术状态
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="artist",
            status="working",
            current_task="分析策划文档,准备生成美术素材"
        )
        
        artist = self.agents["artist"]
        
        # 加载策划文档供美术Agent参考
        try:
            gdd_content = await self.file_tool.read(
                str(self.knowledge_base_dir / "game_design_doc.md")
            )
            artist.load_file_to_context("game_design_doc.md", gdd_content)
            
            rules_content = await self.file_tool.read(
                str(self.knowledge_base_dir / "project_rules.yaml")
            )
            artist.load_file_to_context("project_rules.yaml", rules_content)
        except Exception as e:
            self.logger.warning(f"加载策划文档失败: {e}")
        
        # 让美术Agent分析需要哪些素材
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="artist",
            status="thinking",
            current_task="分析游戏需要的美术素材..."
        )
        
        asset_analysis = await artist.think_and_respond(
            f"""请根据游戏策划文档，列出这个游戏需要的核心美术素材。
游戏描述: {self.project_description}

请按以下JSON格式列出（最多6个核心素材，优先列出最重要的）:
[
    {{"name": "素材英文名", "description": "描述(中文)", "style": "pixel art"}},
    ...
]

只输出JSON数组，不要其他内容。"""
        )
        
        # 解析素材清单
        asset_list = self._parse_asset_list(asset_analysis)
        
        if not asset_list:
            self.logger.warning("⚠️ 美术Agent未能生成素材清单，使用默认素材")
            asset_list = self._get_default_asset_list()
        
        self.logger.info(f"素材清单: {len(asset_list)}个素材待生成")
        
        # 广播状态：开始生成
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="artist",
            status="working",
            current_task=f"正在生成{len(asset_list)}个游戏素材..."
        )
        
        # 批量生成素材
        project_dir = str(self.project_dir)
        result = await artist.generate_assets_from_spec(
            asset_list=asset_list,
            project_dir=project_dir
        )
        
        # 广播每个成功的素材
        for asset in result.get("assets", []):
            if asset.get("success") and asset.get("path"):
                await broadcast_agent_output(
                    project_id=self.project_name,
                    agent_id="artist",
                    file_path=asset["path"],
                    file_type="image",
                    summary=f"游戏素材: {asset.get('asset_name')}"
                )
        
        self.logger.info(
            f"🎨 美术素材生成完成: "
            f"{result['success']}/{result['total']}成功"
        )
        
        # 美术任务完成
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="artist",
            status="idle",
            current_task=""
        )
    
    def _parse_asset_list(
        self, response: str
    ) -> list:
        """解析美术Agent返回的素材清单JSON"""
        import json
        
        try:
            # 尝试从回复中提取JSON数组
            text = response.strip()
            
            # 移除markdown代码块标记
            if "```" in text:
                lines = text.split("\n")
                json_lines = []
                in_block = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_block = not in_block
                        continue
                    if in_block or (not in_block and line.strip()):
                        json_lines.append(line)
                text = "\n".join(json_lines)
            
            # 寻找JSON数组
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                asset_list = json.loads(json_str)
                
                # 验证格式
                valid_assets = []
                for item in asset_list:
                    if isinstance(item, dict) and "name" in item:
                        valid_assets.append({
                            "name": item.get("name", "unnamed"),
                            "description": item.get("description", ""),
                            "style": item.get("style", "pixel art")
                        })
                
                return valid_assets[:6]  # 最多6个
                
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"解析素材清单失败: {e}")
        
        return []
    
    def _get_default_asset_list(self) -> list:
        """获取默认的素材清单（当解析失败时使用）"""
        return [
            {
                "name": "player_character",
                "description": "游戏主角角色",
                "style": "pixel art"
            },
            {
                "name": "game_background",
                "description": "游戏背景",
                "style": "pixel art"
            },
            {
                "name": "game_item",
                "description": "游戏道具或收集物",
                "style": "pixel art"
            }
        ]
    
    async def _phase_5_integration(self):
        """阶段5: 整合 - 确认代码和素材都已到位"""
        self.logger.info("整合代码和素材...")
        
        # 检查代码文件
        html_exists = (self.output_dir / "index.html").exists()
        js_exists = (self.output_dir / "game.js").exists()
        
        # 检查美术素材
        assets_dir = self.output_dir / "assets"
        asset_files = list(assets_dir.glob("*.png")) if assets_dir.exists() else []
        
        self.logger.info(f"代码文件: HTML={'✅' if html_exists else '❌'}, "
                        f"JS={'✅' if js_exists else '❌'}")
        self.logger.info(f"美术素材: {len(asset_files)}张PNG图片")
        
        if asset_files:
            for f in asset_files:
                self.logger.info(f"  - {f.name}")
        
        self.logger.info("✓ 整合检查完成")
        await asyncio.sleep(1)
    
    async def _phase_6_testing(self):
        """阶段6: 测试 - 测试运行游戏"""
        self.logger.info("测试工程师开始测试...")
        
        # P6版本: 测试Agent会实际执行游戏并检查错误
        
        # 广播测试工程师状态：开始测试
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="tester",
            status="working",
            current_task="准备测试游戏"
        )
        
        tester = self.agents["tester"]
        
        # 加载必要文档
        gdd = await self.file_tool.read(
            str(self.knowledge_base_dir / "game_design_doc.md")
        )
        tester.load_file_to_context("game_design_doc.md", gdd)
        
        # PM分配测试任务
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="working",
            current_task="分配测试任务给测试工程师"
        )
        
        task_message = self._create_task_message(
            to="tester",
            content="请测试游戏代码，运行游戏并检查是否有错误。如果发现Bug请记录到bug_tracker.yaml。",
            context="测试阶段"
        )
        
        await self.message_bus.send(task_message)
        
        # PM任务完成
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="idle",
            current_task=""
        )
        
        # 测试工程师开始测试
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="tester",
            status="thinking",
            current_task="正在运行测试..."
        )
        
        # 等待测试回复
        response = await self._wait_for_response("tester", timeout=120.0)
        
        if response:
            self.logger.info(f"测试回复: {response['content'][:200]}...")
            
            # 检查是否生成了Bug报告
            bug_tracker_path = self.knowledge_base_dir / "bug_tracker.yaml"
            if bug_tracker_path.exists():
                bug_content = await self.file_tool.read(str(bug_tracker_path))
                if "status: open" in bug_content:
                    self.logger.warning("⚠️ 测试发现Bug，需要修复")
                else:
                    self.logger.info("✅ 测试完成，无Bug")
            else:
                self.logger.info("✅ 测试完成")
            
            # 测试工程师任务完成
            await broadcast_agent_status(
                project_id=self.project_name,
                agent_id="tester",
                status="idle",
                current_task=""
            )
    
    async def _phase_6_5_bug_fixing(self):
        """阶段6.5: Bug修复循环 - 修复测试发现的Bug"""
        self.logger.info("开始Bug修复循环...")
        
        max_iterations = 3  # 最多循环3次
        bug_tracker_path = self.knowledge_base_dir / "bug_tracker.yaml"
        
        for iteration in range(max_iterations):
            self.logger.info(f"Bug修复循环 第{iteration + 1}次...")
            
            # 1. 检查是否有未修复的Bug
            if not bug_tracker_path.exists():
                self.logger.info("✅ 无Bug追踪文件，跳过修复")
                break
            
            try:
                bug_content = await self.file_tool.read(str(bug_tracker_path))
                
                # 简单检测是否有open状态的Bug
                if "status: open" not in bug_content:
                    self.logger.info("✅ 无未修复Bug，修复循环结束")
                    break
                
                self.logger.warning(f"⚠️ 发现未修复Bug，开始第{iteration + 1}次修复")
                
                # 2. PM分配修复任务给程序员
                await broadcast_agent_status(
                    project_id=self.project_name,
                    agent_id="pm",
                    status="working",
                    current_task="分配Bug修复任务"
                )
                
                programmer = self.agents["programmer"]
                
                # 加载Bug追踪文件到程序员上下文
                programmer.load_file_to_context("bug_tracker.yaml", bug_content)
                
                fix_message = self._create_task_message(
                    to="programmer",
                    content=f"请修复bug_tracker.yaml中记录的Bug。这是第{iteration + 1}次修复尝试。",
                    context="Bug修复",
                    priority="urgent"
                )
                
                await self.message_bus.send(fix_message)
                
                # PM任务完成
                await broadcast_agent_status(
                    project_id=self.project_name,
                    agent_id="pm",
                    status="idle",
                    current_task=""
                )
                
                # 3. 程序员开始修复
                await broadcast_agent_status(
                    project_id=self.project_name,
                    agent_id="programmer",
                    status="working",
                    current_task="正在修复Bug..."
                )
                
                # 等待程序员修复
                response = await self._wait_for_response("programmer", timeout=180.0)
                
                if response:
                    self.logger.info(f"程序员修复回复: {response['content'][:150]}...")
                
                # 程序员任务完成
                await broadcast_agent_status(
                    project_id=self.project_name,
                    agent_id="programmer",
                    status="idle",
                    current_task=""
                )
                
                # 4. 重新测试
                self.logger.info("重新运行测试...")
                
                await broadcast_agent_status(
                    project_id=self.project_name,
                    agent_id="tester",
                    status="working",
                    current_task="重新测试游戏"
                )
                
                tester = self.agents["tester"]
                
                retest_message = self._create_task_message(
                    to="tester",
                    content="程序员已修复Bug，请重新测试游戏。",
                    context="回归测试",
                    priority="urgent"
                )
                
                await self.message_bus.send(retest_message)
                
                # 等待重测结果
                retest_response = await self._wait_for_response("tester", timeout=120.0)
                
                if retest_response:
                    self.logger.info(f"重测结果: {retest_response['content'][:150]}...")
                
                # 测试工程师任务完成
                await broadcast_agent_status(
                    project_id=self.project_name,
                    agent_id="tester",
                    status="idle",
                    current_task=""
                )
                
                # 5. 等待一小段时间让Bug tracker更新
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Bug修复循环出错: {e}", exc_info=True)
                break
        
        if iteration == max_iterations - 1:
            self.logger.warning("⚠️ 达到最大修复次数(3次)，仍有未修复Bug")
        else:
            self.logger.info("✅ Bug修复循环完成")
        
        # 【决策点4】交付确认 - 测试修复完成后,请求老板确认交付
        self.logger.info("🤔 请求老板决策: 交付确认")
        
        # 检查Bug状态
        bug_tracker_path = self.knowledge_base_dir / "bug_tracker.yaml"
        bug_status = "无Bug记录"
        if bug_tracker_path.exists():
            bug_content = await self.file_tool.read(str(bug_tracker_path))
            if "status: open" in bug_content:
                bug_status = "⚠️ 仍有未修复Bug"
            else:
                bug_status = "✅ 所有Bug已修复"
        
        decision = await self._request_boss_decision(
            title="项目交付确认",
            question=f"测试和Bug修复阶段已完成,是否确认交付项目?\n\nBug状态: {bug_status}\n输出目录: {self.output_dir}",
            options=["确认交付", "继续修复Bug", "放弃项目"],
            context={"phase": "bug_fixing", "bug_status": bug_status}
        )
        
        if decision == "放弃项目":
            self.logger.error("❌ 老板放弃了项目")
            raise Exception("老板放弃了项目")
        elif decision == "继续修复Bug":
            self.logger.warning("⚠️ 老板要求继续修复Bug,但已达最大修复次数,将继续交付流程")
            # TODO: 未来版本可以实现额外的修复循环
    
    async def _phase_7_delivery(self):
        """阶段7: 交付 - PM汇报项目完成"""
        self.logger.info("PM汇报项目完成...")
        
        # 广播PM状态：准备交付
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="working",
            current_task="准备项目交付报告"
        )
        
        pm = self.agents["pm"]
        
        # PM总结项目
        summary_message = {
            "from": "pm",
            "to": "boss",
            "type": "report",
            "content": f"项目 {self.project_name} 开发完成！输出目录: {self.output_dir}",
            "context": "项目交付",
            "priority": "normal",
            "timestamp": datetime.now().isoformat()
        }
        
        await self.message_bus.send(summary_message)
        
        # PM任务完成
        await broadcast_agent_status(
            project_id=self.project_name,
            agent_id="pm",
            status="idle",
            current_task=""
        )
        
        self.logger.info("✓ 项目交付完成")
    
    async def _request_boss_decision(
        self,
        title: str,
        question: str,
        options: List[str],
        context: Dict[str, Any] = None
    ) -> str:
        """
        请求老板决策，阻塞等待用户响应
        
        Args:
            title: 决策标题
            question: 决策问题描述
            options: 可选项列表
            context: 上下文信息
            
        Returns:
            用户选择的选项
        """
        decision_id = str(uuid.uuid4())
        self.logger.info(f"🤔 请求老板决策: {title} (ID: {decision_id})")
        
        # 创建Future对象用于等待决策结果
        decision_future = asyncio.Future()
        self.pending_decisions[decision_id] = decision_future
        
        # 通过WebSocket发送决策请求到前端
        await request_boss_decision(
            project_id=self.project_name,
            decision_id=decision_id,
            agent_id="pm",
            question=f"{title}: {question}",
            options=options
        )
        
        self.logger.info(f"⏳ 等待老板决策...")
        
        try:
            # 检查是否有WebSocket客户端连接（无连接时缩短超时）
            from api.websocket_handler import manager as ws_manager
            has_clients = len(ws_manager.active_connections) > 0
            timeout_seconds = 300.0 if has_clients else 10.0
            
            if not has_clients:
                self.logger.info(f"无前端连接，自动决策超时设为{timeout_seconds}秒")
            
            # 等待决策结果
            decision = await asyncio.wait_for(decision_future, timeout=timeout_seconds)
            self.logger.info(f"✅ 收到老板决策: {decision}")
            
            # 记录决策到日志文件
            await self._log_boss_decision(decision_id, title, question, options, decision, context)
            
            return decision
            
        except asyncio.TimeoutError:
            self.logger.warning("⏰ 决策请求超时，使用默认选项")
            # 超时则返回第一个选项作为默认值
            default_decision = options[0] if options else "继续"
            await self._log_boss_decision(decision_id, title, question, options, default_decision, context, timeout=True)
            return default_decision
            
        finally:
            # 清理pending_decisions
            if decision_id in self.pending_decisions:
                del self.pending_decisions[decision_id]
    
    async def _log_boss_decision(
        self,
        decision_id: str,
        title: str,
        question: str,
        options: List[str],
        decision: str,
        context: Dict[str, Any] = None,
        timeout: bool = False
    ):
        """
        记录老板决策到decision_log.yaml
        
        Args:
            decision_id: 决策ID
            title: 决策标题
            question: 问题描述
            options: 选项列表
            decision: 用户选择
            context: 上下文信息
            timeout: 是否超时
        """
        try:
            decision_log_path = self.knowledge_base_dir / "decision_log.yaml"
            
            # 读取现有日志
            if decision_log_path.exists():
                log_content = await self.file_tool.read(str(decision_log_path))
            else:
                log_content = f"# 老板决策日志\n# 项目名称: {self.project_name}\n\n决策记录:\n"
            
            # 添加新决策记录
            new_entry = f"""
  - id: {decision_id}
    title: {title}
    question: {question}
    options: {options}
    decision: {decision}
    timeout: {timeout}
    timestamp: {datetime.now().isoformat()}
    context: {context or {}}
"""
            
            # 如果日志为空，初始化
            if "决策记录:" not in log_content:
                log_content += "\n决策记录:"
            
            log_content += new_entry
            
            # 保存日志
            await self.file_tool.write(str(decision_log_path), log_content)
            
        except Exception as e:
            self.logger.error(f"记录决策日志失败: {e}", exc_info=True)
    
    def submit_boss_decision(self, decision_id: str, choice: str):
        """
        提交老板决策结果（由HTTP API调用）
        
        Args:
            decision_id: 决策ID
            choice: 用户选择
        """
        if decision_id in self.pending_decisions:
            future = self.pending_decisions[decision_id]
            if not future.done():
                future.set_result(choice)
                self.logger.info(f"✅ 决策已提交: {decision_id} -> {choice}")
                return True
        return False
    
    async def _wait_for_response(self, agent_id: str, timeout: float = 30.0) -> Optional[Dict]:
        """
        等待指定Agent的回复消息
        
        Args:
            agent_id: Agent ID
            timeout: 超时时间（秒）
            
        Returns:
            消息字典，如果超时则返回None
        """
        start_time = asyncio.get_event_loop().time()
        
        # workflow监听自己的消息队列（Agent的回复应发给"workflow"）
        # 过滤出from=agent_id的消息，忽略其他来源的消息
        
        while True:
            # 检查是否超时
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                self.logger.warning(f"等待 {agent_id} 回复超时 ({timeout}s)")
                return None
            
            remaining = timeout - elapsed
            recv_timeout = min(2.0, remaining)
            
            # 尝试从"workflow"的队列接收消息
            message = await self.message_bus.receive("workflow", timeout=recv_timeout)
            
            if message:
                msg_from = message.get("from", "")
                msg_type = message.get("type", "")
                
                if msg_from == agent_id:
                    # 找到了目标Agent的回复
                    self.logger.info(f"收到 {agent_id} 的回复 (type={msg_type})")
                    return message
                else:
                    # 不是目标Agent的消息，记录并跳过
                    self.logger.debug(
                        f"跳过非目标消息: from={msg_from} type={msg_type} "
                        f"(等待来自 {agent_id} 的消息)"
                    )
    
    def get_status(self) -> Dict[str, Any]:
        """获取工作流当前状态"""
        return {
            "project_name": self.project_name,
            "status": self.status,
            "current_phase": self.current_phase,
            "total_phases": len(self.phases),
            "phase_name": self.phases[self.current_phase - 1]["name"] if self.current_phase > 0 else "未开始",
            "agent_status": {
                agent_id: agent.get_status()
                for agent_id, agent in self.agents.items()
            }
        }


# 测试用例（直接运行此文件时执行）
if __name__ == "__main__":
    async def test_workflow():
        """测试工作流"""
        workflow = GameDevWorkflow(
            project_name="test_snake_game",
            project_description="做一个简单的贪吃蛇游戏，蛇可以移动和吃食物"
        )
        
        await workflow.start()
        
        print("\n" + "="*60)
        print("最终状态:")
        print("="*60)
        status = workflow.get_status()
        print(f"项目名称: {status['project_name']}")
        print(f"状态: {status['status']}")
        print(f"阶段: {status['current_phase']}/{status['total_phases']}")
        print("="*60)
    
    # 运行测试
    asyncio.run(test_workflow())
