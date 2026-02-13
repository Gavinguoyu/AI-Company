"""
文件: tools/file_tool.py
职责: 提供安全的文件读写操作工具
依赖: utils/logger.py
被依赖: Agent基类、各具体Agent
关键接口:
  - FileTool.read(file_path) -> 读取文件内容
  - FileTool.write(file_path, content) -> 写入文件
  - FileTool.exists(file_path) -> 检查文件是否存在
  - FileTool.list_directory(dir_path) -> 列出目录内容
"""

import os
import aiofiles
from pathlib import Path
from typing import Optional, List, Dict, Any
from utils.logger import setup_logger

logger = setup_logger("file_tool")


class FileTool:
    """文件操作工具 - 为Agent提供安全的文件读写能力"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """
        初始化文件工具
        
        Args:
            workspace_root: 工作空间根目录，默认为项目根目录
        """
        if workspace_root is None:
            # 默认为项目根目录 (backend的父目录)
            workspace_root = str(Path(__file__).parent.parent.parent)
        
        self.workspace_root = Path(workspace_root).resolve()
        logger.info(f"文件工具初始化完成，工作空间: {self.workspace_root}")
    
    def _get_absolute_path(self, file_path: str) -> Path:
        """
        将相对路径转换为绝对路径，并确保在工作空间内
        
        Args:
            file_path: 文件路径（相对或绝对）
            
        Returns:
            绝对路径Path对象
            
        Raises:
            ValueError: 路径在工作空间外
        """
        path = Path(file_path)
        
        # 如果是相对路径，相对于workspace_root
        if not path.is_absolute():
            path = self.workspace_root / path
        
        # 解析路径（处理 .. 等）
        path = path.resolve()
        
        # 安全检查：确保路径在工作空间内
        try:
            path.relative_to(self.workspace_root)
        except ValueError:
            raise ValueError(f"拒绝访问工作空间外的路径: {path}")
        
        return path
    
    async def read(self, file_path: str) -> str:
        """
        异步读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容字符串
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 路径不安全
        """
        path = self._get_absolute_path(file_path)
        
        if not path.exists():
            logger.error(f"文件不存在: {path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not path.is_file():
            logger.error(f"不是文件: {path}")
            raise ValueError(f"不是文件: {file_path}")
        
        try:
            async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
                content = await f.read()
            logger.info(f"成功读取文件: {file_path} ({len(content)} 字符)")
            return content
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            raise
    
    async def write(self, file_path: str, content: str) -> bool:
        """
        异步写入文件（覆盖模式）
        
        Args:
            file_path: 文件路径
            content: 要写入的内容
            
        Returns:
            成功返回True
            
        Raises:
            ValueError: 路径不安全
        """
        path = self._get_absolute_path(file_path)
        
        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
                await f.write(content)
            logger.info(f"成功写入文件: {file_path} ({len(content)} 字符)")
            return True
        except Exception as e:
            logger.error(f"写入文件失败 {file_path}: {e}")
            raise
    
    async def append(self, file_path: str, content: str) -> bool:
        """
        异步追加内容到文件
        
        Args:
            file_path: 文件路径
            content: 要追加的内容
            
        Returns:
            成功返回True
        """
        path = self._get_absolute_path(file_path)
        
        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiofiles.open(path, mode='a', encoding='utf-8') as f:
                await f.write(content)
            logger.info(f"成功追加到文件: {file_path} ({len(content)} 字符)")
            return True
        except Exception as e:
            logger.error(f"追加文件失败 {file_path}: {e}")
            raise
    
    def exists(self, file_path: str) -> bool:
        """
        检查文件或目录是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            存在返回True，不存在返回False
        """
        try:
            path = self._get_absolute_path(file_path)
            exists = path.exists()
            logger.debug(f"检查文件存在: {file_path} -> {exists}")
            return exists
        except ValueError:
            # 路径不安全，视为不存在
            return False
    
    def is_file(self, file_path: str) -> bool:
        """
        检查路径是否为文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是文件返回True
        """
        try:
            path = self._get_absolute_path(file_path)
            return path.is_file()
        except ValueError:
            return False
    
    def is_directory(self, file_path: str) -> bool:
        """
        检查路径是否为目录
        
        Args:
            file_path: 目录路径
            
        Returns:
            是目录返回True
        """
        try:
            path = self._get_absolute_path(file_path)
            return path.is_dir()
        except ValueError:
            return False
    
    async def list_directory(self, dir_path: str = ".") -> List[Dict[str, Any]]:
        """
        列出目录内容
        
        Args:
            dir_path: 目录路径，默认为当前工作目录
            
        Returns:
            文件/目录信息列表，每项包含 name, type, size
            
        Raises:
            NotADirectoryError: 不是目录
        """
        path = self._get_absolute_path(dir_path)
        
        if not path.exists():
            logger.error(f"目录不存在: {path}")
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        
        if not path.is_dir():
            logger.error(f"不是目录: {path}")
            raise NotADirectoryError(f"不是目录: {dir_path}")
        
        items = []
        for item in path.iterdir():
            item_info = {
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "path": str(item.relative_to(self.workspace_root))
            }
            items.append(item_info)
        
        logger.info(f"列出目录: {dir_path} ({len(items)} 项)")
        return items
    
    async def delete(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            成功返回True
            
        Raises:
            IsADirectoryError: 是目录而非文件
        """
        path = self._get_absolute_path(file_path)
        
        if not path.exists():
            logger.warning(f"文件不存在，无需删除: {file_path}")
            return True
        
        if path.is_dir():
            raise IsADirectoryError(f"不能删除目录: {file_path}")
        
        try:
            path.unlink()
            logger.info(f"成功删除文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"删除文件失败 {file_path}: {e}")
            raise
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典 {name, type, size, modified_time}
        """
        path = self._get_absolute_path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        stat = path.stat()
        
        info = {
            "name": path.name,
            "type": "directory" if path.is_dir() else "file",
            "size": stat.st_size,
            "modified_time": stat.st_mtime,
            "path": str(path.relative_to(self.workspace_root))
        }
        
        return info
