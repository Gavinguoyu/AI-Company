"""
P9 美术集成 - 测试文件
测试内容:
1. ImageGenTool 初始化和基本功能
2. 美术Agent升级验证
3. 工具注册验证
4. 图片生成端到端测试（需要API Key）
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


def print_section(title: str):
    """打印测试章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_result(test_name: str, passed: bool, detail: str = ""):
    """打印测试结果"""
    icon = "✅" if passed else "❌"
    msg = f"{icon} {test_name}"
    if detail:
        msg += f" - {detail}"
    print(msg)


async def test_1_image_gen_tool_init():
    """测试1: ImageGenTool初始化"""
    print_section("测试1: ImageGenTool 初始化")
    
    from tools.image_gen_tool import ImageGenTool
    
    tool = ImageGenTool()
    
    # 检查客户端是否初始化
    has_client = tool.client is not None
    print_result(
        "客户端初始化",
        has_client,
        "Gemini Client已创建" if has_client else "GOOGLE_API_KEY未配置"
    )
    
    # 检查模型名
    print_result(
        "模型配置",
        "gemini" in tool.model,
        f"模型: {tool.model}"
    )
    
    # 检查统计信息
    stats = tool.get_generation_stats()
    print_result(
        "统计信息初始化",
        stats["total_generated"] == 0,
        f"已生成: {stats['total_generated']}, 失败: {stats['total_failed']}"
    )
    
    return has_client


async def test_2_tool_registration():
    """测试2: 工具注册验证"""
    print_section("测试2: 工具注册到ToolRegistry")
    
    from tools.tool_registry import ToolRegistry
    from tools.image_gen_tool import ImageGenTool
    
    registry = ToolRegistry()
    
    # 注册image_gen工具
    tool = ImageGenTool()
    registry.register_tool("image_gen", tool)
    
    # 验证注册成功
    has_tool = registry.has_tool("image_gen")
    print_result("工具注册", has_tool)
    
    # 获取工具实例
    retrieved = registry.get_tool("image_gen")
    print_result(
        "获取工具实例",
        retrieved is not None,
        f"类型: {type(retrieved).__name__}" if retrieved else "获取失败"
    )
    
    # 获取工具描述
    desc = registry.get_tool_description("image_gen")
    print_result(
        "工具描述",
        desc is not None and len(desc) > 0,
        f"{desc[:60]}..." if desc else "无描述"
    )
    
    # 列出所有工具
    all_tools = registry.list_tools()
    tool_names = [t["name"] for t in all_tools]
    print_result(
        "工具列表包含image_gen",
        "image_gen" in tool_names,
        f"已注册工具: {tool_names}"
    )
    
    # 检查工具方法
    for t in all_tools:
        if t["name"] == "image_gen":
            methods = t["methods"]
            has_generate = "generate" in methods
            has_game_asset = "generate_game_asset" in methods
            print_result(
                "generate方法",
                has_generate,
                "已暴露" if has_generate else "未找到"
            )
            print_result(
                "generate_game_asset方法",
                has_game_asset,
                "已暴露" if has_game_asset else "未找到"
            )
    
    return has_tool


async def test_3_artist_agent_upgrade():
    """测试3: 美术Agent升级验证"""
    print_section("测试3: 美术Agent升级")
    
    from tools.tool_registry import ToolRegistry
    from tools.image_gen_tool import ImageGenTool
    from tools.file_tool import FileTool
    
    # 确保工具已注册
    registry = ToolRegistry()
    if not registry.has_tool("image_gen"):
        registry.register_tool("image_gen", ImageGenTool())
    if not registry.has_tool("file"):
        registry.register_tool("file", FileTool())
    
    from agents.artist_agent import ArtistAgent
    
    artist = ArtistAgent()
    
    # 检查基本信息
    print_result(
        "Agent初始化",
        artist.agent_id == "artist",
        f"ID: {artist.agent_id}, 角色: {artist.role}"
    )
    
    # 检查已启用的工具
    available_tools = artist.get_available_tools()
    tool_names = [t["name"] for t in available_tools]
    
    has_file = "file" in tool_names
    has_image_gen = "image_gen" in tool_names
    
    print_result(
        "file工具已启用",
        has_file
    )
    print_result(
        "image_gen工具已启用",
        has_image_gen
    )
    
    # 检查系统提示词中包含Gemini相关内容
    has_gemini_ref = "Gemini" in artist.system_prompt
    print_result(
        "系统提示词包含Gemini引用",
        has_gemini_ref
    )
    
    # 检查关键方法
    has_generate_method = hasattr(artist, "generate_assets_from_spec")
    has_prompt_method = hasattr(artist, "create_prompt_for_asset")
    
    print_result(
        "generate_assets_from_spec方法",
        has_generate_method
    )
    print_result(
        "create_prompt_for_asset方法",
        has_prompt_method
    )
    
    return has_image_gen and has_generate_method


async def test_4_image_generation_e2e(skip_if_no_key: bool = True):
    """测试4: 图片生成端到端测试（需要API Key）"""
    print_section("测试4: 图片生成端到端测试")
    
    from config import Config
    
    if not Config.GOOGLE_API_KEY and skip_if_no_key:
        print("⏭️ 跳过: GOOGLE_API_KEY 未配置")
        return True
    
    from tools.image_gen_tool import ImageGenTool
    
    tool = ImageGenTool()
    
    if tool.client is None:
        print("⏭️ 跳过: Gemini客户端未初始化")
        return True
    
    # 测试目录
    test_output = Path(__file__).parent.parent / "test_output"
    test_output.mkdir(parents=True, exist_ok=True)
    
    # 生成简单测试图片
    print("正在生成测试图片（这可能需要几秒钟）...")
    
    result = await tool.generate(
        prompt="a simple pixel art apple, game asset, clean white background, 64x64 pixels",
        aspect_ratio="1:1",
        save_path=str(test_output / "test_apple.png")
    )
    
    print_result(
        "API调用",
        result["success"],
        result.get("error", "成功")
    )
    
    if result["success"]:
        file_exists = Path(result["path"]).exists()
        print_result(
            "图片文件保存",
            file_exists,
            f"路径: {result['path']}" if file_exists else "文件不存在"
        )
        
        if file_exists:
            file_size = Path(result["path"]).stat().st_size
            print_result(
                "图片文件大小",
                file_size > 0,
                f"{file_size / 1024:.1f} KB"
            )
        
        # 检查统计
        stats = tool.get_generation_stats()
        print_result(
            "统计更新",
            stats["total_generated"] >= 1,
            f"已生成: {stats['total_generated']}"
        )
    
    # 测试game_asset方法
    print("\n测试 generate_game_asset 方法...")
    
    asset_result = await tool.generate_game_asset(
        asset_spec={
            "name": "test_star",
            "description": "a golden star collectible item",
            "style": "pixel art"
        },
        project_dir=str(test_output)
    )
    
    print_result(
        "game_asset生成",
        asset_result["success"],
        asset_result.get("error", f"素材: {asset_result.get('asset_name')}")
    )
    
    if asset_result["success"]:
        asset_path = Path(asset_result["path"])
        print_result(
            "素材文件保存",
            asset_path.exists(),
            f"路径: {asset_result['path']}"
        )
    
    return result["success"]


async def test_5_workflow_import():
    """测试5: 工作流导入验证"""
    print_section("测试5: 工作流导入验证")
    
    try:
        from workflows.game_dev_workflow import GameDevWorkflow
        print_result("GameDevWorkflow 导入", True)
        
        # 检查是否有新方法
        has_artist_method = hasattr(
            GameDevWorkflow, "_phase_4_artist_assets"
        )
        print_result(
            "_phase_4_artist_assets 方法",
            has_artist_method
        )
        
        has_programmer_method = hasattr(
            GameDevWorkflow, "_phase_4_programmer_coding"
        )
        print_result(
            "_phase_4_programmer_coding 方法",
            has_programmer_method
        )
        
        has_parse_method = hasattr(
            GameDevWorkflow, "_parse_asset_list"
        )
        print_result(
            "_parse_asset_list 方法",
            has_parse_method
        )
        
        return has_artist_method and has_programmer_method
        
    except Exception as e:
        print_result("GameDevWorkflow 导入", False, str(e))
        return False


async def main():
    """运行所有P9测试"""
    print("\n" + "="*60)
    print("  P9 美术集成 - 测试套件")
    print("="*60)
    
    results = {}
    
    # 测试1: 工具初始化
    results["tool_init"] = await test_1_image_gen_tool_init()
    
    # 测试2: 工具注册
    results["tool_register"] = await test_2_tool_registration()
    
    # 测试3: Agent升级
    results["agent_upgrade"] = await test_3_artist_agent_upgrade()
    
    # 测试4: 端到端（需要API Key）
    results["e2e"] = await test_4_image_generation_e2e()
    
    # 测试5: 工作流导入
    results["workflow"] = await test_5_workflow_import()
    
    # 汇总
    print_section("测试汇总")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"  {icon} {name}")
    
    print(f"\n总计: {total} 项, 通过: {passed}, 失败: {failed}")
    
    if failed == 0:
        print("\n🎉 P9 美术集成测试全部通过！")
    else:
        print(f"\n⚠️ {failed}项测试未通过，请检查")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
