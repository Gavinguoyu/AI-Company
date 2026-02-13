"""
P10 端到端测试运行器
启动一个计数器游戏项目，监控完整工作流执行过程
"""

import asyncio
import sys
import io
import time
import json
from pathlib import Path

# 设置Windows控制台编码为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import httpx


BASE_URL = "http://localhost:8000"


async def start_project():
    """启动一个计数器游戏项目"""
    print("=" * 60)
    print("🎯 P10 端到端测试: 开发一个计数器游戏")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 健康检查
        print("\n📡 Step 1: 健康检查...")
        health = await client.get(f"{BASE_URL}/api/health")
        assert health.status_code == 200, f"健康检查失败: {health.status_code}"
        print(f"  ✅ 服务正常: {health.json()['status']}")
        
        # 2. 启动项目
        print("\n🚀 Step 2: 启动计数器游戏项目...")
        response = await client.post(
            f"{BASE_URL}/api/project/start",
            json={
                "game_idea": "一个简单的计数器游戏：屏幕中央显示一个数字(从0开始)，有两个按钮：+1按钮和-1按钮。点击按钮数字会对应变化。要有简洁美观的界面。",
                "project_name": "p10_counter_e2e"
            }
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"  ❌ 启动失败: {response.text}")
            return None
        
        result = response.json()
        project_id = result["project_id"]
        print(f"  ✅ 项目已启动: {project_id}")
        print(f"  消息: {result['message']}")
        
        return project_id


async def monitor_project(project_id: str):
    """监控项目执行进度"""
    print(f"\n⏱️ Step 3: 监控项目进度 (最长等待30分钟)...")
    print("-" * 60)
    
    max_wait = 1800  # 30分钟
    poll_interval = 15  # 每15秒查一次
    elapsed = 0
    last_phase = ""
    
    while elapsed < max_wait:
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{BASE_URL}/api/project/{project_id}/status")
                
                if response.status_code != 200:
                    print(f"  ⚠️ {elapsed}s | 查询状态失败: {response.status_code}")
                    continue
                
                status = response.json()
                current_phase = status.get('current_phase', '未知')
                progress = status.get('progress', 0)
                project_status = status.get('status', '未知')
                agents = status.get('agents_status', {})
                
                # 只在阶段变化时打印详细信息
                if current_phase != last_phase:
                    print(f"\n  📍 [{elapsed}s] 阶段变化: {last_phase or '无'} → {current_phase}")
                    print(f"     状态: {project_status} | 进度: {progress:.0f}%")
                    print(f"     Agent状态: {json.dumps(agents, ensure_ascii=False)}")
                    last_phase = current_phase
                else:
                    # 简洁打印
                    active_agents = [k for k, v in agents.items() if v != 'idle']
                    active_str = ", ".join(active_agents) if active_agents else "无活跃Agent"
                    print(f"  ⏱️ [{elapsed}s] {current_phase} | {project_status} | {progress:.0f}% | 活跃: {active_str}")
                
                # 检查是否完成
                if project_status == 'completed':
                    print(f"\n  🎉 项目完成！总耗时: {elapsed}秒")
                    return True
                elif project_status == 'failed':
                    print(f"\n  ❌ 项目失败！总耗时: {elapsed}秒")
                    return False
                    
        except Exception as e:
            print(f"  ⚠️ [{elapsed}s] 查询异常: {e}")
    
    print(f"\n  ⏰ 超时！已等待{max_wait}秒")
    return False


async def verify_output(project_id: str):
    """验证项目输出文件"""
    print(f"\n📂 Step 4: 验证输出文件...")
    print("-" * 60)
    
    # 从project_id提取project_name
    # project_id格式: {project_name}_{timestamp}
    # 实际项目目录用的是project_name
    project_name = "p10_counter_e2e"
    
    project_dir = Path("projects") / project_name
    output_dir = project_dir / "output"
    knowledge_dir = project_dir / "shared_knowledge"
    
    checks = {
        "项目目录存在": project_dir.exists(),
        "输出目录存在": output_dir.exists(),
        "知识库目录存在": knowledge_dir.exists(),
        "index.html存在": (output_dir / "index.html").exists(),
        "game.js存在": (output_dir / "game.js").exists(),
        "game_design_doc.md存在": (knowledge_dir / "game_design_doc.md").exists(),
        "tech_design_doc.md存在": (knowledge_dir / "tech_design_doc.md").exists(),
        "project_rules.yaml存在": (knowledge_dir / "project_rules.yaml").exists(),
        "bug_tracker.yaml存在": (knowledge_dir / "bug_tracker.yaml").exists(),
        "decision_log.yaml存在": (knowledge_dir / "decision_log.yaml").exists(),
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    # 检查HTML文件大小
    html_path = output_dir / "index.html"
    js_path = output_dir / "game.js"
    
    if html_path.exists():
        size = html_path.stat().st_size
        print(f"\n  📄 index.html 大小: {size} bytes")
        if size < 100:
            print(f"  ⚠️ HTML文件过小，可能是空文件")
            all_passed = False
    
    if js_path.exists():
        size = js_path.stat().st_size
        print(f"  📄 game.js 大小: {size} bytes")
        if size < 100:
            print(f"  ⚠️ JS文件过小，可能是空文件")
            all_passed = False
    
    # 检查美术素材
    assets_dir = output_dir / "assets"
    if assets_dir.exists():
        asset_files = list(assets_dir.glob("*"))
        print(f"\n  🎨 美术素材: {len(asset_files)} 个文件")
        for f in asset_files[:10]:
            print(f"    - {f.name} ({f.stat().st_size} bytes)")
    
    return all_passed


async def main():
    """主测试流程"""
    start_time = time.time()
    
    try:
        # 1. 启动项目
        project_id = await start_project()
        if not project_id:
            print("\n❌ 无法启动项目，测试终止")
            return 1
        
        # 2. 监控进度
        success = await monitor_project(project_id)
        
        # 3. 验证输出
        output_ok = await verify_output(project_id)
        
        # 4. 总结
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("📊 P10 端到端测试总结")
        print("=" * 60)
        print(f"  项目ID: {project_id}")
        print(f"  工作流完成: {'✅' if success else '❌'}")
        print(f"  输出验证: {'✅' if output_ok else '❌'}")
        print(f"  总耗时: {total_time:.0f}秒 ({total_time/60:.1f}分钟)")
        print("=" * 60)
        
        if success and output_ok:
            print("🎉 端到端测试通过！")
            return 0
        else:
            print("⚠️ 端到端测试部分失败，需要排查")
            return 1
            
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
