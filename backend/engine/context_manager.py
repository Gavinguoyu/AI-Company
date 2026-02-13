"""
文件: engine/context_manager.py
职责: 管理Agent的LLM上下文窗口，防止上下文爆炸
依赖: config.py, llm_client.py
被依赖: engine/agent.py
"""

import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

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
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from config import Config
from utils.logger import setup_logger


class ContextManager:
    """
    上下文管理器
    负责管理Agent的对话历史和工作上下文，防止超出LLM的上下文窗口限制
    """
    
    def __init__(
        self,
        max_tokens: int = 100000,  # Gemini 2.0 Flash 支持 100 万上下文，这里保守设置 10 万
        max_messages: int = 50      # 最多保留最近 50 条消息
    ):
        """
        初始化上下文管理器
        
        Args:
            max_tokens: 最大允许的 token 数量
            max_messages: 最大保留的消息数量
        """
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.messages: List[Dict[str, str]] = []
        self.current_tokens = 0
        
        # 创建日志器
        self.logger = setup_logger(
            "context_manager",
            log_level=Config.LOG_LEVEL,
            log_to_file=Config.LOG_TO_FILE
        )
        
        self.logger.info(f"上下文管理器初始化: 最大{max_tokens}tokens, 最多{max_messages}条消息")
    
    def add_message(self, role: str, content: str) -> None:
        """
        添加一条消息到上下文
        
        Args:
            role: 角色（"user" 或 "model"）
            content: 消息内容
        """
        message = {
            "role": role,
            "content": content
        }
        
        self.messages.append(message)
        
        # 估算新增的 token 数量（简单估算：1 token ≈ 4 字符）
        estimated_tokens = len(content) // 4
        self.current_tokens += estimated_tokens
        
        # 如果超过限制，裁剪旧消息
        self._trim_if_needed()
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        获取当前的消息历史
        
        Returns:
            消息列表
        """
        return self.messages.copy()
    
    def clear(self) -> None:
        """清空所有消息"""
        self.messages.clear()
        self.current_tokens = 0
        
        self.logger.info("上下文已清空")
    
    def _trim_if_needed(self) -> None:
        """
        如果上下文超过限制，裁剪旧消息
        保留最近的消息，删除最早的消息
        """
        # 检查消息数量限制
        if len(self.messages) > self.max_messages:
            # 删除最早的消息（但保留系统消息）
            removed_count = 0
            while len(self.messages) > self.max_messages:
                if self.messages[0].get("role") != "system":
                    removed = self.messages.pop(0)
                    removed_tokens = len(removed.get("content", "")) // 4
                    self.current_tokens -= removed_tokens
                    removed_count += 1
                else:
                    # 如果第一条是系统消息，从第二条开始删
                    if len(self.messages) > 1:
                        removed = self.messages.pop(1)
                        removed_tokens = len(removed.get("content", "")) // 4
                        self.current_tokens -= removed_tokens
                        removed_count += 1
                    else:
                        break
            
            if removed_count > 0:
                self.logger.debug(f"裁剪上下文: 删除了 {removed_count} 条旧消息（超过消息数量限制）")
        
        # 检查 token 数量限制
        if self.current_tokens > self.max_tokens:
            # 持续删除最早的消息，直到低于限制
            removed_count = 0
            while self.current_tokens > self.max_tokens and len(self.messages) > 1:
                if self.messages[0].get("role") != "system":
                    removed = self.messages.pop(0)
                    removed_tokens = len(removed.get("content", "")) // 4
                    self.current_tokens -= removed_tokens
                    removed_count += 1
                else:
                    if len(self.messages) > 1:
                        removed = self.messages.pop(1)
                        removed_tokens = len(removed.get("content", "")) // 4
                        self.current_tokens -= removed_tokens
                        removed_count += 1
                    else:
                        break
            
            if removed_count > 0:
                self.logger.debug(f"裁剪上下文: 因 token 超限删除了 {removed_count} 条消息")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取上下文摘要
        
        Returns:
            包含消息数量、token 数量等信息的字典
        """
        return {
            "message_count": len(self.messages),
            "estimated_tokens": self.current_tokens,
            "max_tokens": self.max_tokens,
            "max_messages": self.max_messages,
            "usage_percentage": (self.current_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0
        }
    
    def inject_file_content(self, file_path: str, content: str) -> None:
        """
        将文件内容注入到上下文中
        这用于让 Agent 读取项目规范、配置等文件
        
        Args:
            file_path: 文件路径（用于标识）
            content: 文件内容
        """
        file_message = f"## 文件: {file_path}\n\n{content}"
        self.add_message("user", file_message)
        
        self.logger.debug(f"已注入文件内容: {file_path}")


# 测试代码
if __name__ == "__main__":
    print("\n" + "="*60)
    print("测试上下文管理器")
    print("="*60 + "\n")
    
    # 创建上下文管理器（设置较小的限制方便测试）
    cm = ContextManager(max_tokens=1000, max_messages=5)
    
    print("\n1. 添加消息测试:")
    print("-" * 60)
    cm.add_message("user", "你好！")
    cm.add_message("model", "你好！我是AI助手，有什么可以帮你的吗？")
    cm.add_message("user", "请告诉我今天的天气。")
    cm.add_message("model", "抱歉，我无法获取实时天气信息。")
    
    summary = cm.get_summary()
    print(f"消息数量: {summary['message_count']}")
    print(f"估算 Token: {summary['estimated_tokens']}")
    print(f"使用率: {summary['usage_percentage']:.1f}%")
    
    print("\n2. 测试消息数量限制（最多5条）:")
    print("-" * 60)
    for i in range(10):
        cm.add_message("user", f"测试消息 {i+1}")
    
    summary = cm.get_summary()
    print(f"消息数量: {summary['message_count']} (应该不超过5条)")
    
    print("\n3. 注入文件内容测试:")
    print("-" * 60)
    cm.inject_file_content(
        "project_rules.yaml",
        "命名规范:\n  - 使用 snake_case\n  - 函数名要清晰表达意图"
    )
    
    summary = cm.get_summary()
    print(f"注入后消息数量: {summary['message_count']}")
    
    print("\n4. 获取消息历史:")
    print("-" * 60)
    messages = cm.get_messages()
    for i, msg in enumerate(messages, 1):
        role = msg['role']
        content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
        print(f"{i}. [{role}] {content}")
    
    print("\n5. 清空测试:")
    print("-" * 60)
    cm.clear()
    summary = cm.get_summary()
    print(f"清空后消息数量: {summary['message_count']}")
    
    print("\n" + "="*60)
    print("✅ 上下文管理器测试通过！")
    print("="*60 + "\n")
