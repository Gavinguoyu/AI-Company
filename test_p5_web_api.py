"""
P5 阶段测试脚本 - Web 后端 API 测试

测试内容:
1. FastAPI 应用启动
2. HTTP 接口功能
3. WebSocket 连接和消息推送
"""

import asyncio
import sys
import os
from pathlib import Path
import json
import httpx
import websockets
from datetime import datetime

# 设置控制台编码为 UTF-8（Windows 兼容）
if sys.platform == "win32":
    try:
        os.system("chcp 65001 > nul 2>&1")
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from config import Config


class TestResults:
    """测试结果记录器"""
    
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.total += 1
        self.passed += 1
        print(f"  ✅ {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.total += 1
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ❌ {test_name}")
        print(f"     错误: {error}")
    
    def print_summary(self):
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        print(f"总测试数: {self.total}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print(f"通过率: {self.passed/self.total*100:.1f}%" if self.total > 0 else "通过率: 0%")
        
        if self.errors:
            print("\n失败的测试:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        print("="*60 + "\n")
        
        return self.failed == 0


# 全局测试结果
results = TestResults()


async def test_http_api():
    """测试 HTTP API 接口"""
    print("\n📡 测试 HTTP API 接口")
    print("-" * 60)
    
    base_url = f"http://{Config.SERVER_HOST}:{Config.SERVER_PORT}"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 测试 1: 健康检查
        try:
            response = await client.get(f"{base_url}/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            results.add_pass("健康检查接口")
        except Exception as e:
            results.add_fail("健康检查接口", str(e))
        
        # 测试 2: 创建项目
        try:
            response = await client.post(
                f"{base_url}/api/project/start",
                json={
                    "game_idea": "做一个测试用的贪吃蛇游戏",
                    "project_name": "test_snake"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "project_id" in data
            
            # 保存项目ID用于后续测试
            global test_project_id
            test_project_id = data["project_id"]
            
            results.add_pass("创建项目接口")
        except Exception as e:
            results.add_fail("创建项目接口", str(e))
        
        # 测试 3: 查询项目状态
        try:
            response = await client.get(f"{base_url}/api/project/{test_project_id}/status")
            assert response.status_code == 200
            data = response.json()
            assert data["project_id"] == test_project_id
            assert "status" in data
            results.add_pass("查询项目状态接口")
        except Exception as e:
            results.add_fail("查询项目状态接口", str(e))
        
        # 测试 4: 获取项目列表
        try:
            response = await client.get(f"{base_url}/api/projects")
            assert response.status_code == 200
            data = response.json()
            assert "total" in data
            assert "projects" in data
            assert data["total"] >= 1  # 至少有刚创建的项目
            results.add_pass("获取项目列表接口")
        except Exception as e:
            results.add_fail("获取项目列表接口", str(e))
        
        # 测试 5: 删除项目
        try:
            response = await client.delete(f"{base_url}/api/project/{test_project_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            results.add_pass("删除项目接口")
        except Exception as e:
            results.add_fail("删除项目接口", str(e))
        
        # 测试 6: 查询不存在的项目（应该返回 404）
        try:
            response = await client.get(f"{base_url}/api/project/nonexistent/status")
            assert response.status_code == 404
            results.add_pass("错误处理（404）")
        except Exception as e:
            results.add_fail("错误处理（404）", str(e))


async def test_websocket():
    """测试 WebSocket 连接和消息推送"""
    print("\n🔌 测试 WebSocket 连接")
    print("-" * 60)
    
    ws_url = f"ws://{Config.SERVER_HOST}:{Config.SERVER_PORT}/ws/test_client_123"
    
    try:
        # 测试 1: 建立连接
        async with websockets.connect(ws_url) as websocket:
            results.add_pass("WebSocket 连接建立")
            
            # 测试 2: 接收欢迎消息
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                assert data["event"] == "connected"
                assert data["client_id"] == "test_client_123"
                results.add_pass("接收欢迎消息")
            except Exception as e:
                results.add_fail("接收欢迎消息", str(e))
            
            # 测试 3: 发送 ping，接收 pong
            try:
                await websocket.send(json.dumps({"type": "ping"}))
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                assert data["event"] == "pong"
                results.add_pass("心跳检测 (ping/pong)")
            except Exception as e:
                results.add_fail("心跳检测 (ping/pong)", str(e))
            
            # 测试 4: 订阅项目
            try:
                await websocket.send(json.dumps({
                    "type": "subscribe_project",
                    "project_id": "test_project_123"
                }))
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                assert data["event"] == "subscribed"
                results.add_pass("订阅项目")
            except Exception as e:
                results.add_fail("订阅项目", str(e))
            
            # 测试 5: 取消订阅
            try:
                await websocket.send(json.dumps({
                    "type": "unsubscribe_project",
                    "project_id": "test_project_123"
                }))
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                assert data["event"] == "unsubscribed"
                results.add_pass("取消订阅项目")
            except Exception as e:
                results.add_fail("取消订阅项目", str(e))
    
    except Exception as e:
        results.add_fail("WebSocket 连接建立", str(e))


async def test_concurrent_websockets():
    """测试多个 WebSocket 并发连接"""
    print("\n👥 测试并发 WebSocket 连接")
    print("-" * 60)
    
    ws_base_url = f"ws://{Config.SERVER_HOST}:{Config.SERVER_PORT}/ws"
    
    async def connect_client(client_id: str):
        """单个客户端连接"""
        try:
            async with websockets.connect(f"{ws_base_url}/{client_id}") as ws:
                # 接收欢迎消息
                await asyncio.wait_for(ws.recv(), timeout=5.0)
                # 发送 ping
                await ws.send(json.dumps({"type": "ping"}))
                # 接收 pong
                await asyncio.wait_for(ws.recv(), timeout=5.0)
                return True
        except:
            return False
    
    # 同时连接 5 个客户端
    try:
        tasks = [connect_client(f"client_{i}") for i in range(5)]
        results_list = await asyncio.gather(*tasks)
        
        success_count = sum(results_list)
        if success_count == 5:
            results.add_pass(f"并发连接（5个客户端同时连接）")
        else:
            results.add_fail(f"并发连接", f"只有 {success_count}/5 个客户端成功")
    except Exception as e:
        results.add_fail("并发连接", str(e))


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("P5 阶段测试 - Web 后端 API")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试目标: http://{Config.SERVER_HOST}:{Config.SERVER_PORT}")
    print("="*60)
    
    # 等待服务器启动
    print("\n⏳ 等待服务器响应...")
    await asyncio.sleep(2)  # 等待2秒
    
    try:
        # 测试 HTTP API
        await test_http_api()
        
        # 测试 WebSocket
        await test_websocket()
        
        # 测试并发 WebSocket
        await test_concurrent_websockets()
        
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 打印测试结果
    success = results.print_summary()
    
    if success:
        print("🎉 所有测试通过！P5 阶段开发完成！")
        return 0
    else:
        print("⚠️  部分测试失败，请修复后重新测试")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
