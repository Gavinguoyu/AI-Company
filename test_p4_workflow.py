"""
P4阶段测试脚本 - 游戏开发工作流测试
==========================================
测试内容:
1. 工作流初始化
2. 项目目录结构创建
3. 共享知识库文件创建
4. 7个阶段流程执行
5. Agent协作流程
"""

import asyncio
import sys
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from workflows.game_dev_workflow import GameDevWorkflow
from config import Config


async def test_workflow_initialization():
    """测试1: 工作流初始化"""
    print("\n" + "="*60)
    print("测试1: 工作流初始化")
    print("="*60)
    
    try:
        workflow = GameDevWorkflow(
            project_name="test_simple_game",
            project_description="做一个简单的点击游戏，点击屏幕得分"
        )
        
        print(f"✓ 工作流创建成功")
        print(f"  - 项目名称: {workflow.project_name}")
        print(f"  - 项目描述: {workflow.project_description}")
        print(f"  - 阶段数量: {len(workflow.phases)}")
        print(f"  - 当前状态: {workflow.status}")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def test_project_structure():
    """测试2: 项目目录结构创建"""
    print("\n" + "="*60)
    print("测试2: 项目目录结构创建")
    print("="*60)
    
    try:
        workflow = GameDevWorkflow(
            project_name="test_structure",
            project_description="测试项目结构"
        )
        
        # 创建项目结构
        await workflow._create_project_structure()
        
        # 检查目录是否创建
        required_dirs = [
            workflow.project_dir,
            workflow.knowledge_base_dir,
            workflow.output_dir,
            workflow.output_dir / "js",
            workflow.output_dir / "assets",
            workflow.logs_dir
        ]
        
        all_exist = True
        for directory in required_dirs:
            exists = directory.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {directory.relative_to(Config.PROJECTS_DIR)}")
            if not exists:
                all_exist = False
        
        if all_exist:
            print("✓ 所有目录创建成功")
            return True
        else:
            print("✗ 部分目录创建失败")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_knowledge_base_files():
    """测试3: 共享知识库文件创建"""
    print("\n" + "="*60)
    print("测试3: 共享知识库文件创建")
    print("="*60)
    
    try:
        workflow = GameDevWorkflow(
            project_name="test_knowledge_base",
            project_description="测试知识库"
        )
        
        # 创建知识库
        await workflow._create_project_structure()
        
        # 检查文件是否创建
        required_files = [
            "project_rules.yaml",
            "game_design_doc.md",
            "tech_design_doc.md",
            "api_registry.yaml",
            "config_tables.yaml",
            "art_asset_list.yaml",
            "bug_tracker.yaml",
            "decision_log.yaml"
        ]
        
        all_exist = True
        for filename in required_files:
            filepath = workflow.knowledge_base_dir / filename
            exists = filepath.exists()
            status = "✓" if exists else "✗"
            
            if exists:
                size = filepath.stat().st_size
                print(f"  {status} {filename} ({size} bytes)")
            else:
                print(f"  {status} {filename}")
                all_exist = False
        
        if all_exist:
            print("✓ 所有知识库文件创建成功")
            
            # 读取并显示一个文件的内容
            project_rules_path = workflow.knowledge_base_dir / "project_rules.yaml"
            content = project_rules_path.read_text(encoding='utf-8')
            print(f"\n【project_rules.yaml 示例内容】:")
            print(content[:300] + "...")
            
            return True
        else:
            print("✗ 部分文件创建失败")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_creation():
    """测试4: Agent创建和注册"""
    print("\n" + "="*60)
    print("测试4: Agent创建和注册")
    print("="*60)
    
    try:
        workflow = GameDevWorkflow(
            project_name="test_agents",
            project_description="测试Agent创建"
        )
        
        # 创建Agent
        await workflow._create_agents()
        
        # 检查Agent是否创建
        expected_agents = ["pm", "planner", "programmer", "artist", "tester"]
        
        all_created = True
        for agent_id in expected_agents:
            exists = agent_id in workflow.agents
            status = "✓" if exists else "✗"
            
            if exists:
                agent = workflow.agents[agent_id]
                print(f"  {status} {agent_id}: {agent.role}")
            else:
                print(f"  {status} {agent_id}: 未创建")
                all_created = False
        
        if all_created:
            print(f"✓ 所有 {len(expected_agents)} 个Agent创建成功")
            return True
        else:
            print("✗ 部分Agent创建失败")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_phase_execution():
    """测试5: 阶段执行流程（简化测试）"""
    print("\n" + "="*60)
    print("测试5: 阶段执行流程（简化测试）")
    print("="*60)
    
    try:
        workflow = GameDevWorkflow(
            project_name="test_phases",
            project_description="一个简单的点击计数游戏"
        )
        
        # 初始化环境
        await workflow.initialize()
        print("✓ 工作流环境初始化成功")
        
        # 测试第一个阶段（立项）
        print("\n执行阶段1: 立项...")
        await workflow._phase_1_initiation()
        print("✓ 阶段1执行完成")
        
        # 检查消息历史
        history = workflow.message_bus.get_history(limit=10)
        print(f"\n消息历史 (最近{len(history)}条):")
        for i, msg in enumerate(history[-5:], 1):  # 显示最近5条
            print(f"  {i}. [{msg['from']}→{msg['to']}] {msg['type']}: {msg['content'][:50]}...")
        
        # 停止所有Agent
        await workflow.agent_manager.stop_all()
        
        print("\n✓ 阶段执行测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_workflow_status():
    """测试6: 工作流状态查询"""
    print("\n" + "="*60)
    print("测试6: 工作流状态查询")
    print("="*60)
    
    try:
        workflow = GameDevWorkflow(
            project_name="test_status",
            project_description="测试状态查询"
        )
        
        # 初始化
        await workflow.initialize()
        
        # 获取状态
        status = workflow.get_status()
        
        print(f"工作流状态:")
        print(f"  - 项目名称: {status['project_name']}")
        print(f"  - 状态: {status['status']}")
        print(f"  - 当前阶段: {status['current_phase']}/{status['total_phases']}")
        print(f"  - 阶段名称: {status['phase_name']}")
        print(f"  - Agent数量: {len(status['agent_status'])}")
        
        print(f"\nAgent状态:")
        for agent_id, agent_status in status['agent_status'].items():
            print(f"  - {agent_id}: {agent_status['status']} ({agent_status['role']})")
        
        # 停止
        await workflow.agent_manager.stop_all()
        
        print("\n✓ 状态查询测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("P4 阶段测试 - 游戏开发工作流")
    print("="*60)
    
    tests = [
        ("工作流初始化", test_workflow_initialization),
        ("项目目录结构创建", test_project_structure),
        ("共享知识库文件创建", test_knowledge_base_files),
        ("Agent创建和注册", test_agent_creation),
        ("阶段执行流程", test_phase_execution),
        ("工作流状态查询", test_workflow_status),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{test_name}' 执行异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")
    
    print("="*60)
    print(f"测试结果: {passed}/{total} 通过")
    print("="*60)
    
    if passed == total:
        print("\n🎉 所有测试通过！P4阶段基础功能实现完成")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
