"""
文件: api/websocket_handler.py
职责: WebSocket 实时通信处理，推送 Agent 活动和消息
依赖: fastapi, websockets
被依赖: main.py
关键接口:
  - WebSocket /ws/{client_id} - 建立 WebSocket 连接
  - broadcast_message() - 广播消息给所有连接的客户端
  - send_to_client() - 发送消息给特定客户端
"""

import sys
from pathlib import Path
from typing import Dict, Set, Any
import asyncio
import json
from datetime import datetime

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from config import Config
from utils.logger import setup_logger


# 创建路由器
router = APIRouter(tags=["WebSocket"])

# 创建日志器
logger = setup_logger("websocket", log_level=Config.LOG_LEVEL, log_to_file=Config.LOG_TO_FILE)


# =====================================================
# WebSocket 连接管理
# =====================================================

class ConnectionManager:
    """
    WebSocket 连接管理器
    负责管理所有活跃的 WebSocket 连接
    
    P11增强:
    - 心跳检测
    - 消息发送重试
    - 连接健康状态监控
    """
    
    def __init__(self):
        # 存储所有活跃连接: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # 连接锁（防止并发问题）
        self._lock = asyncio.Lock()
        
        # P11: 消息发送失败计数（用于监控）
        self._send_failures: Dict[str, int] = {}
        
        # P11: 最大允许失败次数
        self._max_failures = 3
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """
        接受新的 WebSocket 连接
        
        Args:
            client_id: 客户端唯一标识
            websocket: WebSocket 连接对象
        """
        await websocket.accept()
        
        async with self._lock:
            # 如果该客户端已有连接，先关闭旧连接
            if client_id in self.active_connections:
                old_ws = self.active_connections[client_id]
                try:
                    if old_ws.client_state == WebSocketState.CONNECTED:
                        await old_ws.close()
                except Exception as e:
                    logger.warning(f"关闭旧连接失败 ({client_id}): {e}")
            
            # 保存新连接
            self.active_connections[client_id] = websocket
            
            # P11: 重置失败计数
            self._send_failures[client_id] = 0
        
        logger.info(f"✅ WebSocket 连接建立: {client_id} (总连接数: {len(self.active_connections)})")
    
    async def disconnect(self, client_id: str):
        """
        移除断开的连接
        
        Args:
            client_id: 客户端唯一标识
        """
        async with self._lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            
            # P11: 清理失败计数
            if client_id in self._send_failures:
                del self._send_failures[client_id]
        
        logger.info(f"❌ WebSocket 连接断开: {client_id} (总连接数: {len(self.active_connections)})")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str, retry: int = 2):
        """
        发送消息给指定客户端（P11增强：支持重试）
        
        Args:
            message: 要发送的消息（字典）
            client_id: 目标客户端ID
            retry: 重试次数（默认2次）
        """
        if client_id not in self.active_connections:
            logger.warning(f"客户端不在线: {client_id}")
            return False
        
        websocket = self.active_connections[client_id]
        
        for attempt in range(retry + 1):
            try:
                # 检查连接状态
                if websocket.client_state != WebSocketState.CONNECTED:
                    raise ConnectionError("WebSocket未连接")
                
                # 转换为 JSON 字符串
                message_json = json.dumps(message, ensure_ascii=False)
                
                # 发送
                await websocket.send_text(message_json)
                logger.debug(f"📤 发送消息到 {client_id}: {message.get('event', 'unknown')}")
                
                # P11: 成功后重置失败计数
                self._send_failures[client_id] = 0
                return True
                
            except Exception as e:
                logger.warning(f"发送消息失败 ({client_id}), 尝试 {attempt+1}/{retry+1}: {e}")
                
                # P11: 记录失败
                self._send_failures[client_id] = self._send_failures.get(client_id, 0) + 1
                
                if attempt < retry:
                    # 短暂等待后重试
                    await asyncio.sleep(0.5)
                else:
                    # 重试耗尽，断开连接
                    logger.error(f"发送失败次数过多 ({client_id}), 断开连接")
                    await self.disconnect(client_id)
                    return False
        
        return False
    
    async def broadcast(self, message: Dict[str, Any], exclude: Set[str] = None):
        """
        广播消息给所有连接的客户端
        
        Args:
            message: 要广播的消息（字典）
            exclude: 要排除的客户端ID集合（可选）
        """
        if exclude is None:
            exclude = set()
        
        # 转换为 JSON 字符串
        message_json = json.dumps(message, ensure_ascii=False)
        
        # 获取所有要发送的客户端
        async with self._lock:
            target_clients = [
                (client_id, ws)
                for client_id, ws in self.active_connections.items()
                if client_id not in exclude
            ]
        
        logger.debug(f"📡 广播消息: {message.get('event', 'unknown')} (接收者: {len(target_clients)})")
        
        # 并发发送给所有客户端
        disconnect_list = []
        
        for client_id, websocket in target_clients:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"广播失败 ({client_id}): {e}")
                disconnect_list.append(client_id)
        
        # 断开失败的连接
        for client_id in disconnect_list:
            await self.disconnect(client_id)
    
    def get_active_clients(self) -> list:
        """
        获取所有活跃客户端列表
        
        Returns:
            客户端ID列表
        """
        return list(self.active_connections.keys())


# 创建全局连接管理器
manager = ConnectionManager()


# =====================================================
# WebSocket 路由
# =====================================================

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket 连接端点
    
    Args:
        websocket: WebSocket 连接对象
        client_id: 客户端唯一标识（通常是浏览器生成的UUID）
    """
    # 建立连接
    await manager.connect(client_id, websocket)
    
    try:
        # 发送欢迎消息
        await manager.send_personal_message(
            {
                "event": "connected",
                "client_id": client_id,
                "message": "WebSocket 连接成功",
                "timestamp": datetime.now().isoformat()
            },
            client_id
        )
        
        # 循环接收客户端消息
        while True:
            try:
                # 接收文本消息
                data = await websocket.receive_text()
                
                try:
                    # 解析 JSON
                    message = json.loads(data)
                    
                    logger.debug(f"📥 收到客户端消息 ({client_id}): {message.get('type', 'unknown')}")
                    
                    # 处理不同类型的消息
                    await handle_client_message(client_id, message)
                    
                except json.JSONDecodeError:
                    logger.warning(f"收到无效 JSON ({client_id}): {data[:100]}")
                    await manager.send_personal_message(
                        {
                            "event": "error",
                            "message": "无效的 JSON 格式"
                        },
                        client_id
                    )
            
            except WebSocketDisconnect:
                # 客户端主动断开
                break
            
            except Exception as e:
                logger.error(f"处理消息异常 ({client_id}): {e}", exc_info=True)
                # 继续运行，不因单条消息错误而断开连接
    
    finally:
        # 断开连接
        await manager.disconnect(client_id)


async def handle_client_message(client_id: str, message: Dict[str, Any]):
    """
    处理客户端发来的消息
    
    Args:
        client_id: 客户端ID
        message: 消息内容
    """
    message_type = message.get("type", "unknown")
    
    if message_type == "ping":
        # 心跳检测
        await manager.send_personal_message(
            {
                "event": "pong",
                "timestamp": datetime.now().isoformat()
            },
            client_id
        )
    
    elif message_type == "subscribe_project":
        # 订阅项目更新
        project_id = message.get("project_id")
        logger.info(f"客户端 {client_id} 订阅项目: {project_id}")
        
        # TODO: 实现项目订阅逻辑
        # 当前 P5 阶段先返回确认，后续集成
        
        await manager.send_personal_message(
            {
                "event": "subscribed",
                "project_id": project_id,
                "message": f"已订阅项目 {project_id} 的实时更新"
            },
            client_id
        )
    
    elif message_type == "unsubscribe_project":
        # 取消订阅项目
        project_id = message.get("project_id")
        logger.info(f"客户端 {client_id} 取消订阅项目: {project_id}")
        
        # TODO: 实现取消订阅逻辑
        
        await manager.send_personal_message(
            {
                "event": "unsubscribed",
                "project_id": project_id
            },
            client_id
        )
    
    elif message_type == "boss_decision_response":
        # 处理老板决策响应
        decision_id = message.get("decision_id")
        choice = message.get("choice")
        
        logger.info(f"📥 收到老板决策响应: {decision_id} -> {choice}")
        
        # 调用全局的决策处理函数
        await handle_boss_decision_response(decision_id, choice)
        
        # 发送确认
        await manager.send_personal_message(
            {
                "event": "decision_submitted",
                "decision_id": decision_id,
                "message": "决策已提交"
            },
            client_id
        )
    
    else:
        logger.warning(f"未知消息类型: {message_type}")


# =====================================================
# 决策处理（全局存储）
# =====================================================

# 全局工作流字典 - 由 http_routes 在启动项目时注册
_active_workflows: Dict[str, Any] = {}

def register_workflow(project_id: str, workflow):
    """
    注册活跃的工作流实例
    
    Args:
        project_id: 项目ID
        workflow: GameDevWorkflow实例
    """
    _active_workflows[project_id] = workflow
    logger.info(f"注册工作流: {project_id}")

def unregister_workflow(project_id: str):
    """
    注销工作流实例
    
    Args:
        project_id: 项目ID
    """
    if project_id in _active_workflows:
        del _active_workflows[project_id]
        logger.info(f"注销工作流: {project_id}")

async def handle_boss_decision_response(decision_id: str, choice: str):
    """
    处理老板决策响应，提交给对应的工作流
    
    Args:
        decision_id: 决策ID
        choice: 用户选择
    """
    # 查找包含该决策的工作流
    for project_id, workflow in _active_workflows.items():
        if hasattr(workflow, 'submit_boss_decision'):
            success = workflow.submit_boss_decision(decision_id, choice)
            if success:
                logger.info(f"✅ 决策已提交到工作流 {project_id}: {decision_id} -> {choice}")
                return
    
    logger.warning(f"⚠️ 未找到决策ID对应的工作流: {decision_id}")

# =====================================================
# 导出的工具函数（供其他模块调用）
# =====================================================

async def broadcast_agent_message(
    project_id: str,
    from_agent: str,
    to_agent: str,
    message_type: str,
    content: str,
    context: str = ""
):
    """
    广播 Agent 消息给所有连接的客户端
    
    Args:
        project_id: 项目ID
        from_agent: 发送者 Agent ID
        to_agent: 接收者 Agent ID
        message_type: 消息类型
        content: 消息内容
        context: 上下文信息
    """
    await manager.broadcast({
        "event": "agent_message",
        "project_id": project_id,
        "from": from_agent,
        "to": to_agent,
        "type": message_type,
        "content": content,
        "context": context,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_agent_status(
    project_id: str,
    agent_id: str,
    status: str,
    current_task: str = ""
):
    """
    广播 Agent 状态变化
    
    Args:
        project_id: 项目ID
        agent_id: Agent ID
        status: 新状态（idle/working/thinking/waiting）
        current_task: 当前任务描述
    """
    await manager.broadcast({
        "event": "agent_status",
        "project_id": project_id,
        "agent_id": agent_id,
        "status": status,
        "current_task": current_task,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_file_update(
    project_id: str,
    file_path: str,
    update_type: str,
    updated_by: str
):
    """
    广播文件更新事件
    
    Args:
        project_id: 项目ID
        file_path: 文件路径
        update_type: 更新类型（created/modified/deleted）
        updated_by: 更新者 Agent ID
    """
    await manager.broadcast({
        "event": "file_update",
        "project_id": project_id,
        "file_path": file_path,
        "update_type": update_type,
        "updated_by": updated_by,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_agent_output(
    project_id: str,
    agent_id: str,
    file_path: str,
    file_type: str,
    summary: str = ""
):
    """
    广播 Agent 产出文件事件
    
    Args:
        project_id: 项目ID
        agent_id: 产出者 Agent ID
        file_path: 文件路径（相对于项目目录）
        file_type: 文件类型（document/code/config/asset）
        summary: 文件摘要描述
    """
    await manager.broadcast({
        "event": "file_output",
        "project_id": project_id,
        "agent_id": agent_id,
        "file_path": file_path,
        "file_type": file_type,
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_phase_change(
    project_id: str,
    old_phase: str,
    new_phase: str,
    progress: float
):
    """
    广播项目阶段变化
    
    Args:
        project_id: 项目ID
        old_phase: 旧阶段
        new_phase: 新阶段
        progress: 进度百分比
    """
    # 同步更新projects_store中的阶段信息（用于HTTP API查询）
    # 注意：project_id可能是"项目名_时间戳"格式，需要找到对应的存储记录
    from api.http_routes import projects_store
    
    for pid, project in projects_store.items():
        if pid == project_id or project.get("project_name") == project_id:
            project["current_phase"] = new_phase
            project["progress"] = progress
            project["updated_at"] = datetime.now().isoformat()
            break
    
    await manager.broadcast({
        "event": "phase_change",
        "project_id": project_id,
        "old_phase": old_phase,
        "new_phase": new_phase,
        "progress": progress,
        "timestamp": datetime.now().isoformat()
    })


async def request_boss_decision(
    project_id: str,
    decision_id: str,
    agent_id: str,
    question: str,
    options: list = None
):
    """
    请求老板做决策（触发前端弹窗）
    
    Args:
        project_id: 项目ID
        decision_id: 决策点唯一ID
        agent_id: 请求决策的 Agent ID
        question: 决策问题描述
        options: 可选项列表（可选）
    """
    await manager.broadcast({
        "event": "boss_decision",
        "project_id": project_id,
        "decision_id": decision_id,
        "agent_id": agent_id,
        "question": question,
        "options": options or [],
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_task_complete(
    project_id: str,
    task_name: str,
    completed_by: str,
    result: str
):
    """
    广播任务完成事件
    
    Args:
        project_id: 项目ID
        task_name: 任务名称
        completed_by: 完成者 Agent ID
        result: 任务结果描述
    """
    await manager.broadcast({
        "event": "task_complete",
        "project_id": project_id,
        "task_name": task_name,
        "completed_by": completed_by,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_error_alert(
    project_id: str,
    error_type: str,
    error_message: str,
    agent_id: str = ""
):
    """
    广播错误警报
    
    Args:
        project_id: 项目ID
        error_type: 错误类型
        error_message: 错误消息
        agent_id: 发生错误的 Agent ID（可选）
    """
    await manager.broadcast({
        "event": "error_alert",
        "project_id": project_id,
        "error_type": error_type,
        "error_message": error_message,
        "agent_id": agent_id,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_project_complete(
    project_id: str,
    message: str = "",
    output_dir: str = ""
):
    """
    广播项目完成事件（BUG-014）
    
    Args:
        project_id: 项目ID
        message: 完成消息
        output_dir: 输出目录
    """
    await manager.broadcast({
        "event": "project_complete",
        "project_id": project_id,
        "message": message or f"🎉 项目 {project_id} 开发完成！",
        "output_dir": output_dir,
        "timestamp": datetime.now().isoformat()
    })
