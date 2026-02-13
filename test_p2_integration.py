"""
P2阶段集成测试脚本

测试内容:
1. 消息总线功能
2. 5个Agent的基本能力
3. Agent管理器
4. 多Agent协作通信
"""

import asyncio
import sys
from pathlib import Path

# 添加 backend 到路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from engine.message_bus import MessageBus
from engine.agent_manager import AgentManager
from agents.pm_agent import create_pm_agent
from agents.planner_agent import create_planner_agent
from agents.programmer_agent import create_programmer_agent
from agents.artist_agent import create_artist_agent
from agents.tester_agent import create_tester_agent


async def test_message_bus():
    """测试1: 消息总线"""
    print("\n" + "="*60)
    print("测试1: 消息总线")
    print("="*60)
    
    bus = MessageBus()
    
    # 测试单例
    bus2 = MessageBus()
    assert bus is bus2, "消息总线应该是单例"
    print("✅ 单例模式正常")
    
    # 测试订阅
    bus.subscribe("test_agent", lambda msg: None)
    summary = bus.get_summary()
    assert summary['active_agents'] == 1
    print("✅ Agent订阅正常")
    
    # 测试消息发送
    msg = {
        "from": "a",
        "to": "b",
        "type": "test",
        "content": "hello"
    }
    await bus.send(msg)
    history = bus.get_history(limit=1)
    assert len(history) == 1
    print("✅ 消息发送正常")
    
    print("✅ 消息总线测试通过\n")


async def test_agents():
    """测试2: 5个Agent的基本能力"""
    print("\n" + "="*60)
    print("测试2: 5个Agent基本能力")
    print("="*60)
    
    agents = {
        "pm": create_pm_agent(),
        "planner": create_planner_agent(),
        "programmer": create_programmer_agent(),
        "artist": create_artist_agent(),
        "tester": create_tester_agent()
    }
    
    for agent_id, agent in agents.items():
        assert agent.agent_id == agent_id
        assert agent.role is not None
        print(f"✅ {agent_id:12} - {agent.role}")
    
    print("✅ 所有Agent创建成功\n")


async def test_agent_manager():
    """测试3: Agent管理器"""
    print("\n" + "="*60)
    print("测试3: Agent管理器")
    print("="*60)
    
    manager = AgentManager()
    
    # 注册3个Agent
    pm = create_pm_agent()
    planner = create_planner_agent()
    programmer = create_programmer_agent()
    
    manager.register_agent(pm)
    manager.register_agent(planner)
    manager.register_agent(programmer)
    
    summary = manager.get_summary()
    assert summary['agent_count'] == 3
    print(f"✅ 注册了 {summary['agent_count']} 个Agent")
    
    # 启动工作循环
    await manager.start_all()
    assert manager.running
    print("✅ 工作循环启动成功")
    
    # 停止工作循环
    await manager.stop_all()
    assert not manager.running
    print("✅ 工作循环停止成功")
    
    print("✅ Agent管理器测试通过\n")


async def test_multi_agent_communication():
    """测试4: 多Agent协作通信"""
    print("\n" + "="*60)
    print("测试4: 多Agent协作通信")
    print("="*60)
    
    manager = AgentManager()
    
    # 注册所有Agent
    manager.register_agent(create_pm_agent())
    manager.register_agent(create_planner_agent())
    manager.register_agent(create_programmer_agent())
    
    # 启动工作循环
    await manager.start_all()
    
    # 场景1: PM给策划发消息
    print("\n场景1: PM → Planner")
    msg1 = {
        "from": "pm",
        "to": "planner",
        "type": "question",
        "content": "请简要说明贪吃蛇的核心玩法(一句话即可)",
        "priority": "normal"
    }
    await manager.message_bus.send(msg1)
    print("  消息已发送，等待回复...")
    
    # 等待处理
    await asyncio.sleep(12)
    
    # 检查消息历史
    history = manager.message_bus.get_history(limit=10)
    pm_to_planner = [m for m in history if m['from'] == 'pm' and m['to'] == 'planner']
    planner_to_pm = [m for m in history if m['from'] == 'planner' and m['to'] == 'pm']
    
    assert len(pm_to_planner) >= 1, "PM应该给策划发了消息"
    assert len(planner_to_pm) >= 1, "策划应该回复了PM"
    
    print(f"  ✅ PM发送: {len(pm_to_planner)}条")
    print(f"  ✅ Planner回复: {len(planner_to_pm)}条")
    
    # 场景2: 策划给程序员发消息
    print("\n场景2: Planner → Programmer")
    msg2 = {
        "from": "planner",
        "to": "programmer",
        "type": "report",
        "content": "策划文档已完成，请查阅",
        "priority": "normal"
    }
    await manager.message_bus.send(msg2)
    print("  消息已发送")
    
    await asyncio.sleep(1)
    
    planner_to_prog = [m for m in manager.message_bus.get_history() 
                       if m['from'] == 'planner' and m['to'] == 'programmer']
    assert len(planner_to_prog) >= 1
    print("  ✅ 消息传递成功")
    
    # 停止
    await manager.stop_all()
    
    print("\n✅ 多Agent协作通信测试通过\n")


async def test_all():
    """运行所有测试"""
    print("\n" + "="*70)
    print("P2阶段集成测试 - 消息总线 + 多Agent协作")
    print("="*70)
    
    try:
        await test_message_bus()
        await test_agents()
        await test_agent_manager()
        await test_multi_agent_communication()
        
        print("\n" + "="*70)
        print("🎉 P2阶段所有测试通过！")
        print("="*70)
        
        print("\n" + "="*70)
        print("测试摘要:")
        print("="*70)
        print("✅ 消息总线: 单例、订阅、消息路由")
        print("✅ 5个Agent: PM、策划、程序员、美术、测试")
        print("✅ Agent管理器: 注册、工作循环、生命周期管理")
        print("✅ 多Agent通信: PM↔策划、策划→程序员")
        print("\n核心功能:")
        print("  • Agent能接收和发送消息")
        print("  • Agent能通过消息总线互相对话")
        print("  • Agent工作循环能正常运行")
        print("  • 消息能正确路由到目标Agent")
        print("\n下一阶段: P3 - 工具系统")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_all())
    sys.exit(0 if success else 1)
