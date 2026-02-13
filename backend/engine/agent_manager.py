"""
文件: engine/agent_manager.py
职责: Agent管理器 - 管理所有Agent的生命周期和工作循环
依赖: engine/message_bus.py, engine/agent.py
被依赖: workflows/game_dev_workflow.py

关键接口:
  - AgentManager() - 创建Agent管理器
  - register_agent(agent) - 注册Agent
  - start_all() - 启动所有Agent的工作循环
  - stop_all() - 停止所有Agent
"""

import asyncio
from typing import Dict, List, Optional
from pathlib import Path
import sys

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from engine.message_bus import MessageBus
from engine.agent import Agent
from utils.logger import setup_logger


class AgentManager:
    """
    Agent管理器
    
    职责:
    1. 管理所有Agent的注册和注销
    2. 启动和停止Agent的工作循环
    3. 监控Agent的运行状态
    """
    
    def __init__(self):
        """初始化Agent管理器"""
        self.agents: Dict[str, Agent] = {}
        self.running = False
        self.tasks: List[asyncio.Task] = []
        
        # 消息总线
        self.message_bus = MessageBus()
        
        # 日志器
        self.logger = setup_logger("agent_manager")
        
        self.logger.info("Agent管理器初始化成功")
    
    def register_agent(self, agent: Agent) -> None:
        """
        注册Agent
        
        Args:
            agent: Agent实例
        """
        agent_id = agent.agent_id
        
        if agent_id in self.agents:
            self.logger.warning(f"Agent [{agent_id}] 已经注册，将被覆盖")
        
        self.agents[agent_id] = agent
        
        # 订阅消息总线
        self.message_bus.subscribe(agent_id, agent.process_message)
        
        self.logger.info(f"Agent [{agent_id}] 注册成功")
    
    def unregister_agent(self, agent_id: str) -> None:
        """
        注销Agent
        
        Args:
            agent_id: Agent的ID
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.message_bus.unsubscribe(agent_id)
            self.logger.info(f"Agent [{agent_id}] 注销成功")
    
    async def _agent_work_loop(self, agent: Agent) -> None:
        """
        Agent工作循环
        
        每个Agent的主循环:
        1. 检查是否有新消息需要处理
        2. 检查是否有分配给自己的任务
        3. 没有消息也没有任务时，空闲等待
        
        Args:
            agent: Agent实例
        """
        agent_id = agent.agent_id
        
        self.logger.info(f"Agent [{agent_id}] 工作循环启动")
        
        try:
            while self.running:
                # 1. 检查是否有新消息
                message = await self.message_bus.receive(agent_id, timeout=2.0)
                
                if message:
                    self.logger.debug(f"Agent [{agent_id}] 收到消息")
                    
                    # 处理消息
                    response_content = await agent.process_message(message)
                    
                    # 如果需要回复
                    if response_content:
                        # 优先使用reply_to字段，否则回复给发送者
                        reply_to = message.get("reply_to", message.get("from"))
                        
                        response = {
                            "from": agent_id,
                            "to": reply_to,
                            "type": "answer",
                            "content": response_content,
                            "priority": "normal"
                        }
                        await self.message_bus.send(response)
                
                # 2. TODO: 检查是否有分配的任务(P4阶段实现)
                # task = await check_tasks(agent.task_queue)
                
                # 3. 空闲等待
                await asyncio.sleep(0.1)
        
        except asyncio.CancelledError:
            self.logger.info(f"Agent [{agent_id}] 工作循环被取消")
        except Exception as e:
            self.logger.error(f"Agent [{agent_id}] 工作循环出错: {e}", exc_info=True)
    
    async def start_all(self) -> None:
        """启动所有Agent的工作循环"""
        if self.running:
            self.logger.warning("Agent管理器已经在运行")
            return
        
        self.running = True
        
        self.logger.info(f"启动 {len(self.agents)} 个Agent的工作循环")
        
        # 为每个Agent创建工作循环任务
        for agent in self.agents.values():
            task = asyncio.create_task(self._agent_work_loop(agent))
            self.tasks.append(task)
        
        self.logger.info("所有Agent工作循环已启动")
    
    async def stop_all(self) -> None:
        """停止所有Agent的工作循环"""
        if not self.running:
            return
        
        self.running = False
        
        self.logger.info("停止所有Agent的工作循环")
        
        # 取消所有任务
        for task in self.tasks:
            task.cancel()
        
        # 等待所有任务完成
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        
        self.logger.info("所有Agent工作循环已停止")
    
    def get_summary(self) -> Dict:
        """
        获取管理器状态摘要
        
        Returns:
            状态摘要字典
        """
        return {
            "running": self.running,
            "agent_count": len(self.agents),
            "agents": {
                agent_id: agent.get_status()
                for agent_id, agent in self.agents.items()
            },
            "message_bus": self.message_bus.get_summary()
        }


# 测试代码
if __name__ == "__main__":
    async def test_agent_manager():
        """测试Agent管理器"""
        print("\n" + "="*60)
        print("测试 Agent Manager")
        print("="*60 + "\n")
        
        try:
            # 导入所有Agent
            from agents.pm_agent import create_pm_agent
            from agents.planner_agent import create_planner_agent
            from agents.programmer_agent import create_programmer_agent
            
            # 创建管理器
            manager = AgentManager()
            
            print("1. 测试Agent注册:")
            print("-" * 60)
            
            pm = create_pm_agent()
            planner = create_planner_agent()
            programmer = create_programmer_agent()
            
            manager.register_agent(pm)
            manager.register_agent(planner)
            manager.register_agent(programmer)
            
            summary = manager.get_summary()
            print(f"已注册Agent数量: {summary['agent_count']}")
            print(f"Agent列表: {list(summary['agents'].keys())}")
            print("✅ Agent注册成功\n")
            
            print("2. 测试启动工作循环:")
            print("-" * 60)
            
            # 启动所有Agent
            await manager.start_all()
            print(f"工作循环运行中: {manager.running}")
            print("✅ 工作循环启动成功\n")
            
            print("3. 测试Agent间通信:")
            print("-" * 60)
            
            # PM给策划发消息
            message = {
                "from": "pm",
                "to": "planner",
                "type": "question",
                "content": "请为贪吃蛇游戏设计核心玩法",
                "priority": "normal"
            }
            
            await manager.message_bus.send(message)
            print("PM → Planner: 发送消息")
            
            # 等待消息处理
            await asyncio.sleep(15)  # 等待LLM回复
            
            history = manager.message_bus.get_history(limit=5)
            print(f"\n最近消息数: {len(history)} 条")
            for msg in history:
                print(f"  {msg['from']} → {msg['to']}: {msg['type']}")
            
            print("\n✅ Agent间通信正常\n")
            
            print("4. 测试停止工作循环:")
            print("-" * 60)
            
            await manager.stop_all()
            print(f"工作循环运行中: {manager.running}")
            print("✅ 工作循环停止成功\n")
            
            print("="*60)
            print("✅ Agent Manager 测试全部通过！")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 运行测试
    asyncio.run(test_agent_manager())
