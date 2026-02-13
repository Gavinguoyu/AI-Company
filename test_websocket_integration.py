"""
测试WebSocket集成
验证创建项目后，Agent的工作过程是否能推送到前端
"""

import sys
import io

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime

# 配置
API_BASE = "http://localhost:8000"
WS_BASE = "ws://localhost:8000"
CLIENT_ID = "test_client_123"

# 存储收到的消息
received_messages = []


async def websocket_listener():
    """WebSocket监听器，接收服务器推送的消息"""
    uri = f"{WS_BASE}/ws/{CLIENT_ID}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ WebSocket已连接: {uri}\n")
            
            # 循环接收消息
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=120.0)
                    data = json.loads(message)
                    
                    # 记录消息
                    received_messages.append(data)
                    
                    # 打印消息
                    event = data.get("event", "unknown")
                    timestamp = data.get("timestamp", "")
                    
                    if event == "connected":
                        print(f"[{timestamp}] 🔗 连接成功")
                    
                    elif event == "agent_message":
                        from_agent = data.get("from", "unknown")
                        to_agent = data.get("to", "unknown")
                        content = data.get("content", "")[:100]
                        print(f"[{timestamp}] 💬 {from_agent} → {to_agent}: {content}...")
                    
                    elif event == "agent_status":
                        agent_id = data.get("agent_id", "unknown")
                        status = data.get("status", "unknown")
                        task = data.get("current_task", "")
                        print(f"[{timestamp}] 🤖 {agent_id}: {status} - {task}")
                    
                    elif event == "phase_change":
                        new_phase = data.get("new_phase", "unknown")
                        progress = data.get("progress", 0)
                        print(f"[{timestamp}] 📊 阶段变化: {new_phase} ({progress:.1f}%)")
                    
                    elif event == "error_alert":
                        error_msg = data.get("error_message", "")
                        print(f"[{timestamp}] ❌ 错误: {error_msg}")
                    
                    else:
                        print(f"[{timestamp}] 📡 收到消息: {event}")
                
                except asyncio.TimeoutError:
                    print("⏰ WebSocket监听超时")
                    break
                except Exception as e:
                    print(f"❌ 接收消息错误: {e}")
                    break
    
    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")


def create_project():
    """创建测试项目"""
    print("="*60)
    print("创建测试项目...")
    print("="*60 + "\n")
    
    project_data = {
        "project_name": "test_ws_game",
        "game_idea": "做一个简单的打砖块游戏，玩家控制挡板弹球击碎砖块"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/project/start",
            json=project_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 项目创建成功: {result['project_id']}\n")
            return result['project_id']
        else:
            print(f"❌ 项目创建失败: {response.status_code}")
            print(f"   响应: {response.text}\n")
            return None
    
    except Exception as e:
        print(f"❌ API调用失败: {e}\n")
        return None


async def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("WebSocket集成测试")
    print("="*60 + "\n")
    
    # 1. 启动WebSocket监听器
    print("1️⃣ 启动WebSocket监听器...")
    ws_task = asyncio.create_task(websocket_listener())
    
    # 等待连接建立
    await asyncio.sleep(2)
    
    # 2. 创建项目
    print("\n2️⃣ 创建项目...")
    project_id = create_project()
    
    if not project_id:
        print("❌ 测试失败：无法创建项目")
        ws_task.cancel()
        return
    
    # 3. 等待消息
    print("3️⃣ 等待Agent消息...\n")
    print("-"*60)
    
    # 等待工作流执行（最多120秒）
    try:
        await asyncio.wait_for(ws_task, timeout=120.0)
    except asyncio.TimeoutError:
        print("\n⏰ 测试超时（120秒）")
    except asyncio.CancelledError:
        pass
    
    # 4. 统计结果
    print("\n" + "="*60)
    print("测试结果统计")
    print("="*60)
    
    # 统计各类消息数量
    message_counts = {}
    for msg in received_messages:
        event = msg.get("event", "unknown")
        message_counts[event] = message_counts.get(event, 0) + 1
    
    print(f"\n总共收到 {len(received_messages)} 条消息:\n")
    for event, count in sorted(message_counts.items()):
        print(f"  - {event}: {count} 条")
    
    # 检查是否收到关键消息
    print("\n关键消息检查:")
    
    has_agent_message = any(msg.get("event") == "agent_message" for msg in received_messages)
    has_agent_status = any(msg.get("event") == "agent_status" for msg in received_messages)
    has_phase_change = any(msg.get("event") == "phase_change" for msg in received_messages)
    
    print(f"  ✅ Agent消息" if has_agent_message else "  ❌ Agent消息")
    print(f"  ✅ Agent状态" if has_agent_status else "  ❌ Agent状态")
    print(f"  ✅ 阶段变化" if has_phase_change else "  ❌ 阶段变化")
    
    # 最终判断
    print("\n" + "="*60)
    if has_agent_message and has_agent_status and has_phase_change:
        print("✅ WebSocket集成测试通过！")
        print("   前端应该能看到Agent的工作过程了。")
    else:
        print("❌ WebSocket集成测试失败")
        print("   前端可能看不到Agent的工作过程。")
    print("="*60 + "\n")


if __name__ == "__main__":
    # 检查服务器是否运行
    print("检查服务器状态...")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器正在运行\n")
        else:
            print("❌ 服务器响应异常")
            exit(1)
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("   请先启动服务器: python backend/main.py\n")
        exit(1)
    
    # 运行测试
    asyncio.run(main())
