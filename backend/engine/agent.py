"""
文件: engine/agent.py
职责: Agent基类，定义所有AI员工的基本能力
依赖: llm_client.py, context_manager.py, config.py
被依赖: agents/*.py (所有具体的Agent实现)

关键接口:
  - Agent(agent_id, role, system_prompt) - 创建Agent实例
  - async think_and_respond(user_message) - 让Agent思考并回复
  - async process_message(message_dict) - 处理收到的消息
"""

import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
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
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from config import Config
from engine.llm_client import LLMClient
from engine.context_manager import ContextManager
from utils.logger import setup_logger
from tools.tool_registry import AgentToolkit


class Agent:
    """
    Agent 基类
    
    所有AI员工（策划、程序员、美术等）都继承此类
    提供基本的对话能力、上下文管理、消息处理、工具调用等功能
    """
    
    def __init__(
        self,
        agent_id: str,
        role: str,
        system_prompt: str,
        model_name: Optional[str] = None,
        tools: Optional[List[str]] = None
    ):
        """
        初始化 Agent
        
        Args:
            agent_id: Agent唯一标识符（如 "planner", "programmer"）
            role: Agent角色名称（如 "游戏策划", "游戏程序员"）
            system_prompt: 系统提示词，定义Agent的职责和行为规范
            model_name: 使用的LLM模型，默认使用配置中的模型
            tools: 允许使用的工具列表（如 ["file", "code_runner"]）
        """
        self.agent_id = agent_id
        self.role = role
        self.system_prompt = system_prompt
        
        # 创建 LLM 客户端
        self.llm_client = LLMClient(model_name)
        
        # 创建上下文管理器
        self.context_manager = ContextManager(
            max_tokens=Config.MAX_PROJECT_TOKENS // 5,  # 每个Agent分配总预算的1/5
            max_messages=50
        )
        
        # 创建工具包
        self.toolkit = AgentToolkit(agent_id)
        
        # 启用指定的工具
        if tools:
            for tool_name in tools:
                self.toolkit.enable_tool(tool_name)
        
        # Agent 状态
        self.status = "idle"  # idle, thinking, working, waiting
        self.current_task: Optional[str] = None
        
        # 创建日志器
        self.logger = setup_logger(
            f"agent.{agent_id}",
            log_level=Config.LOG_LEVEL,
            log_to_file=Config.LOG_TO_FILE
        )
        
        self.logger.info(f"Agent初始化成功: [{agent_id}] {role}")
        if tools:
            self.logger.info(f"启用的工具: {', '.join(tools)}")
    
    async def think_and_respond(self, user_message: str) -> str:
        """
        让 Agent 思考并生成回复
        
        这是Agent的核心能力：接收消息，调用LLM思考，返回回复
        
        Args:
            user_message: 用户或其他Agent发来的消息
        
        Returns:
            Agent的回复内容
        """
        try:
            self.status = "thinking"
            
            # 将用户消息添加到上下文
            self.context_manager.add_message("user", user_message)
            
            # 获取当前上下文
            messages = self.context_manager.get_messages()
            
            context_summary = self.context_manager.get_summary()
            self.logger.debug(f"正在思考... 上下文: {context_summary['message_count']}条消息, "
                            f"{context_summary['estimated_tokens']}tokens")
            
            # 调用 LLM 生成回复
            response = await self.llm_client.generate_response(
                messages=messages,
                system_prompt=self.system_prompt
            )
            
            # 将回复添加到上下文
            self.context_manager.add_message("model", response)
            
            self.status = "idle"
            
            self.logger.info("回复完成")
            
            return response
            
        except Exception as e:
            self.status = "idle"
            error_msg = f"Agent思考出错: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return f"抱歉，我遇到了技术问题：{error_msg}"
    
    async def process_message(self, message: Dict[str, Any]) -> Optional[str]:
        """
        处理收到的消息
        
        这个方法会在消息总线中被调用（P2阶段实现）
        
        Args:
            message: 消息字典，格式见 platform_constitution.md 中的消息格式标准
        
        Returns:
            如果需要回复，返回回复内容；否则返回 None
        """
        msg_type = message.get("type", "question")
        content = message.get("content", "")
        from_agent = message.get("from", "unknown")
        
        self.logger.debug(f"收到来自 [{from_agent}] 的消息，类型: {msg_type}")
        self.logger.debug(f"内容: {content[:100]}...")
        
        # 根据消息类型决定是否需要回复
        if msg_type in ["question", "request_review"]:
            # 需要回复的消息
            response = await self.think_and_respond(content)
            return response
        elif msg_type in ["answer", "report"]:
            # 不需要回复的消息，只需要记录到上下文
            self.context_manager.add_message("user", f"[{from_agent}说]: {content}")
            return None
        else:
            # 未知类型，默认回复
            response = await self.think_and_respond(content)
            return response
    
    def load_file_to_context(self, file_path: str, content: str) -> None:
        """
        将文件内容加载到 Agent 的上下文中
        
        这用于实现"文件即真相"原则：Agent工作前先读取相关文件
        
        Args:
            file_path: 文件路径标识
            content: 文件内容
        """
        self.context_manager.inject_file_content(file_path, content)
        
        self.logger.debug(f"已加载文件: {file_path}")
    
    async def call_tool(self, tool_name: str, method_name: str, *args, **kwargs) -> Any:
        """
        调用工具方法（便捷接口）
        
        Args:
            tool_name: 工具名称（如 "file", "code_runner"）
            method_name: 方法名（如 "read", "write"）
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            工具方法的返回值
            
        Raises:
            PermissionError: 工具未启用
        """
        try:
            result = await self.toolkit.call(tool_name, method_name, *args, **kwargs)
            self.logger.debug(f"调用工具: {tool_name}.{method_name}")
            return result
        except Exception as e:
            self.logger.error(f"工具调用失败 {tool_name}.{method_name}: {e}")
            raise
    
    def enable_tool(self, tool_name: str) -> bool:
        """
        启用工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            成功返回True
        """
        success = self.toolkit.enable_tool(tool_name)
        if success:
            self.logger.info(f"启用工具: {tool_name}")
        return success
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        获取可用工具列表
        
        Returns:
            工具信息列表
        """
        return self.toolkit.get_available_tools()
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取 Agent 的当前状态
        
        Returns:
            包含Agent状态信息的字典
        """
        context_summary = self.context_manager.get_summary()
        
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "status": self.status,
            "current_task": self.current_task,
            "context": context_summary,
            "tools": [tool["name"] for tool in self.get_available_tools()]
        }
    
    def reset_context(self) -> None:
        """清空Agent的上下文（用于开始新项目时）"""
        self.context_manager.clear()
        self.status = "idle"
        self.current_task = None
        
        self.logger.info("上下文已重置")


# 测试代码
if __name__ == "__main__":
    async def test_agent():
        """测试 Agent 基类"""
        print("\n" + "="*60)
        print("测试 Agent 基类")
        print("="*60 + "\n")
        
        try:
            # 创建一个测试 Agent
            system_prompt = """
你是一个友好的AI游戏策划。
你的职责是：
1. 理解用户的游戏创意
2. 提出专业的游戏设计建议
3. 用简洁清晰的语言沟通

请始终保持专业和友好的态度。
"""
            
            agent = Agent(
                agent_id="test_planner",
                role="测试策划",
                system_prompt=system_prompt
            )
            
            print("\n1. 测试 Agent 状态:")
            print("-" * 60)
            status = agent.get_status()
            print(f"Agent ID: {status['agent_id']}")
            print(f"角色: {status['role']}")
            print(f"状态: {status['status']}")
            
            print("\n2. 测试对话能力:")
            print("-" * 60)
            
            # 第一轮对话
            print("\n用户: 你好！我想做一个贪吃蛇游戏。")
            response1 = await agent.think_and_respond(
                "你好！我想做一个贪吃蛇游戏。"
            )
            print(f"\n策划: {response1}\n")
            
            # 第二轮对话
            print("\n用户: 应该加入什么特色玩法？")
            response2 = await agent.think_and_respond(
                "应该加入什么特色玩法？"
            )
            print(f"\n策划: {response2}\n")
            
            print("\n3. 测试加载文件到上下文:")
            print("-" * 60)
            
            agent.load_file_to_context(
                "project_rules.yaml",
                """
项目规范：
- 游戏类型：休闲小游戏
- 技术栈：HTML5 + Canvas + JavaScript
- 目标平台：浏览器
- 风格：像素风格
"""
            )
            
            print("\n用户: 根据项目规范，这个游戏应该用什么技术实现？")
            response3 = await agent.think_and_respond(
                "根据项目规范，这个游戏应该用什么技术实现？"
            )
            print(f"\n策划: {response3}\n")
            
            print("\n4. 测试上下文状态:")
            print("-" * 60)
            status = agent.get_status()
            context = status['context']
            print(f"消息数量: {context['message_count']}")
            print(f"Token使用: {context['estimated_tokens']} / {context['max_tokens']}")
            print(f"使用率: {context['usage_percentage']:.1f}%")
            
            print("\n" + "="*60)
            print("✅ Agent 基类测试通过！")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 运行测试
    asyncio.run(test_agent())
