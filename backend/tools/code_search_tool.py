"""
文件: tools/code_search_tool.py
职责: 搜索代码中的函数、类、变量定义
依赖: utils/logger.py
被依赖: 程序员Agent
关键接口:
  - CodeSearchTool.search_function(name, directory) -> 搜索函数定义
  - CodeSearchTool.search_class(name, directory) -> 搜索类定义
  - CodeSearchTool.search_variable(name, directory) -> 搜索变量定义
  - CodeSearchTool.get_api_registry(registry_file) -> 读取API注册表
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger("code_search")


class CodeSearchTool:
    """代码搜索工具 - 帮助Agent查找已有的代码实现"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """
        初始化代码搜索工具
        
        Args:
            workspace_root: 工作空间根目录
        """
        if workspace_root is None:
            workspace_root = str(Path(__file__).parent.parent.parent)
        
        self.workspace_root = Path(workspace_root).resolve()
        logger.info(f"代码搜索工具初始化完成，工作空间: {self.workspace_root}")
    
    async def search_function(
        self, 
        function_name: str, 
        directory: str = ".",
        file_pattern: str = "*.js"
    ) -> List[Dict[str, Any]]:
        """
        搜索函数定义
        
        Args:
            function_name: 函数名
            directory: 搜索目录（相对于workspace）
            file_pattern: 文件匹配模式（如 *.js, *.py）
            
        Returns:
            匹配结果列表 [{file, line, content}]
        """
        search_dir = self.workspace_root / directory
        
        if not search_dir.exists():
            logger.warning(f"搜索目录不存在: {search_dir}")
            return []
        
        results = []
        
        # JavaScript函数定义的正则模式
        patterns = [
            rf'function\s+{function_name}\s*\(',  # function foo()
            rf'const\s+{function_name}\s*=\s*function',  # const foo = function
            rf'const\s+{function_name}\s*=\s*\(',  # const foo = ()
            rf'let\s+{function_name}\s*=\s*function',  # let foo = function
            rf'let\s+{function_name}\s*=\s*\(',  # let foo = ()
            rf'var\s+{function_name}\s*=\s*function',  # var foo = function
            rf'{function_name}\s*:\s*function',  # foo: function
            rf'{function_name}\s*\([^)]*\)\s*{{',  # foo() { (方法简写)
        ]
        
        # 遍历所有匹配的文件
        for file_path in search_dir.rglob(file_pattern):
            if not file_path.is_file():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, start=1):
                    for pattern in patterns:
                        if re.search(pattern, line):
                            results.append({
                                "file": str(file_path.relative_to(self.workspace_root)),
                                "line": i,
                                "content": line.strip(),
                                "type": "function"
                            })
                            break  # 一行只记录一次
            
            except Exception as e:
                logger.warning(f"读取文件失败 {file_path}: {e}")
                continue
        
        logger.info(f"搜索函数 '{function_name}' 找到 {len(results)} 个结果")
        return results
    
    async def search_class(
        self, 
        class_name: str, 
        directory: str = ".",
        file_pattern: str = "*.js"
    ) -> List[Dict[str, Any]]:
        """
        搜索类定义
        
        Args:
            class_name: 类名
            directory: 搜索目录
            file_pattern: 文件匹配模式
            
        Returns:
            匹配结果列表
        """
        search_dir = self.workspace_root / directory
        
        if not search_dir.exists():
            logger.warning(f"搜索目录不存在: {search_dir}")
            return []
        
        results = []
        
        # JavaScript类定义的正则模式
        patterns = [
            rf'class\s+{class_name}\s*{{',  # class Foo {
            rf'class\s+{class_name}\s+extends',  # class Foo extends Bar
        ]
        
        for file_path in search_dir.rglob(file_pattern):
            if not file_path.is_file():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, start=1):
                    for pattern in patterns:
                        if re.search(pattern, line):
                            results.append({
                                "file": str(file_path.relative_to(self.workspace_root)),
                                "line": i,
                                "content": line.strip(),
                                "type": "class"
                            })
                            break
            
            except Exception as e:
                logger.warning(f"读取文件失败 {file_path}: {e}")
                continue
        
        logger.info(f"搜索类 '{class_name}' 找到 {len(results)} 个结果")
        return results
    
    async def search_variable(
        self, 
        var_name: str, 
        directory: str = ".",
        file_pattern: str = "*.js"
    ) -> List[Dict[str, Any]]:
        """
        搜索变量定义
        
        Args:
            var_name: 变量名
            directory: 搜索目录
            file_pattern: 文件匹配模式
            
        Returns:
            匹配结果列表
        """
        search_dir = self.workspace_root / directory
        
        if not search_dir.exists():
            logger.warning(f"搜索目录不存在: {search_dir}")
            return []
        
        results = []
        
        # 变量定义的正则模式
        patterns = [
            rf'const\s+{var_name}\s*=',  # const FOO =
            rf'let\s+{var_name}\s*=',    # let foo =
            rf'var\s+{var_name}\s*=',    # var foo =
        ]
        
        for file_path in search_dir.rglob(file_pattern):
            if not file_path.is_file():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for i, line in enumerate(lines, start=1):
                    for pattern in patterns:
                        if re.search(pattern, line):
                            results.append({
                                "file": str(file_path.relative_to(self.workspace_root)),
                                "line": i,
                                "content": line.strip(),
                                "type": "variable"
                            })
                            break
            
            except Exception as e:
                logger.warning(f"读取文件失败 {file_path}: {e}")
                continue
        
        logger.info(f"搜索变量 '{var_name}' 找到 {len(results)} 个结果")
        return results
    
    async def search_all(
        self, 
        name: str, 
        directory: str = ".",
        file_pattern: str = "*.js"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        搜索所有类型的定义（函数、类、变量）
        
        Args:
            name: 名称
            directory: 搜索目录
            file_pattern: 文件匹配模式
            
        Returns:
            分类结果字典 {functions, classes, variables}
        """
        functions = await self.search_function(name, directory, file_pattern)
        classes = await self.search_class(name, directory, file_pattern)
        variables = await self.search_variable(name, directory, file_pattern)
        
        return {
            "functions": functions,
            "classes": classes,
            "variables": variables,
            "total": len(functions) + len(classes) + len(variables)
        }
    
    async def get_api_registry(self, registry_file: str = "shared_knowledge/api_registry.yaml") -> Dict[str, Any]:
        """
        读取并解析API注册表
        
        Args:
            registry_file: 注册表文件路径（相对于项目目录）
            
        Returns:
            API注册表字典，如果文件不存在则返回空字典
        """
        import yaml
        
        registry_path = self.workspace_root / registry_file
        
        if not registry_path.exists():
            logger.info(f"API注册表不存在: {registry_file}")
            return {}
        
        try:
            content = registry_path.read_text(encoding='utf-8')
            data = yaml.safe_load(content)
            logger.info(f"成功读取API注册表: {registry_file}")
            return data or {}
        except Exception as e:
            logger.error(f"解析API注册表失败: {e}")
            return {}
    
    async def check_function_exists(
        self, 
        function_name: str,
        registry_file: str = "shared_knowledge/api_registry.yaml"
    ) -> bool:
        """
        检查函数是否已在API注册表中
        
        Args:
            function_name: 函数名
            registry_file: 注册表文件路径
            
        Returns:
            存在返回True
        """
        registry = await self.get_api_registry(registry_file)
        
        if not registry or "modules" not in registry:
            return False
        
        # 遍历所有模块，查找函数
        for module_path, module_info in registry["modules"].items():
            if "exports" not in module_info:
                continue
            
            for export in module_info["exports"]:
                # 检查函数名或类中的方法名
                if export.get("name") == function_name:
                    return True
                
                # 检查类方法
                if "methods" in export:
                    for method in export["methods"]:
                        if function_name in method.get("signature", ""):
                            return True
        
        return False
    
    def get_file_imports(self, file_path: str) -> List[str]:
        """
        获取文件中的所有import语句
        
        Args:
            file_path: 文件路径
            
        Returns:
            import语句列表
        """
        path = self.workspace_root / file_path
        
        if not path.exists() or not path.is_file():
            return []
        
        imports = []
        
        try:
            content = path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 匹配import语句
            import_patterns = [
                r'import\s+.*\s+from\s+["\'].*["\']',  # import ... from "..."
                r'import\s+["\'].*["\']',              # import "..."
                r'require\(["\'].*["\']\)',            # require("...")
            ]
            
            for line in lines:
                for pattern in import_patterns:
                    if re.search(pattern, line):
                        imports.append(line.strip())
                        break
        
        except Exception as e:
            logger.warning(f"读取文件导入失败 {file_path}: {e}")
        
        return imports
