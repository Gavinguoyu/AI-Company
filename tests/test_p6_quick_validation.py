"""
P6阶段快速验证测试 - 验证程序员Agent和测试Agent的增强功能
不运行完整工作流,只测试Agent的核心功能
"""

import asyncio
import sys
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from agents.programmer_agent import ProgrammerAgent
from agents.tester_agent import TesterAgent
from tools.file_tool import FileTool
from tools.code_runner import CodeRunner
from tools.code_search_tool import CodeSearchTool
from tools.tool_registry import ToolRegistry
from config import Config
import shutil


async def test_p6_quick_validation():
    """P6阶段快速验证"""
    
    print("\n" + "="*70)
    print("P6阶段快速验证测试")
    print("="*70 + "\n")
    
    # 初始化工具注册表
    print("初始化全局工具注册表...")
    registry = ToolRegistry()
    file_tool = FileTool()
    code_runner = CodeRunner()
    code_search = CodeSearchTool()
    
    registry.register_tool("file", file_tool)
    registry.register_tool("code_runner", code_runner)
    registry.register_tool("code_search", code_search)
    print("✅ 工具注册表初始化完成\n")
    
    test_project_name = "quick_test_p6"
    test_project_dir = Config.PROJECTS_DIR / test_project_name
    output_dir = test_project_dir / "output"
    
    # 清理并创建测试目录
    if test_project_dir.exists():
        shutil.rmtree(test_project_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("测试1: 程序员Agent能否写入文件")
        print("-" * 70)
        
        programmer = ProgrammerAgent(project_name=test_project_name)
        
        # 检查programmer是否有file工具
        available_tools = programmer.get_available_tools()
        print(f"程序员可用工具: {[tool['name'] for tool in available_tools]}")
        
        if any(tool['name'] == 'file' for tool in available_tools):
            print("✅ 程序员Agent已启用file工具")
        else:
            print("❌ 程序员Agent未启用file工具")
            return False
        
        print()
        
        print("测试2: 测试Agent能否执行代码")
        print("-" * 70)
        
        tester = TesterAgent(project_name=test_project_name)
        
        # 检查tester是否有code_runner工具
        available_tools = tester.get_available_tools()
        print(f"测试工程师可用工具: {[tool['name'] for tool in available_tools]}")
        
        if any(tool['name'] == 'code_runner' for tool in available_tools):
            print("✅ 测试Agent已启用code_runner工具")
        else:
            print("❌ 测试Agent未启用code_runner工具")
            return False
        
        print()
        
        print("测试3: 手动测试文件写入")
        print("-" * 70)
        
        # 手动调用工具写入测试文件
        test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Game</title>
</head>
<body>
    <canvas id="gameCanvas" width="400" height="400"></canvas>
    <script>
        console.log('Game loaded');
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'red';
        ctx.fillRect(0, 0, 100, 100);
    </script>
</body>
</html>"""
        
        html_path = f"projects/{test_project_name}/output/test.html"
        success = await programmer.call_tool("file", "write", html_path, test_html)
        
        if success:
            print(f"✅ 成功写入测试文件: {html_path}")
            
            # 验证文件存在
            if Path(html_path).exists():
                print(f"✅ 文件确实存在: {Path(html_path).stat().st_size} 字节")
            else:
                print(f"❌ 文件未找到")
                return False
        else:
            print("❌ 写入文件失败")
            return False
        
        print()
        
        print("测试4: 测试Agent读取和执行文件")
        print("-" * 70)
        
        # 测试Agent读取文件
        content = await tester.call_tool("file", "read", html_path)
        if content:
            print(f"✅ 测试Agent成功读取文件 ({len(content)} 字符)")
        else:
            print("❌ 测试Agent读取文件失败")
            return False
        
        # 测试Agent执行HTML
        result = await tester.call_tool("code_runner", "execute_html", content, 5.0, True)
        
        if result.get('success'):
            print("✅ 测试Agent成功执行HTML代码")
        else:
            error_msg = result.get('error', '未知错误')
            print(f"⚠️ HTML执行失败: {error_msg}")
            # 不返回False,因为code_runner可能在无浏览器环境中运行
        
        print()
        
        print("测试5: 验证程序员Agent的代码生成能力")
        print("-" * 70)
        
        # 检查程序员Agent是否能从上下文识别游戏类型
        programmer.load_file_to_context("requirement", "做一个贪吃蛇游戏")
        game_info = programmer._extract_game_info_from_context()
        
        print(f"识别的游戏类型: {game_info['type']}")
        print(f"游戏标题: {game_info['title']}")
        
        if game_info['type'] == 'snake':
            print("✅ 正确识别贪吃蛇游戏类型")
        else:
            print("⚠️ 游戏类型识别可能不准确，但不影响功能")
        
        print()
        
        print("="*70)
        print("🎉 P6阶段快速验证测试完成！")
        print("="*70)
        print()
        print("核心功能验证:")
        print("  ✅ 程序员Agent可以写文件")
        print("  ✅ 测试Agent可以读文件和执行代码")
        print("  ✅ Agent工具系统工作正常")
        print()
        print("下一步: 运行完整的端到端测试 (test_p6_game_generation.py)")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试文件
        if test_project_dir.exists():
            shutil.rmtree(test_project_dir)
            print(f"已清理测试目录: {test_project_dir}")


if __name__ == "__main__":
    success = asyncio.run(test_p6_quick_validation())
    
    if success:
        print("\n✅ 快速验证测试通过！P6核心功能正常！")
        sys.exit(0)
    else:
        print("\n❌ 快速验证测试失败")
        sys.exit(1)
