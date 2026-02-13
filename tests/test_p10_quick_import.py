"""
P10 快速导入和模块检测测试
验证所有P1-P9模块能正常导入，无语法错误
"""

import sys
import io
from pathlib import Path
import time

# 设置Windows控制台编码为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

results = []

def test_import(name, import_func):
    """测试单个导入"""
    try:
        import_func()
        results.append((name, True, ""))
        print(f"  ✅ {name}")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"  ❌ {name}: {e}")


def main():
    print("=" * 60)
    print("🔍 P10 快速模块导入检测")
    print("=" * 60)
    start_time = time.time()
    
    # ===== 核心引擎 =====
    print("\n📦 核心引擎模块:")
    
    test_import("config.Config", lambda: __import__('config').Config)
    test_import("engine.agent.Agent", lambda: __import__('engine.agent', fromlist=['Agent']).Agent)
    test_import("engine.message_bus.MessageBus", lambda: __import__('engine.message_bus', fromlist=['MessageBus']).MessageBus)
    test_import("engine.agent_manager.AgentManager", lambda: __import__('engine.agent_manager', fromlist=['AgentManager']).AgentManager)
    test_import("engine.llm_client.LLMClient", lambda: __import__('engine.llm_client', fromlist=['LLMClient']).LLMClient)
    test_import("engine.context_manager.ContextManager", lambda: __import__('engine.context_manager', fromlist=['ContextManager']).ContextManager)
    
    # ===== 工具系统 =====
    print("\n🛠️ 工具系统模块:")
    
    test_import("tools.file_tool.FileTool", lambda: __import__('tools.file_tool', fromlist=['FileTool']).FileTool)
    test_import("tools.code_runner.CodeRunner", lambda: __import__('tools.code_runner', fromlist=['CodeRunner']).CodeRunner)
    test_import("tools.code_search_tool.CodeSearchTool", lambda: __import__('tools.code_search_tool', fromlist=['CodeSearchTool']).CodeSearchTool)
    test_import("tools.tool_registry.ToolRegistry", lambda: __import__('tools.tool_registry', fromlist=['ToolRegistry']).ToolRegistry)
    test_import("tools.game_validator.GameValidator", lambda: __import__('tools.game_validator', fromlist=['GameValidator']).GameValidator)
    test_import("tools.image_gen_tool.ImageGenTool", lambda: __import__('tools.image_gen_tool', fromlist=['ImageGenTool']).ImageGenTool)
    
    # ===== Agent =====
    print("\n👤 Agent 模块:")
    
    test_import("agents.pm_agent.PMAgent", lambda: __import__('agents.pm_agent', fromlist=['PMAgent']).PMAgent)
    test_import("agents.planner_agent.PlannerAgent", lambda: __import__('agents.planner_agent', fromlist=['PlannerAgent']).PlannerAgent)
    test_import("agents.programmer_agent.ProgrammerAgent", lambda: __import__('agents.programmer_agent', fromlist=['ProgrammerAgent']).ProgrammerAgent)
    test_import("agents.artist_agent.ArtistAgent", lambda: __import__('agents.artist_agent', fromlist=['ArtistAgent']).ArtistAgent)
    test_import("agents.tester_agent.TesterAgent", lambda: __import__('agents.tester_agent', fromlist=['TesterAgent']).TesterAgent)
    
    # ===== 工作流 =====
    print("\n🔄 工作流模块:")
    
    test_import("workflows.game_dev_workflow.GameDevWorkflow", lambda: __import__('workflows.game_dev_workflow', fromlist=['GameDevWorkflow']).GameDevWorkflow)
    
    # ===== API =====
    print("\n🌐 API 模块:")
    
    test_import("api.http_routes.router", lambda: __import__('api.http_routes', fromlist=['router']).router)
    test_import("api.websocket_handler.router", lambda: __import__('api.websocket_handler', fromlist=['router']).router)
    test_import("api.websocket_handler.ConnectionManager", lambda: __import__('api.websocket_handler', fromlist=['ConnectionManager']).ConnectionManager)
    
    # ===== 提示词模板 =====
    print("\n📝 提示词模板:")
    
    test_import("prompts.code_generation_template", lambda: __import__('prompts.code_generation_template', fromlist=['HTML5_GAME_TEMPLATE']))
    
    # ===== 工具函数 =====
    print("\n🔧 工具函数:")
    
    test_import("utils.logger.setup_logger", lambda: __import__('utils.logger', fromlist=['setup_logger']).setup_logger)
    test_import("utils.retry.async_retry", lambda: __import__('utils.retry', fromlist=['async_retry']).async_retry)
    
    # ===== FastAPI App =====
    print("\n🚀 FastAPI App:")
    
    test_import("main.create_app", lambda: __import__('main', fromlist=['create_app']).create_app)
    
    # ===== 统计结果 =====
    elapsed = time.time() - start_time
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    print(f"⏱️ 耗时: {elapsed:.1f}秒")
    
    if failed > 0:
        print(f"\n❌ 失败的模块 ({failed}个):")
        for name, ok, err in results:
            if not ok:
                print(f"  - {name}: {err}")
        print("=" * 60)
        return 1
    else:
        print("\n🎉 所有模块导入测试通过！")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
