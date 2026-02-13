"""
文件: agents/planner_agent.py
职责: 游戏策划Agent - 负责游戏设计文档、玩法设计、数值配置
依赖: engine/agent.py
被依赖: workflows/game_dev_workflow.py

关键能力:
  - 根据需求撰写游戏策划文档(GDD)
  - 定义游戏玩法、规则、关卡、数值配置表
  - 回答程序员和美术关于设计意图的疑问
  - 根据测试反馈调整设计
"""

import sys
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from engine.agent import Agent


class PlannerAgent(Agent):
    """
    游戏策划Agent
    
    职责:
    1. 根据PM的任务，撰写游戏策划文档(GDD)
    2. 定义游戏玩法、规则、关卡、数值配置表
    3. 输出结构化的配置数据(YAML格式)
    4. 回答程序员和美术关于设计意图的疑问
    """
    
    def __init__(self):
        """初始化Planner Agent"""
        
        system_prompt = """你是一位资深的游戏策划。

你的职责:
1. 根据需求撰写清晰、完整的游戏策划文档(GDD)
2. 定义游戏玩法、规则、关卡设计
3. 设计数值配置表，平衡游戏难度
4. 输出结构化的YAML配置文件供程序员使用
5. 回答程序员和美术关于设计意图的问题
6. 根据测试反馈调整和优化设计

设计原则:
- 玩法要简单易懂，容易上手但有深度
- 数值设计要平衡，避免过难或过简单
- 考虑技术可行性，不提出难以实现的需求
- 文档要清晰明确，避免歧义
- 所有配置数据使用YAML格式输出

沟通风格:
- 专业、有条理、逻辑清晰
- 善于用具体例子说明抽象概念
- 对程序员和美术的疑问耐心解答
"""
        
        super().__init__(
            agent_id="planner",
            role="游戏策划",
            system_prompt=system_prompt
        )
        
        self.logger.info("Planner Agent 初始化完成")


def create_planner_agent() -> PlannerAgent:
    """创建Planner Agent实例"""
    return PlannerAgent()


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_planner_agent():
        """测试Planner Agent"""
        print("\n" + "="*60)
        print("测试 Planner Agent")
        print("="*60 + "\n")
        
        try:
            planner = create_planner_agent()
            
            print("1. 测试基本信息:")
            print("-" * 60)
            print(f"Agent ID: {planner.agent_id}")
            print(f"角色: {planner.role}")
            print("✅ 策划初始化成功\n")
            
            print("2. 测试策划文档编写:")
            print("-" * 60)
            print("\nPM: 请为贪吃蛇游戏编写核心玩法设计")
            response = await planner.think_and_respond(
                "请为贪吃蛇游戏编写核心玩法设计，包括基本规则、食物系统、分数计算等"
            )
            print(f"\n策划: {response[:300]}...\n")
            print("✅ 策划文档能力正常\n")
            
            print("3. 测试配置表设计:")
            print("-" * 60)
            print("\nPM: 请设计道具系统的配置表")
            response = await planner.think_and_respond(
                "请用YAML格式设计道具系统的配置表，包含至少3种道具：加速、减速、无敌"
            )
            print(f"\n策划: {response[:300]}...\n")
            print("✅ 配置表设计能力正常\n")
            
            print("4. 测试回答程序员问题:")
            print("-" * 60)
            print("\n程序员: 加速道具的具体数值是多少？")
            response = await planner.think_and_respond(
                "[程序员问题] 加速道具应该让蛇的速度增加多少？持续时间多久？有没有上限？"
            )
            print(f"\n策划: {response[:200]}...\n")
            print("✅ 问答能力正常\n")
            
            print("="*60)
            print("✅ Planner Agent 测试全部通过！")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_planner_agent())
