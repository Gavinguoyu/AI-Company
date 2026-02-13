"""
P4阶段完整测试 - 端到端游戏开发工作流
==========================================
此测试将运行一个完整的7阶段游戏开发流程
"""

import asyncio
import sys
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from workflows.game_dev_workflow import GameDevWorkflow


async def main():
    """运行完整工作流"""
    print("\n" + "="*60)
    print("P4 阶段完整测试 - 端到端游戏开发工作流")
    print("="*60)
    print("\n这将运行一个完整的游戏开发流程，包括:")
    print("  1. 立项 - PM接收需求")
    print("  2. 策划 - 策划编写GDD")
    print("  3. 技术设计 - 程序员设计架构")
    print("  4. 并行开发 - 程序员+美术工作")
    print("  5. 整合 - 整合代码和素材")
    print("  6. 测试 - 测试工程师测试")
    print("  7. 交付 - PM汇报完成")
    print("\n" + "="*60)
    
    # 创建工作流
    workflow = GameDevWorkflow(
        project_name="click_counter_game",
        project_description="做一个简单的点击计数游戏，每次点击屏幕计数器加1，显示得分"
    )
    
    try:
        # 启动工作流
        await workflow.start()
        
        # 获取最终状态
        print("\n" + "="*60)
        print("最终状态报告")
        print("="*60)
        
        status = workflow.get_status()
        print(f"\n项目名称: {status['project_name']}")
        print(f"最终状态: {status['status']}")
        print(f"完成阶段: {status['current_phase']}/{status['total_phases']}")
        
        print(f"\nAgent最终状态:")
        for agent_id, agent_status in status['agent_status'].items():
            print(f"  - {agent_id}: {agent_status['status']} ({agent_status['role']})")
        
        # 检查输出文件
        print(f"\n项目目录: {workflow.project_dir}")
        print(f"\n共享知识库文件:")
        if workflow.knowledge_base_dir.exists():
            for file in workflow.knowledge_base_dir.iterdir():
                if file.is_file():
                    size = file.stat().st_size
                    print(f"  - {file.name} ({size} bytes)")
        
        print(f"\n输出文件:")
        if workflow.output_dir.exists():
            for file in workflow.output_dir.rglob("*"):
                if file.is_file():
                    size = file.stat().st_size
                    rel_path = file.relative_to(workflow.output_dir)
                    print(f"  - {rel_path} ({size} bytes)")
        
        print("\n" + "="*60)
        print("✅ 完整工作流测试成功！")
        print("="*60)
        
        return True
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ 工作流执行失败")
        print("="*60)
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
