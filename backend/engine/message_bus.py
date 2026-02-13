"""
文件: engine/message_bus.py
职责: Agent间消息路由、记录和推送
依赖: utils/logger.py
被依赖: api/websocket_handler.py, agents/*.py

关键接口:
  - MessageBus() - 创建消息总线实例(单例)
  - async send(message) - 发送消息
  - subscribe(agent_id, callback) - 订阅消息
  - get_history(limit) - 获取历史消息
"""

import asyncio
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import json
from pathlib import Path
import sys

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from utils.logger import setup_logger


class MessageBus:
    """
    消息总线
    
    所有Agent之间的通信都通过消息总线进行
    职责:
    1. 消息路由(点对点、广播)
    2. 消息记录(持久化日志)
    3. 消息推送(WebSocket实时推送)
    4. 消息队列管理(防止消息淹没)
    """
    
    _instance = None  # 单例模式
    
    def __new__(cls):
        """单例模式: 确保只有一个消息总线实例"""
        if cls._instance is None:
            cls._instance = super(MessageBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化消息总线"""
        if self._initialized:
            return
            
        # 消息历史记录(内存中保留最近的消息)
        self.message_history: List[Dict[str, Any]] = []
        self.max_history = 1000  # 最多保留1000条消息
        
        # Agent订阅: {agent_id: callback}
        self.subscribers: Dict[str, Callable] = {}
        
        # WebSocket订阅者(用于实时推送到前端)
        self.websocket_callbacks: List[Callable] = []
        
        # 消息队列: {agent_id: asyncio.Queue}
        self.message_queues: Dict[str, asyncio.Queue] = {}
        
        # 消息频率限制: {(from, to): [(timestamp, count), ...]}
        self.rate_limits: Dict[tuple, List[tuple]] = {}
        self.max_messages_per_minute = 10  # 同一对Agent之间每分钟最多10条消息
        
        # 日志器
        self.logger = setup_logger("message_bus")
        
        self._initialized = True
        
        self.logger.info("消息总线初始化成功")
    
    def subscribe(self, agent_id: str, callback: Callable) -> None:
        """
        订阅消息
        
        Agent注册自己的消息处理回调函数
        
        Args:
            agent_id: Agent的唯一标识符
            callback: 消息处理回调函数 async def callback(message)
        """
        self.subscribers[agent_id] = callback
        
        # 为Agent创建消息队列
        if agent_id not in self.message_queues:
            self.message_queues[agent_id] = asyncio.Queue()
        
        self.logger.info(f"Agent [{agent_id}] 已订阅消息总线")
    
    def unsubscribe(self, agent_id: str) -> None:
        """
        取消订阅
        
        Args:
            agent_id: Agent的唯一标识符
        """
        if agent_id in self.subscribers:
            del self.subscribers[agent_id]
            self.logger.info(f"Agent [{agent_id}] 已取消订阅")
    
    def subscribe_websocket(self, callback: Callable) -> None:
        """
        订阅WebSocket推送
        
        前端通过WebSocket接收实时消息
        
        Args:
            callback: WebSocket推送回调函数
        """
        self.websocket_callbacks.append(callback)
        self.logger.info(f"WebSocket订阅者已添加，当前订阅者数量: {len(self.websocket_callbacks)}")
    
    def _check_rate_limit(self, from_agent: str, to_agent: str) -> bool:
        """
        检查消息频率是否超限
        
        同一对Agent之间每分钟最多10条消息
        
        Args:
            from_agent: 发送者
            to_agent: 接收者
        
        Returns:
            True: 未超限，可以发送
            False: 已超限，拒绝发送
        """
        key = (from_agent, to_agent)
        now = datetime.now().timestamp()
        
        # 清理1分钟前的记录
        if key in self.rate_limits:
            self.rate_limits[key] = [
                (ts, count) for ts, count in self.rate_limits[key]
                if now - ts < 60
            ]
        else:
            self.rate_limits[key] = []
        
        # 检查是否超限(检查现有消息数，不包括本次)
        recent_count = sum(count for _, count in self.rate_limits[key])
        if recent_count >= self.max_messages_per_minute:
            self.logger.warning(
                f"消息频率超限: [{from_agent}] → [{to_agent}] "
                f"({recent_count}/{self.max_messages_per_minute} 消息/分钟)"
            )
            return False
        
        # 检查通过后，记录本次发送
        self.rate_limits[key].append((now, 1))
        return True
    
    async def send(self, message: Dict[str, Any]) -> bool:
        """
        发送消息
        
        Args:
            message: 消息字典，格式:
                {
                    "from": "agent_id",
                    "to": "target_id",  # 或 "all" 表示广播
                    "type": "question|answer|report|request_review",
                    "content": "消息正文",
                    "context": "工作上下文",
                    "priority": "normal|urgent|blocking",
                    "timestamp": "ISO8601时间戳"
                }
        
        Returns:
            True: 发送成功
            False: 发送失败(频率超限等)
        """
        # 补充时间戳(如果没有)
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        from_agent = message.get("from", "unknown")
        to_agent = message.get("to", "unknown")
        msg_type = message.get("type", "message")
        priority = message.get("priority", "normal")
        
        # 检查频率限制(紧急消息除外)
        if priority != "urgent" and to_agent != "all" and to_agent != "boss":
            if not self._check_rate_limit(from_agent, to_agent):
                return False
        
        # 记录到历史
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        # 日志记录
        content_preview = message.get("content", "")[:50]
        self.logger.info(
            f"消息路由: [{from_agent}] → [{to_agent}] "
            f"类型:{msg_type} 优先级:{priority} 内容:{content_preview}..."
        )
        
        # 推送到WebSocket(实时显示)
        await self._push_to_websockets(message)
        
        # 路由消息
        if to_agent == "all":
            # 广播消息
            await self._broadcast(message)
        elif to_agent == "boss":
            # 发给老板(人类介入)
            await self._send_to_boss(message)
        else:
            # 点对点消息
            await self._send_to_agent(to_agent, message)
        
        return True
    
    async def _send_to_agent(self, agent_id: str, message: Dict[str, Any]) -> None:
        """
        发送消息给指定Agent
        
        Args:
            agent_id: 目标Agent的ID
            message: 消息内容
        """
        if agent_id in self.message_queues:
            await self.message_queues[agent_id].put(message)
            self.logger.debug(f"消息已加入 [{agent_id}] 的队列")
        else:
            self.logger.warning(f"Agent [{agent_id}] 未订阅消息总线，消息丢失")
    
    async def _broadcast(self, message: Dict[str, Any]) -> None:
        """
        广播消息给所有Agent
        
        Args:
            message: 消息内容
        """
        self.logger.debug(f"广播消息给 {len(self.message_queues)} 个Agent")
        
        for agent_id, queue in self.message_queues.items():
            # 不发给自己
            if agent_id != message.get("from"):
                await queue.put(message)
    
    async def _send_to_boss(self, message: Dict[str, Any]) -> None:
        """
        发送消息给老板(人类介入)
        
        这个方法会触发前端弹窗，等待用户决策
        
        Args:
            message: 消息内容
        """
        self.logger.info(f"请求老板决策: {message.get('content', '')[:50]}...")
        
        # WebSocket会推送这个消息到前端，触发决策面板
        # 实际的等待逻辑在 P7 阶段实现
        pass
    
    async def _push_to_websockets(self, message: Dict[str, Any]) -> None:
        """
        推送消息到所有WebSocket订阅者
        
        Args:
            message: 消息内容
        """
        if not self.websocket_callbacks:
            return
        
        # 异步推送到所有WebSocket
        tasks = [callback(message) for callback in self.websocket_callbacks]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def receive(self, agent_id: str, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        接收消息(Agent调用)
        
        Args:
            agent_id: Agent的ID
            timeout: 超时时间(秒)，None表示无限等待
        
        Returns:
            消息字典，如果超时返回None
        """
        if agent_id not in self.message_queues:
            self.logger.warning(f"Agent [{agent_id}] 未订阅消息总线")
            return None
        
        try:
            if timeout is None:
                message = await self.message_queues[agent_id].get()
            else:
                message = await asyncio.wait_for(
                    self.message_queues[agent_id].get(),
                    timeout=timeout
                )
            
            return message
        except asyncio.TimeoutError:
            return None
    
    def get_history(self, limit: Optional[int] = None, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取消息历史
        
        Args:
            limit: 返回最近的N条消息，None表示全部
            agent_id: 只返回与指定Agent相关的消息，None表示全部
        
        Returns:
            消息列表
        """
        messages = self.message_history
        
        # 过滤Agent相关消息
        if agent_id:
            messages = [
                msg for msg in messages
                if msg.get("from") == agent_id or msg.get("to") == agent_id or msg.get("to") == "all"
            ]
        
        # 限制数量
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取消息总线状态摘要
        
        Returns:
            状态摘要字典
        """
        return {
            "total_messages": len(self.message_history),
            "active_agents": len(self.subscribers),
            "websocket_connections": len(self.websocket_callbacks),
            "queued_messages": {
                agent_id: queue.qsize()
                for agent_id, queue in self.message_queues.items()
            }
        }
    
    def clear_history(self) -> None:
        """清空消息历史"""
        self.message_history.clear()
        self.logger.info("消息历史已清空")


# 测试代码
if __name__ == "__main__":
    async def test_message_bus():
        """测试消息总线"""
        print("\n" + "="*60)
        print("测试消息总线")
        print("="*60 + "\n")
        
        try:
            # 创建消息总线
            bus = MessageBus()
            
            print("1. 测试单例模式:")
            print("-" * 60)
            bus2 = MessageBus()
            print(f"bus is bus2: {bus is bus2}")
            assert bus is bus2, "消息总线应该是单例"
            print("✅ 单例模式正常\n")
            
            print("2. 测试Agent订阅:")
            print("-" * 60)
            
            received_messages = []
            
            async def agent_callback(message):
                received_messages.append(message)
                print(f"  收到消息: {message['from']} → {message['to']}: {message['content'][:30]}...")
            
            bus.subscribe("agent_a", agent_callback)
            bus.subscribe("agent_b", agent_callback)
            print("✅ 2个Agent已订阅\n")
            
            print("3. 测试点对点消息:")
            print("-" * 60)
            message1 = {
                "from": "agent_a",
                "to": "agent_b",
                "type": "question",
                "content": "你好，agent_b！",
                "priority": "normal"
            }
            success = await bus.send(message1)
            assert success, "消息发送应该成功"
            
            # 接收消息
            received = await bus.receive("agent_b", timeout=1.0)
            assert received is not None, "agent_b应该收到消息"
            assert received["content"] == "你好，agent_b！"
            print("✅ 点对点消息正常\n")
            
            print("4. 测试广播消息:")
            print("-" * 60)
            message2 = {
                "from": "agent_a",
                "to": "all",
                "type": "report",
                "content": "这是一条广播消息",
                "priority": "normal"
            }
            await bus.send(message2)
            
            # agent_b应该收到广播
            received_b = await bus.receive("agent_b", timeout=1.0)
            assert received_b is not None, "agent_b应该收到广播"
            print("✅ 广播消息正常\n")
            
            print("5. 测试消息历史:")
            print("-" * 60)
            history = bus.get_history(limit=5)
            print(f"最近5条消息: {len(history)} 条")
            for i, msg in enumerate(history, 1):
                print(f"  {i}. {msg['from']} → {msg['to']}: {msg['type']}")
            print("✅ 消息历史记录正常\n")
            
            print("6. 测试频率限制:")
            print("-" * 60)
            # 快速发送多条消息
            success_count = 0
            failed_count = 0
            for i in range(12):
                msg = {
                    "from": "agent_c",  # 使用新的Agent避免与前面的消息混淆
                    "to": "agent_d",
                    "type": "question",
                    "content": f"测试消息 {i+1}",
                    "priority": "normal"
                }
                success = await bus.send(msg)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            
            print(f"  成功发送: {success_count} 条")
            print(f"  被限流: {failed_count} 条")
            assert success_count == 10, f"应该成功发送10条消息，实际: {success_count}"
            assert failed_count == 2, f"应该有2条被限流，实际: {failed_count}"
            print("✅ 频率限制正常\n")
            
            print("7. 测试状态摘要:")
            print("-" * 60)
            summary = bus.get_summary()
            print(f"总消息数: {summary['total_messages']}")
            print(f"活跃Agent: {summary['active_agents']}")
            print(f"队列状态: {summary['queued_messages']}")
            print("✅ 状态摘要正常\n")
            
            print("="*60)
            print("✅ 消息总线测试全部通过！")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 运行测试
    asyncio.run(test_message_bus())
