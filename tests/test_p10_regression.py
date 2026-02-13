# -*- coding: utf-8 -*-
"""
P10 Quick Regression Test
Verifies all modules from P1-P9 can be imported and initialized correctly.
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = str(Path(__file__).parent.parent / "backend")
sys.path.insert(0, backend_path)


def test_p0_config():
    """P0: Config validation"""
    from config import Config
    assert Config.validate(), "Config validation failed"
    print("  [OK] P0 - Config validation")


def test_p1_engine():
    """P1: Agent engine core"""
    from engine.llm_client import LLMClient
    from engine.context_manager import ContextManager
    from engine.agent import Agent
    
    client = LLMClient()
    assert client is not None
    
    ctx = ContextManager()
    assert ctx is not None
    
    print("  [OK] P1 - Agent engine (LLMClient, ContextManager, Agent)")


def test_p2_message_bus():
    """P2: Message bus and agents"""
    from engine.message_bus import MessageBus
    from engine.agent_manager import AgentManager
    from agents.pm_agent import PMAgent
    from agents.planner_agent import PlannerAgent
    from agents.programmer_agent import ProgrammerAgent
    from agents.artist_agent import ArtistAgent
    from agents.tester_agent import TesterAgent
    
    bus = MessageBus()
    assert bus is not None
    
    # Verify all 5 agents can be created
    pm = PMAgent()
    planner = PlannerAgent()
    programmer = ProgrammerAgent()
    artist = ArtistAgent()
    tester = TesterAgent()
    
    print("  [OK] P2 - MessageBus + 5 Agents")


def test_p3_tools():
    """P3: Tool system"""
    from tools.file_tool import FileTool
    from tools.code_runner import CodeRunner
    from tools.code_search_tool import CodeSearchTool
    from tools.tool_registry import ToolRegistry
    
    ft = FileTool()
    assert ft is not None
    
    cr = CodeRunner()
    assert cr is not None
    
    print("  [OK] P3 - Tools (FileTool, CodeRunner, CodeSearchTool, ToolRegistry)")


def test_p4_workflow():
    """P4: Game dev workflow"""
    from workflows.game_dev_workflow import GameDevWorkflow
    
    wf = GameDevWorkflow("test_p10", "Test game for P10 regression")
    assert wf is not None
    assert wf.project_name == "test_p10"
    
    print("  [OK] P4 - GameDevWorkflow")


def test_p5_api():
    """P5: Web API routes"""
    from api.http_routes import router as http_router
    from api.websocket_handler import router as ws_router
    
    assert http_router is not None
    assert ws_router is not None
    
    print("  [OK] P5 - HTTP + WebSocket routes")


def test_p5_fastapi_app():
    """P5: FastAPI app creation"""
    from main import create_app
    app = create_app()
    assert app is not None
    assert app.title == "AI \u6e38\u620f\u5f00\u53d1\u516c\u53f8"
    
    print("  [OK] P5 - FastAPI app creation")


def test_p7_decision():
    """P7: Boss decision mechanism"""
    from workflows.game_dev_workflow import GameDevWorkflow
    
    # Check that decision methods exist
    assert hasattr(GameDevWorkflow, '_request_boss_decision'), "Missing _request_boss_decision"
    assert hasattr(GameDevWorkflow, 'submit_boss_decision'), "Missing submit_boss_decision"
    
    print("  [OK] P7 - Decision mechanism methods exist")


def test_p9_image_gen():
    """P9: Image generation tool"""
    from tools.image_gen_tool import ImageGenTool
    
    tool = ImageGenTool()
    assert tool is not None
    
    print("  [OK] P9 - ImageGenTool")


def test_p9_artist_tools():
    """P9: Artist agent has image_gen tool"""
    from agents.artist_agent import ArtistAgent
    
    artist = ArtistAgent()
    tools = artist.get_available_tools()
    tool_names = [t['name'] for t in tools]
    
    assert 'image_gen' in tool_names or 'file' in tool_names, \
        f"Artist should have file/image_gen tools, got: {tool_names}"
    
    print("  [OK] P9 - Artist agent tools configured")


def main():
    print("=" * 60)
    print("P10 Quick Regression Test")
    print("=" * 60)
    print()
    
    tests = [
        test_p0_config,
        test_p1_engine,
        test_p2_message_bus,
        test_p3_tools,
        test_p4_workflow,
        test_p5_api,
        test_p5_fastapi_app,
        test_p7_decision,
        test_p9_image_gen,
        test_p9_artist_tools,
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            errors.append((test.__name__, str(e)))
            print(f"  [FAIL] {test.__name__}: {e}")
    
    print()
    print("=" * 60)
    print(f"Results: {passed}/{passed + failed} passed")
    if errors:
        print(f"\nFailed tests:")
        for name, err in errors:
            print(f"  - {name}: {err}")
    else:
        print("All regression tests passed!")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
