"""
文件: tools/tool_registry.py
职责: 工具注册和调用机制
依赖: utils/logger.py, tools/*
被依赖: Agent基类
关键接口:
  - ToolRegistry.register_tool(name, tool_instance) -> 注册工具
  - ToolRegistry.get_tool(name) -> 获取工具实例
  - ToolRegistry.call_tool(name, method, **kwargs) -> 调用工具方法
  - ToolRegistry.list_tools() -> 列出所有工具
"""

from typing import Dict, Any, Optional, List, Callable
from utils.logger import setup_logger

logger = setup_logger("tool_registry")


class ToolRegistry:
    """工具注册表 - 管理所有可用工具的单例"""
    
    _instance = None
    _tools: Dict[str, Any] = {}
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("工具注册表初始化")
        return cls._instance
    
    def register_tool(self, name: str, tool_instance: Any) -> None:
        """
        注册工具
        
        Args:
            name: 工具名称（唯一标识）
            tool_instance: 工具实例对象
        """
        if name in self._tools:
            logger.warning(f"工具 '{name}' 已存在，将被覆盖")
        
        self._tools[name] = tool_instance
        logger.info(f"注册工具: {name} ({type(tool_instance).__name__})")
    
    def unregister_tool(self, name: str) -> bool:
        """
        注销工具
        
        Args:
            name: 工具名称
            
        Returns:
            成功返回True
        """
        if name not in self._tools:
            logger.warning(f"工具 '{name}' 不存在")
            return False
        
        del self._tools[name]
        logger.info(f"注销工具: {name}")
        return True
    
    def get_tool(self, name: str) -> Optional[Any]:
        """
        获取工具实例
        
        Args:
            name: 工具名称
            
        Returns:
            工具实例，不存在返回None
        """
        tool = self._tools.get(name)
        if tool is None:
            logger.warning(f"工具 '{name}' 不存在")
        return tool
    
    async def call_tool(
        self, 
        tool_name: str, 
        method_name: str, 
        *args, 
        **kwargs
    ) -> Any:
        """
        调用工具的方法
        
        Args:
            tool_name: 工具名称
            method_name: 方法名
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            方法调用结果
            
        Raises:
            ValueError: 工具或方法不存在
        """
        tool = self.get_tool(tool_name)
        
        if tool is None:
            raise ValueError(f"工具 '{tool_name}' 不存在")
        
        if not hasattr(tool, method_name):
            raise ValueError(f"工具 '{tool_name}' 没有方法 '{method_name}'")
        
        method = getattr(tool, method_name)
        
        if not callable(method):
            raise ValueError(f"'{method_name}' 不是可调用方法")
        
        logger.debug(f"调用工具方法: {tool_name}.{method_name}")
        
        # 如果是异步方法，await调用
        import inspect
        if inspect.iscoroutinefunction(method):
            result = await method(*args, **kwargs)
        else:
            result = method(*args, **kwargs)
        
        return result
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        列出所有已注册的工具
        
        Returns:
            工具信息列表 [{name, type, methods}]
        """
        tools_info = []
        
        for name, tool in self._tools.items():
            # 获取工具的所有公共方法
            methods = [
                method for method in dir(tool)
                if not method.startswith('_') and callable(getattr(tool, method))
            ]
            
            tools_info.append({
                "name": name,
                "type": type(tool).__name__,
                "methods": methods
            })
        
        return tools_info
    
    def has_tool(self, name: str) -> bool:
        """
        检查工具是否已注册
        
        Args:
            name: 工具名称
            
        Returns:
            已注册返回True
        """
        return name in self._tools
    
    def get_tool_description(self, name: str) -> Optional[str]:
        """
        获取工具的描述信息
        
        Args:
            name: 工具名称
            
        Returns:
            工具类的docstring，不存在返回None
        """
        tool = self.get_tool(name)
        if tool is None:
            return None
        
        return tool.__class__.__doc__ or "无描述"


class AgentToolkit:
    """Agent工具包 - 为单个Agent提供工具访问接口"""
    
    def __init__(self, agent_id: str):
        """
        初始化Agent工具包
        
        Args:
            agent_id: Agent ID
        """
        self.agent_id = agent_id
        self.registry = ToolRegistry()
        self.enabled_tools: List[str] = []
        
        logger.info(f"为 Agent '{agent_id}' 创建工具包")
    
    def enable_tool(self, tool_name: str) -> bool:
        """
        启用工具（允许Agent使用）
        
        Args:
            tool_name: 工具名称
            
        Returns:
            成功返回True
        """
        if not self.registry.has_tool(tool_name):
            logger.warning(f"工具 '{tool_name}' 未注册，无法启用")
            return False
        
        if tool_name not in self.enabled_tools:
            self.enabled_tools.append(tool_name)
            logger.info(f"Agent '{self.agent_id}' 启用工具: {tool_name}")
        
        return True
    
    def disable_tool(self, tool_name: str) -> bool:
        """
        禁用工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            成功返回True
        """
        if tool_name in self.enabled_tools:
            self.enabled_tools.remove(tool_name)
            logger.info(f"Agent '{self.agent_id}' 禁用工具: {tool_name}")
            return True
        return False
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """
        检查工具是否已启用
        
        Args:
            tool_name: 工具名称
            
        Returns:
            已启用返回True
        """
        return tool_name in self.enabled_tools
    
    async def call(self, tool_name: str, method_name: str, *args, **kwargs) -> Any:
        """
        调用已启用的工具方法
        
        Args:
            tool_name: 工具名称
            method_name: 方法名
            
        Returns:
            方法调用结果
            
        Raises:
            PermissionError: 工具未启用
        """
        if not self.is_tool_enabled(tool_name):
            raise PermissionError(
                f"Agent '{self.agent_id}' 没有权限使用工具 '{tool_name}'"
            )
        
        return await self.registry.call_tool(tool_name, method_name, *args, **kwargs)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        获取已启用的工具列表
        
        Returns:
            工具信息列表
        """
        all_tools = self.registry.list_tools()
        return [
            tool for tool in all_tools
            if tool["name"] in self.enabled_tools
        ]
    
    def get_tool_info_for_prompt(self) -> str:
        """
        生成工具说明（用于Agent的System Prompt）
        
        Returns:
            工具说明文本
        """
        if not self.enabled_tools:
            return "你当前没有可用的工具。"
        
        tools = self.get_available_tools()
        
        prompt = "## 可用工具\n\n你可以使用以下工具来完成任务：\n\n"
        
        for tool in tools:
            desc = self.registry.get_tool_description(tool["name"])
            prompt += f"### {tool['name']} ({tool['type']})\n"
            prompt += f"{desc}\n\n"
            prompt += "**可用方法**:\n"
            for method in tool["methods"]:
                prompt += f"- `{method}()`\n"
            prompt += "\n"
        
        prompt += "**使用方式**: 在你的回复中说明需要调用哪个工具的哪个方法，以及所需参数。\n"
        
        return prompt


# 全局工具注册函数（便捷接口）
def register_all_tools():
    """注册所有内置工具到全局注册表"""
    from backend.tools.file_tool import FileTool
    from backend.tools.code_runner import CodeRunner
    from backend.tools.code_search_tool import CodeSearchTool
    from backend.tools.image_gen_tool import ImageGenTool
    
    registry = ToolRegistry()
    
    # 注册文件工具
    registry.register_tool("file", FileTool())
    
    # 注册代码执行工具
    registry.register_tool("code_runner", CodeRunner())
    
    # 注册代码搜索工具
    registry.register_tool("code_search", CodeSearchTool())
    
    # 注册图片生成工具（P9新增 - Gemini 2.5 Flash Image）
    registry.register_tool("image_gen", ImageGenTool())
    
    logger.info("所有内置工具已注册")
