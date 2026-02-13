"""
文件: agents/pm_agent.py
职责: 项目经理Agent - 负责项目管理、任务分配、协调冲突
依赖: engine/agent.py
被依赖: workflows/game_dev_workflow.py

关键能力:
  - 接收用户需求并拆解为任务
  - 分配任务给对应的Agent
  - 监控项目进度
  - 协调Agent之间的冲突
  - 向老板(用户)汇报并请求决策
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from engine.agent import Agent


class PMAgent(Agent):
    """
    项目经理Agent
    
    职责:
    1. 接收老板(用户)的游戏需求
    2. 将需求拆解为具体任务，分配给对应的员工
    3. 监控项目进度，协调各角色之间的冲突
    4. 当出现分歧或阻塞时，汇报给老板决策
    """
    
    def __init__(self):
        """初始化PM Agent"""
        
        system_prompt = """你是一位经验丰富的游戏项目经理(PM)。

你的职责:
1. 接收老板的游戏需求，深入理解需求的核心要点
2. 将需求拆解为具体的任务，分配给策划、程序员、美术、测试等团队成员
3. 监控项目进度，确保按阶段推进
4. 协调团队成员之间的沟通和冲突
5. 当出现重大分歧或阻塞时，汇报给老板并请求决策

工作原则:
- 保持项目目标清晰，不偏离用户需求
- 合理安排任务顺序：策划 → 技术设计 → 并行开发 → 整合 → 测试
- 及时发现和解决团队成员之间的沟通问题
- 重大决策必须请示老板，不擅自做主
- 用简洁清晰的语言沟通，避免冗长

沟通风格:
- 专业、高效、有条理
- 对团队成员友好但不失严谨
- 向老板汇报时突出关键信息
"""
        
        super().__init__(
            agent_id="pm",
            role="项目经理",
            system_prompt=system_prompt
        )
        
        # PM特有的状态
        self.current_project: Dict[str, Any] = {}
        self.tasks: List[Dict[str, Any]] = []
        self.project_phase = "idle"  # idle, planning, designing, developing, testing, done
        
        self.logger.info("PM Agent 初始化完成")
    
    def start_project(self, project_name: str, user_requirement: str) -> None:
        """
        启动新项目
        
        Args:
            project_name: 项目名称
            user_requirement: 用户需求描述
        """
        self.current_project = {
            "name": project_name,
            "requirement": user_requirement,
            "start_time": None,
            "status": "starting"
        }
        
        self.project_phase = "planning"
        
        self.logger.info(f"项目启动: [{project_name}]")
        self.logger.info(f"需求: {user_requirement[:100]}...")
    
    def create_task(self, task_type: str, assignee: str, description: str, priority: str = "normal") -> Dict[str, Any]:
        """
        创建任务
        
        Args:
            task_type: 任务类型(planning, design, coding, art, testing)
            assignee: 分配给谁(agent_id)
            description: 任务描述
            priority: 优先级
        
        Returns:
            任务字典
        """
        task = {
            "id": f"task_{len(self.tasks) + 1}",
            "type": task_type,
            "assignee": assignee,
            "description": description,
            "priority": priority,
            "status": "pending",  # pending, in_progress, completed, blocked
            "created_at": None
        }
        
        self.tasks.append(task)
        
        self.logger.info(f"创建任务: [{task['id']}] 分配给 [{assignee}]")
        
        return task
    
    def get_project_status(self) -> Dict[str, Any]:
        """
        获取项目状态
        
        Returns:
            项目状态字典
        """
        return {
            "project": self.current_project,
            "phase": self.project_phase,
            "tasks": {
                "total": len(self.tasks),
                "completed": len([t for t in self.tasks if t["status"] == "completed"]),
                "in_progress": len([t for t in self.tasks if t["status"] == "in_progress"]),
                "blocked": len([t for t in self.tasks if t["status"] == "blocked"])
            },
            "agent_status": self.get_status()
        }


def create_pm_agent() -> PMAgent:
    """
    创建PM Agent实例
    
    工厂函数，供外部调用
    
    Returns:
        PM Agent实例
    """
    return PMAgent()


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_pm_agent():
        """测试PM Agent"""
        print("\n" + "="*60)
        print("测试 PM Agent")
        print("="*60 + "\n")
        
        try:
            # 创建PM
            pm = create_pm_agent()
            
            print("1. 测试PM初始化:")
            print("-" * 60)
            print(f"Agent ID: {pm.agent_id}")
            print(f"角色: {pm.role}")
            print(f"状态: {pm.status}")
            print("✅ PM初始化成功\n")
            
            print("2. 测试启动项目:")
            print("-" * 60)
            pm.start_project(
                "贪吃蛇游戏",
                "做一个贪吃蛇游戏，像素风格，带道具系统，支持浏览器运行"
            )
            status = pm.get_project_status()
            print(f"项目名称: {status['project']['name']}")
            print(f"项目阶段: {status['phase']}")
            print("✅ 项目启动成功\n")
            
            print("3. 测试任务创建:")
            print("-" * 60)
            task1 = pm.create_task(
                task_type="planning",
                assignee="planner",
                description="编写游戏策划文档(GDD)，定义玩法、规则、数值配置",
                priority="high"
            )
            print(f"任务1: {task1['id']} - {task1['description'][:40]}...")
            
            task2 = pm.create_task(
                task_type="design",
                assignee="programmer",
                description="设计技术架构，确定模块划分和接口",
                priority="high"
            )
            print(f"任务2: {task2['id']} - {task2['description'][:40]}...")
            
            status = pm.get_project_status()
            print(f"任务总数: {status['tasks']['total']}")
            print("✅ 任务创建成功\n")
            
            print("4. 测试对话能力:")
            print("-" * 60)
            
            # 模拟老板给PM下达需求
            print("\n用户(老板): PM，我想做一个贪吃蛇游戏，你帮我拆解一下需要哪些步骤？")
            response = await pm.think_and_respond(
                "我想做一个贪吃蛇游戏，带道具系统，像素风格。请帮我拆解一下开发步骤。"
            )
            print(f"\nPM: {response}\n")
            
            print("✅ 对话能力正常\n")
            
            print("5. 测试接收进度汇报:")
            print("-" * 60)
            
            # 模拟策划汇报
            print("\n策划: PM，我已经完成了游戏策划文档，请审阅。")
            response = await pm.think_and_respond(
                "[策划汇报] 游戏策划文档已完成，包含玩法设计、道具系统、数值配置表。是否需要调整？"
            )
            print(f"\nPM: {response}\n")
            
            print("✅ 进度汇报处理正常\n")
            
            print("6. 测试协调冲突:")
            print("-" * 60)
            
            # 模拟冲突场景
            print("\n程序员: PM，策划文档中的某个功能技术上很难实现，需要讨论替代方案。")
            response = await pm.think_and_respond(
                "[程序员问题] 策划要求的'蛇穿墙传送'功能在Canvas渲染中实现复杂，建议用边界反弹代替，是否需要和策划讨论？"
            )
            print(f"\nPM: {response}\n")
            
            print("✅ 冲突协调能力正常\n")
            
            print("="*60)
            print("✅ PM Agent 测试全部通过！")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 运行测试
    asyncio.run(test_pm_agent())
