"""
P3阶段测试脚本 - 工具系统测试

测试内容:
1. 文件工具 (FileTool)
2. 代码执行工具 (CodeRunner)
3. 代码搜索工具 (CodeSearchTool)
4. 工具注册机制 (ToolRegistry, AgentToolkit)
5. Agent集成工具系统
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from tools.file_tool import FileTool
from tools.code_runner import CodeRunner
from tools.code_search_tool import CodeSearchTool
from tools.tool_registry import ToolRegistry, AgentToolkit, register_all_tools
from engine.agent import Agent


def print_header(title):
    """打印测试标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_section(title):
    """打印测试小节"""
    print("\n" + "-"*70)
    print(f"  {title}")
    print("-"*70)


async def test_file_tool():
    """测试文件工具"""
    print_header("1. 测试文件工具 (FileTool)")
    
    file_tool = FileTool()
    test_file = "test_data/test_file.txt"
    test_content = "这是一个测试文件\nHello, AI Company!\n"
    
    try:
        # 测试写入
        print_section("1.1 测试文件写入")
        await file_tool.write(test_file, test_content)
        print(f"✅ 成功写入文件: {test_file}")
        
        # 测试读取
        print_section("1.2 测试文件读取")
        read_content = await file_tool.read(test_file)
        assert read_content == test_content, "读取内容与写入内容不一致"
        print(f"✅ 成功读取文件，内容正确")
        print(f"内容: {read_content[:50]}...")
        
        # 测试追加
        print_section("1.3 测试文件追加")
        append_text = "追加的内容\n"
        await file_tool.append(test_file, append_text)
        read_content = await file_tool.read(test_file)
        assert append_text in read_content, "追加内容未找到"
        print(f"✅ 成功追加内容")
        
        # 测试文件存在性检查
        print_section("1.4 测试文件检查")
        assert file_tool.exists(test_file), "文件应该存在"
        assert file_tool.is_file(test_file), "应该是文件"
        assert not file_tool.is_directory(test_file), "不应该是目录"
        print(f"✅ 文件检查功能正常")
        
        # 测试列出目录
        print_section("1.5 测试列出目录")
        items = await file_tool.list_directory("test_data")
        print(f"✅ 找到 {len(items)} 个项目")
        for item in items:
            print(f"  - {item['name']} ({item['type']})")
        
        # 测试获取文件信息
        print_section("1.6 测试获取文件信息")
        info = file_tool.get_file_info(test_file)
        print(f"✅ 文件信息: {info['name']}, {info['size']} 字节")
        
        # 测试删除
        print_section("1.7 测试删除文件")
        await file_tool.delete(test_file)
        assert not file_tool.exists(test_file), "文件应该已被删除"
        print(f"✅ 成功删除文件")
        
        print("\n✅ 文件工具所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 文件工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_code_runner():
    """测试代码执行工具"""
    print_header("2. 测试代码执行工具 (CodeRunner)")
    
    code_runner = CodeRunner()
    
    try:
        # 测试JavaScript语法检查
        print_section("2.1 测试JavaScript语法检查")
        js_code = """
        function hello() {
            console.log("Hello, World!");
        }
        hello();
        """
        result = await code_runner.validate_syntax(js_code, "javascript")
        assert result["valid"], "JavaScript语法应该有效"
        print(f"✅ JavaScript语法检查通过")
        
        # 测试HTML语法检查
        print_section("2.2 测试HTML语法检查")
        html_code = """
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body><h1>Hello</h1></body>
        </html>
        """
        result = await code_runner.validate_syntax(html_code, "html")
        assert result["valid"], "HTML语法应该有效"
        print(f"✅ HTML语法检查通过")
        
        # 测试执行HTML（创建文件）
        print_section("2.3 测试HTML文件创建")
        result = await code_runner.execute_html(html_code, check_only=False)
        assert result["success"], "HTML执行应该成功"
        print(f"✅ HTML文件已创建: {result['file_path']}")
        
        # 测试执行JavaScript（如果Node.js可用）
        print_section("2.4 测试JavaScript执行")
        js_code = """
        console.log("测试JavaScript执行");
        const sum = 1 + 2;
        console.log("1 + 2 =", sum);
        """
        result = await code_runner.execute_js(js_code, use_node=True)
        if result["success"] and result["exit_code"] == 0:
            print(f"✅ JavaScript执行成功")
            print(f"输出: {result['output']}")
        else:
            print(f"⚠️  Node.js未安装或不可用: {result['output']}")
        
        # 清理临时文件
        print_section("2.5 清理临时文件")
        count = code_runner.cleanup_temp_files()
        print(f"✅ 清理了 {count} 个临时文件")
        
        print("\n✅ 代码执行工具所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 代码执行工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_code_search():
    """测试代码搜索工具"""
    print_header("3. 测试代码搜索工具 (CodeSearchTool)")
    
    code_search = CodeSearchTool()
    
    try:
        # 创建测试代码文件
        print_section("3.1 创建测试代码文件")
        file_tool = FileTool()
        test_code = """
        // Snake Game
        class Snake {
            constructor(x, y) {
                this.x = x;
                this.y = y;
            }
            
            move(direction) {
                console.log("Moving", direction);
            }
        }
        
        function createFood(x, y) {
            return { x, y, type: 'apple' };
        }
        
        const GAME_CONFIG = {
            width: 800,
            height: 600
        };
        """
        await file_tool.write("test_data/snake_game.js", test_code)
        print(f"✅ 测试代码文件已创建")
        
        # 测试搜索函数
        print_section("3.2 搜索函数定义")
        results = await code_search.search_function("createFood", "test_data", "*.js")
        assert len(results) > 0, "应该找到createFood函数"
        print(f"✅ 找到函数 'createFood': {len(results)} 个结果")
        for result in results:
            print(f"  - {result['file']}:{result['line']} - {result['content']}")
        
        # 测试搜索类
        print_section("3.3 搜索类定义")
        results = await code_search.search_class("Snake", "test_data", "*.js")
        assert len(results) > 0, "应该找到Snake类"
        print(f"✅ 找到类 'Snake': {len(results)} 个结果")
        for result in results:
            print(f"  - {result['file']}:{result['line']} - {result['content']}")
        
        # 测试搜索变量
        print_section("3.4 搜索变量定义")
        results = await code_search.search_variable("GAME_CONFIG", "test_data", "*.js")
        assert len(results) > 0, "应该找到GAME_CONFIG变量"
        print(f"✅ 找到变量 'GAME_CONFIG': {len(results)} 个结果")
        
        # 测试搜索所有类型
        print_section("3.5 搜索所有类型")
        results = await code_search.search_all("Snake", "test_data", "*.js")
        print(f"✅ 搜索结果:")
        print(f"  - 函数: {len(results['functions'])} 个")
        print(f"  - 类: {len(results['classes'])} 个")
        print(f"  - 变量: {len(results['variables'])} 个")
        print(f"  - 总计: {results['total']} 个")
        
        # 测试获取文件导入
        print_section("3.6 获取文件导入语句")
        imports = code_search.get_file_imports("test_data/snake_game.js")
        print(f"✅ 找到 {len(imports)} 个导入语句")
        
        print("\n✅ 代码搜索工具所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 代码搜索工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tool_registry():
    """测试工具注册机制"""
    print_header("4. 测试工具注册机制")
    
    try:
        # 测试注册所有工具
        print_section("4.1 注册所有内置工具")
        register_all_tools()
        print(f"✅ 所有工具已注册")
        
        # 测试获取工具注册表
        print_section("4.2 列出所有工具")
        registry = ToolRegistry()
        tools = registry.list_tools()
        print(f"✅ 已注册 {len(tools)} 个工具:")
        for tool in tools:
            print(f"  - {tool['name']} ({tool['type']})")
            print(f"    方法: {', '.join(tool['methods'][:5])}...")
        
        # 测试获取工具
        print_section("4.3 获取工具实例")
        file_tool = registry.get_tool("file")
        assert file_tool is not None, "应该能获取file工具"
        print(f"✅ 成功获取工具: file")
        
        # 测试调用工具
        print_section("4.4 调用工具方法")
        result = await registry.call_tool("file", "exists", "test_data")
        print(f"✅ 调用工具成功，结果: {result}")
        
        print("\n✅ 工具注册机制所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 工具注册机制测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_toolkit():
    """测试Agent工具包"""
    print_header("5. 测试Agent工具包")
    
    try:
        # 确保工具已注册
        register_all_tools()
        
        # 创建Agent工具包
        print_section("5.1 创建Agent工具包")
        toolkit = AgentToolkit("test_agent")
        print(f"✅ 创建Agent工具包: test_agent")
        
        # 启用工具
        print_section("5.2 启用工具")
        toolkit.enable_tool("file")
        toolkit.enable_tool("code_search")
        print(f"✅ 已启用工具: file, code_search")
        
        # 获取可用工具
        print_section("5.3 获取可用工具")
        tools = toolkit.get_available_tools()
        print(f"✅ 可用工具 {len(tools)} 个:")
        for tool in tools:
            print(f"  - {tool['name']}")
        
        # 测试工具调用
        print_section("5.4 调用工具")
        result = await toolkit.call("file", "exists", "test_data")
        print(f"✅ 调用成功，结果: {result}")
        
        # 测试未启用工具的权限
        print_section("5.5 测试权限控制")
        try:
            await toolkit.call("code_runner", "execute_js", "console.log('test')")
            print(f"❌ 应该抛出权限错误")
            return False
        except PermissionError:
            print(f"✅ 权限控制正常，未启用的工具无法调用")
        
        # 测试生成工具说明
        print_section("5.6 生成工具说明（用于Prompt）")
        prompt = toolkit.get_tool_info_for_prompt()
        print(f"✅ 工具说明已生成 ({len(prompt)} 字符)")
        print(f"预览:\n{prompt[:200]}...")
        
        print("\n✅ Agent工具包所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ Agent工具包测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_with_tools():
    """测试Agent集成工具系统"""
    print_header("6. 测试Agent集成工具系统")
    
    try:
        # 注册所有工具
        register_all_tools()
        
        # 创建带工具的Agent
        print_section("6.1 创建带工具的Agent")
        agent = Agent(
            agent_id="test_programmer",
            role="测试程序员",
            system_prompt="你是一个测试程序员，可以使用文件工具和代码搜索工具。",
            tools=["file", "code_search"]
        )
        print(f"✅ 创建Agent成功")
        
        # 检查Agent状态
        print_section("6.2 检查Agent状态")
        status = agent.get_status()
        print(f"✅ Agent ID: {status['agent_id']}")
        print(f"✅ 可用工具: {', '.join(status['tools'])}")
        
        # 测试Agent调用工具
        print_section("6.3 Agent调用文件工具")
        test_file = "test_data/agent_test.txt"
        test_content = "Agent使用文件工具写入的内容"
        await agent.call_tool("file", "write", test_file, test_content)
        print(f"✅ Agent成功写入文件")
        
        read_content = await agent.call_tool("file", "read", test_file)
        assert read_content == test_content, "读取内容应该与写入一致"
        print(f"✅ Agent成功读取文件，内容正确")
        
        # 测试Agent调用代码搜索
        print_section("6.4 Agent调用代码搜索工具")
        results = await agent.call_tool("code_search", "search_class", "Snake", "test_data", "*.js")
        print(f"✅ Agent成功搜索代码，找到 {len(results)} 个结果")
        
        # 测试获取可用工具列表
        print_section("6.5 获取Agent可用工具")
        tools = agent.get_available_tools()
        print(f"✅ Agent可用工具: {len(tools)} 个")
        for tool in tools:
            print(f"  - {tool['name']} ({tool['type']})")
        
        # 测试动态启用工具
        print_section("6.6 动态启用新工具")
        agent.enable_tool("code_runner")
        status = agent.get_status()
        assert "code_runner" in status['tools'], "code_runner应该已启用"
        print(f"✅ 成功启用新工具: code_runner")
        print(f"当前可用工具: {', '.join(status['tools'])}")
        
        print("\n✅ Agent集成工具系统所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ Agent集成工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("\n" + "="*70)
    print("  P3阶段测试 - 工具系统")
    print("="*70)
    print("\n开始测试...\n")
    
    results = {
        "文件工具": False,
        "代码执行工具": False,
        "代码搜索工具": False,
        "工具注册机制": False,
        "Agent工具包": False,
        "Agent集成工具": False
    }
    
    # 运行所有测试
    results["文件工具"] = await test_file_tool()
    results["代码执行工具"] = await test_code_runner()
    results["代码搜索工具"] = await test_code_search()
    results["工具注册机制"] = await test_tool_registry()
    results["Agent工具包"] = await test_agent_toolkit()
    results["Agent集成工具"] = await test_agent_with_tools()
    
    # 汇总结果
    print("\n" + "="*70)
    print("  测试结果汇总")
    print("="*70 + "\n")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 P3阶段所有测试通过！工具系统实现完成！")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
