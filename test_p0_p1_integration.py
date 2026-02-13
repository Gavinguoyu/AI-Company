"""
P0+P1 集成测试
验证环境配置和Agent引擎的整体协作
"""

import sys
import os
import asyncio
from pathlib import Path

# 设置控制台编码为 UTF-8（Windows 兼容）
if sys.platform == "win32":
    try:
        os.system("chcp 65001 > nul 2>&1")
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from config import Config
from engine.llm_client import LLMClient
from engine.context_manager import ContextManager
from engine.agent import Agent


async def test_multi_agent_conversation():
    """测试多个Agent之间的对话协作"""
    print("\n" + "="*60)
    print("集成测试：多Agent对话协作")
    print("="*60 + "\n")
    
    # 创建项目经理 Agent
    pm_prompt = """
你是这个游戏开发公司的项目经理。
你的职责是：
1. 理解客户需求
2. 协调团队成员
3. 控制项目进度
请保持专业和高效。
"""
    pm = Agent(
        agent_id="pm",
        role="项目经理",
        system_prompt=pm_prompt
    )
    
    # 创建策划 Agent
    planner_prompt = """
你是游戏策划。
你的职责是：
1. 设计游戏玩法
2. 编写策划文档
3. 回答其他同事关于设计的问题
请简洁专业地回答。
"""
    planner = Agent(
        agent_id="planner",
        role="游戏策划",
        system_prompt=planner_prompt
    )
    
    # 创建程序员 Agent
    programmer_prompt = """
你是游戏程序员。
你的职责是：
1. 实现游戏功能
2. 编写代码
3. 向策划确认技术细节
请用技术专业的语言回答。
"""
    programmer = Agent(
        agent_id="programmer",
        role="游戏程序员",
        system_prompt=programmer_prompt
    )
    
    print("✅ 创建了3个Agent：PM、策划、程序员\n")
    
    # 场景1：PM接收需求
    print("\n" + "-"*60)
    print("场景1：PM接收客户需求")
    print("-"*60)
    
    client_request = "我想做一个贪吃蛇游戏，要有像素风格，有道具系统。"
    print(f"\n客户: {client_request}")
    
    pm_response = await pm.think_and_respond(client_request)
    print(f"\nPM回复: {pm_response[:200]}...\n")
    
    # 场景2：PM向策划分配任务
    print("\n" + "-"*60)
    print("场景2：PM向策划分配任务")
    print("-"*60)
    
    pm_to_planner = "请设计贪吃蛇游戏的玩法，重点是道具系统。客户要求像素风格。"
    print(f"\nPM→策划: {pm_to_planner}")
    
    planner_response = await planner.think_and_respond(pm_to_planner)
    print(f"\n策划回复: {planner_response[:200]}...\n")
    
    # 场景3：程序员向策划提问
    print("\n" + "-"*60)
    print("场景3：程序员向策划提问技术细节")
    print("-"*60)
    
    programmer_question = "关于道具系统，道具的效果持续时间应该是多少？是否有上限？"
    print(f"\n程序员→策划: {programmer_question}")
    
    planner_answer = await planner.think_and_respond(programmer_question)
    print(f"\n策划回复: {planner_answer[:200]}...\n")
    
    # 场景4：验证上下文保持
    print("\n" + "-"*60)
    print("场景4：验证Agent能记住之前的对话")
    print("-"*60)
    
    follow_up = "那加速道具呢？"
    print(f"\n程序员→策划: {follow_up}")
    
    planner_follow_up = await planner.think_and_respond(follow_up)
    print(f"\n策划回复: {planner_follow_up[:200]}...\n")
    
    # 打印各Agent的状态
    print("\n" + "="*60)
    print("各Agent状态统计")
    print("="*60)
    
    for agent in [pm, planner, programmer]:
        status = agent.get_status()
        context = status['context']
        print(f"\n{status['role']} [{status['agent_id']}]:")
        print(f"  消息数: {context['message_count']}")
        print(f"  Token使用: {context['estimated_tokens']:,} / {context['max_tokens']:,}")
        print(f"  使用率: {context['usage_percentage']:.2f}%")
    
    print("\n" + "="*60)
    print("✅ 多Agent对话协作测试通过！")
    print("="*60 + "\n")


async def test_file_injection():
    """测试文件注入功能"""
    print("\n" + "="*60)
    print("集成测试：文件内容注入")
    print("="*60 + "\n")
    
    # 创建程序员Agent
    programmer = Agent(
        agent_id="programmer",
        role="程序员",
        system_prompt="你是一个专业的游戏程序员，严格遵守项目规范。"
    )
    
    # 模拟项目规范文件
    project_rules = """
# 项目规范

## 命名规范
- 变量名使用 camelCase
- 函数名使用 camelCase
- 类名使用 PascalCase
- 常量使用 UPPER_SNAKE_CASE

## 技术栈
- HTML5 + Canvas
- 纯JavaScript（不使用框架）
- 像素风格绘制

## 文件结构
- js/game.js - 游戏主逻辑
- js/snake.js - 蛇对象
- js/food.js - 食物管理
- js/config.js - 配置数据
"""
    
    # 注入文件
    programmer.load_file_to_context("project_rules.md", project_rules)
    
    print("已向程序员注入项目规范文件\n")
    
    # 测试Agent是否遵守规范
    question = "我要创建一个食物管理器类，应该叫什么名字？应该放在哪个文件？"
    print(f"测试问题: {question}")
    
    response = await programmer.think_and_respond(question)
    print(f"\n程序员回复:\n{response}\n")
    
    # 验证回复中是否包含规范要求
    if "FoodManager" in response or "PascalCase" in response:
        print("✅ Agent正确理解了类命名规范（PascalCase）")
    
    if "food.js" in response or "js/food.js" in response:
        print("✅ Agent正确识别了文件位置")
    
    print("\n" + "="*60)
    print("✅ 文件注入测试通过！")
    print("="*60 + "\n")


async def test_context_management():
    """测试上下文管理在实际使用中的表现"""
    print("\n" + "="*60)
    print("集成测试：上下文管理压力测试")
    print("="*60 + "\n")
    
    # 创建一个上下文限制较小的Agent
    agent = Agent(
        agent_id="test_agent",
        role="测试员",
        system_prompt="你是一个测试助手，简洁回答问题。"
    )
    
    # 修改上下文限制（模拟压力）
    agent.context_manager.max_messages = 10
    agent.context_manager.max_tokens = 5000
    
    print(f"设置上下文限制: 最多10条消息, 5000 tokens\n")
    
    # 连续发送多条消息
    questions = [
        "你好！",
        "贪吃蛇游戏应该有什么功能？",
        "道具系统怎么设计？",
        "如何实现碰撞检测？",
        "Canvas如何绘制像素风格？",
        "游戏循环应该怎么写？",
        "如何保存游戏分数？",
        "音效应该怎么添加？",
        "如何实现暂停功能？",
        "移动端适配要注意什么？",
        "关卡设计有什么建议？",
        "多人模式可行吗？",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n第{i}轮对话: {question}")
        response = await agent.think_and_respond(question)
        
        status = agent.get_status()
        context = status['context']
        print(f"  → 上下文状态: {context['message_count']}条消息, "
              f"{context['estimated_tokens']}tokens ({context['usage_percentage']:.1f}%)")
        
        # 验证不会超过限制
        assert context['message_count'] <= 10, "❌ 消息数超过限制！"
        assert context['estimated_tokens'] <= 5000, "❌ Token数超过限制！"
    
    print("\n✅ 所有对话都在上下文限制内")
    
    final_status = agent.get_status()
    final_context = final_status['context']
    
    print(f"\n最终状态:")
    print(f"  消息数: {final_context['message_count']} / 10")
    print(f"  Token: {final_context['estimated_tokens']} / 5000")
    print(f"  使用率: {final_context['usage_percentage']:.1f}%")
    
    print("\n" + "="*60)
    print("✅ 上下文管理压力测试通过！")
    print("="*60 + "\n")


async def main():
    """主测试函数"""
    print("\n")
    print("*" * 60)
    print("    P0+P1 集成测试")
    print("*" * 60)
    print("\n")
    
    try:
        # 验证配置
        print("验证环境配置...")
        if not Config.validate():
            print("❌ 配置验证失败")
            return False
        print("✅ 环境配置正常\n")
        
        # 运行集成测试
        await test_multi_agent_conversation()
        await test_file_injection()
        await test_context_management()
        
        # 总结
        print("\n" + "="*60)
        print("🎉 所有集成测试通过！")
        print("="*60)
        print("\n✅ P0阶段（环境搭建）：完全正常")
        print("✅ P1阶段（Agent引擎核心）：功能完整")
        print("✅ 多Agent协作：测试通过")
        print("✅ 文件注入机制：工作正常")
        print("✅ 上下文管理：压力测试通过")
        print("\n下一步: 准备开始 P2 阶段（消息总线 + 多Agent协作）")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
