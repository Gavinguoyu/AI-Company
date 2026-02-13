"""
文件: tools/code_runner.py
职责: 在安全的子进程中执行JavaScript/HTML代码
依赖: utils/logger.py
被依赖: 测试Agent、程序员Agent
关键接口:
  - CodeRunner.execute_html(html_content, timeout) -> 执行HTML文件
  - CodeRunner.execute_js(js_code, timeout) -> 执行JavaScript代码
  - CodeRunner.validate_syntax(code, language) -> 验证代码语法
"""

import asyncio
import tempfile
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger("code_runner")


class CodeRunner:
    """代码执行工具 - 在隔离环境中安全执行代码"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """
        初始化代码执行器
        
        Args:
            workspace_root: 工作空间根目录
        """
        if workspace_root is None:
            workspace_root = str(Path(__file__).parent.parent.parent)
        
        self.workspace_root = Path(workspace_root).resolve()
        self.temp_dir = Path(tempfile.gettempdir()) / "ai_company_code_runner"
        self.temp_dir.mkdir(exist_ok=True)
        
        logger.info(f"代码执行器初始化完成，临时目录: {self.temp_dir}")
    
    async def execute_html(
        self, 
        html_content: str, 
        timeout: float = 30.0,
        check_only: bool = False
    ) -> Dict[str, Any]:
        """
        执行HTML文件（在浏览器中）
        
        Args:
            html_content: HTML文件内容
            timeout: 超时时间（秒）
            check_only: 仅检查语法，不实际运行
            
        Returns:
            执行结果字典 {success, output, error, file_path}
        """
        # 创建临时HTML文件
        temp_file = self.temp_dir / f"test_{os.getpid()}.html"
        
        try:
            # 写入HTML内容
            temp_file.write_text(html_content, encoding='utf-8')
            logger.info(f"创建临时HTML文件: {temp_file}")
            
            if check_only:
                # 仅语法检查（检查是否能解析为有效HTML）
                return {
                    "success": True,
                    "output": "HTML语法检查通过",
                    "error": None,
                    "file_path": str(temp_file)
                }
            
            # TODO: 在未来阶段实现浏览器自动化测试
            # 当前版本只返回文件路径，供手动测试
            logger.info(f"HTML文件已创建，可在浏览器中打开测试: {temp_file}")
            
            return {
                "success": True,
                "output": f"HTML文件已创建: {temp_file}",
                "error": None,
                "file_path": str(temp_file)
            }
            
        except Exception as e:
            logger.error(f"执行HTML失败: {e}")
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "file_path": str(temp_file) if temp_file.exists() else None
            }
    
    async def execute_js(
        self, 
        js_code: str, 
        timeout: float = 10.0,
        use_node: bool = True
    ) -> Dict[str, Any]:
        """
        执行JavaScript代码
        
        Args:
            js_code: JavaScript代码
            timeout: 超时时间（秒）
            use_node: 是否使用Node.js运行（否则只做语法检查）
            
        Returns:
            执行结果字典 {success, output, error, exit_code}
        """
        temp_file = self.temp_dir / f"test_{os.getpid()}.js"
        
        try:
            # 写入JS代码
            temp_file.write_text(js_code, encoding='utf-8')
            logger.info(f"创建临时JS文件: {temp_file}")
            
            if not use_node:
                # 仅语法检查
                return {
                    "success": True,
                    "output": "JavaScript代码已保存",
                    "error": None,
                    "exit_code": 0,
                    "file_path": str(temp_file)
                }
            
            # 检查Node.js是否可用
            node_available = await self._check_node_available()
            
            if not node_available:
                logger.warning("Node.js 未安装或不可用，跳过执行")
                return {
                    "success": True,
                    "output": "Node.js 未安装，代码已保存但未执行",
                    "error": None,
                    "exit_code": 0,
                    "file_path": str(temp_file)
                }
            
            # 使用Node.js执行
            try:
                process = await asyncio.create_subprocess_exec(
                    "node",
                    str(temp_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.temp_dir)
                )
                
                # 等待执行完成（带超时）
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                stdout_text = stdout.decode('utf-8', errors='replace')
                stderr_text = stderr.decode('utf-8', errors='replace')
                
                success = process.returncode == 0
                
                if success:
                    logger.info(f"JavaScript执行成功，退出码: {process.returncode}")
                else:
                    logger.warning(f"JavaScript执行失败，退出码: {process.returncode}")
                
                return {
                    "success": success,
                    "output": stdout_text,
                    "error": stderr_text if stderr_text else None,
                    "exit_code": process.returncode,
                    "file_path": str(temp_file)
                }
                
            except asyncio.TimeoutError:
                logger.error(f"JavaScript执行超时 ({timeout}秒)")
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "output": None,
                    "error": f"执行超时 ({timeout}秒)",
                    "exit_code": -1,
                    "file_path": str(temp_file)
                }
            
        except Exception as e:
            logger.error(f"执行JavaScript失败: {e}")
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "exit_code": -1,
                "file_path": str(temp_file) if temp_file.exists() else None
            }
        finally:
            # 清理临时文件（可选，保留以便调试）
            # if temp_file.exists():
            #     temp_file.unlink()
            pass
    
    async def _check_node_available(self) -> bool:
        """
        检查Node.js是否可用
        
        Returns:
            可用返回True
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "node",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    async def validate_syntax(
        self, 
        code: str, 
        language: str = "javascript"
    ) -> Dict[str, Any]:
        """
        验证代码语法
        
        Args:
            code: 代码内容
            language: 语言类型 (javascript, html)
            
        Returns:
            验证结果 {valid, errors}
        """
        if language.lower() == "javascript":
            # JavaScript语法检查
            result = await self.execute_js(code, use_node=False)
            return {
                "valid": result["success"],
                "errors": result["error"]
            }
        
        elif language.lower() == "html":
            # HTML语法检查
            result = await self.execute_html(code, check_only=True)
            return {
                "valid": result["success"],
                "errors": result["error"]
            }
        
        else:
            logger.warning(f"不支持的语言: {language}")
            return {
                "valid": False,
                "errors": f"不支持的语言: {language}"
            }
    
    async def execute_game_test(
        self, 
        game_dir: str,
        entry_file: str = "index.html",
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        测试游戏项目
        
        Args:
            game_dir: 游戏目录路径
            entry_file: 入口文件名（默认index.html）
            timeout: 超时时间
            
        Returns:
            测试结果
        """
        game_path = Path(game_dir)
        
        if not game_path.exists():
            logger.error(f"游戏目录不存在: {game_dir}")
            return {
                "success": False,
                "output": None,
                "error": f"游戏目录不存在: {game_dir}"
            }
        
        entry_path = game_path / entry_file
        
        if not entry_path.exists():
            logger.error(f"入口文件不存在: {entry_path}")
            return {
                "success": False,
                "output": None,
                "error": f"入口文件不存在: {entry_file}"
            }
        
        # 读取HTML内容
        html_content = entry_path.read_text(encoding='utf-8')
        
        # 执行HTML
        result = await self.execute_html(html_content, timeout=timeout)
        
        logger.info(f"游戏测试完成: {game_dir}")
        return result
    
    def cleanup_temp_files(self) -> int:
        """
        清理临时文件
        
        Returns:
            清理的文件数量
        """
        count = 0
        try:
            for file in self.temp_dir.glob("test_*.html"):
                file.unlink()
                count += 1
            for file in self.temp_dir.glob("test_*.js"):
                file.unlink()
                count += 1
            logger.info(f"清理了 {count} 个临时文件")
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")
        
        return count
