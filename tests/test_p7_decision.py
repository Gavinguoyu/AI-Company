"""
P7阶段测试 - 人类介入机制
验证决策请求和响应功能
"""

import asyncio
import sys
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from workflows.game_dev_workflow import GameDevWorkflow
from api.websocket_handler import register_workflow, handle_boss_decision_response


async def test_decision_mechanism():
    """测试决策机制"""
    print("=" * 60)
    print("P7阶段测试: 人类介入机制")
    print("=" * 60)
    
    # 创建一个简单的工作流
    workflow = GameDevWorkflow(
        project_name="test_decision",
        project_description="测试决策机制的简单游戏"
    )
    
    # 注册工作流
    register_workflow("test_decision", workflow)
    
    # 初始化工作流（但不启动完整流程）
    await workflow.initialize()
    
    print("\n✅ 工作流已初始化")
    print(f"✅ 决策存储已准备: {len(workflow.pending_decisions)} 个待决策")
    
    # 模拟请求决策
    print("\n" + "=" * 60)
    print("测试1: 请求老板决策")
    print("=" * 60)
    
    # 创建异步任务来请求决策
    async def request_decision():
        decision = await workflow._request_boss_decision(
            title="测试决策",
            question="这是一个测试决策，请选择一个选项",
            options=["选项A", "选项B", "选项C"],
            context={"test": "data"}
        )
        print(f"\n✅ 收到决策结果: {decision}")
        return decision
    
    # 启动决策请求（异步）
    decision_task = asyncio.create_task(request_decision())
    
    # 等待一小段时间确保决策请求已发送
    await asyncio.sleep(1)
    
    print(f"\n✅ 决策请求已发送")
    print(f"✅ 待决策数量: {len(workflow.pending_decisions)}")
    
    # 模拟从前端收到决策响应
    print("\n" + "=" * 60)
    print("测试2: 提交决策响应")
    print("=" * 60)
    
    # 获取决策ID
    decision_id = list(workflow.pending_decisions.keys())[0]
    print(f"✅ 决策ID: {decision_id}")
    
    # 模拟WebSocket收到用户选择
    choice = "选项B"
    await handle_boss_decision_response(decision_id, choice)
    
    # 等待决策任务完成
    result = await decision_task
    
    print(f"\n✅ 决策任务已完成")
    print(f"✅ 最终决策: {result}")
    
    # 验证决策日志
    print("\n" + "=" * 60)
    print("测试3: 验证决策日志")
    print("=" * 60)
    
    decision_log_path = workflow.knowledge_base_dir / "decision_log.yaml"
    if decision_log_path.exists():
        from tools.file_tool import FileTool
        file_tool = FileTool()
        log_content = await file_tool.read(str(decision_log_path))
        print(f"\n✅ 决策日志已记录:")
        print(log_content[:500])  # 显示前500字符
    else:
        print("\n❌ 决策日志文件不存在")
    
    # 停止Agent
    await workflow.agent_manager.stop_all()
    
    print("\n" + "=" * 60)
    print("✅ P7阶段测试完成")
    print("=" * 60)


async def test_decision_timeout():
    """测试决策超时机制"""
    print("\n" + "=" * 60)
    print("测试4: 决策超时机制")
    print("=" * 60)
    
    workflow = GameDevWorkflow(
        project_name="test_timeout",
        project_description="测试超时的简单游戏"
    )
    
    register_workflow("test_timeout", workflow)
    await workflow.initialize()
    
    # 请求决策但不提交响应，等待超时
    print("\n⏳ 请求决策（将在5秒后超时）...")
    
    # 临时减少超时时间用于测试
    original_method = workflow._request_boss_decision
    
    async def quick_timeout_decision(*args, **kwargs):
        # 修改超时时间为5秒
        decision_id = str(__import__('uuid').uuid4())
        workflow.logger.info(f"🤔 请求老板决策 (快速超时): {args[0]} (ID: {decision_id})")
        
        decision_future = asyncio.Future()
        workflow.pending_decisions[decision_id] = decision_future
        
        from api.websocket_handler import request_boss_decision
        await request_boss_decision(
            project_id=workflow.project_name,
            decision_id=decision_id,
            agent_id="pm",
            question=f"{args[0]}: {args[1]}",
            options=args[2]
        )
        
        try:
            decision = await asyncio.wait_for(decision_future, timeout=5.0)
            return decision
        except asyncio.TimeoutError:
            print("\n⏰ 决策超时，使用默认选项")
            default = args[2][0] if args[2] else "继续"
            return default
        finally:
            if decision_id in workflow.pending_decisions:
                del workflow.pending_decisions[decision_id]
    
    workflow._request_boss_decision = quick_timeout_decision
    
    result = await workflow._request_boss_decision(
        "超时测试",
        "这个决策将超时",
        ["默认选项", "其他选项"],
        {}
    )
    
    print(f"\n✅ 超时处理完成，使用默认选项: {result}")
    
    await workflow.agent_manager.stop_all()


if __name__ == "__main__":
    print("\n🚀 开始P7阶段测试\n")
    
    # 运行测试
    asyncio.run(test_decision_mechanism())
    asyncio.run(test_decision_timeout())
    
    print("\n✅ 所有测试完成！")
