"""
文件: tools/game_validator.py
职责: 游戏验证工具 - 检查游戏文件完整性和代码质量
依赖: tools/file_tool.py, tools/code_runner.py
被依赖: workflows/game_dev_workflow.py (可选)

提供:
  - 检查游戏文件是否存在
  - 验证HTML和JavaScript语法
  - 检查游戏是否可以运行
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import re

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from tools.file_tool import FileTool
from tools.code_runner import CodeRunner
from utils.logger import setup_logger


class GameValidator:
    """
    游戏验证工具
    
    用于验证AI生成的游戏文件是否完整、正确
    """
    
    def __init__(self):
        """初始化游戏验证器"""
        self.file_tool = FileTool()
        self.code_runner = CodeRunner()
        self.logger = setup_logger("game_validator")
    
    async def validate_project(self, project_dir: str) -> Dict[str, Any]:
        """
        验证整个项目
        
        Args:
            project_dir: 项目目录路径
        
        Returns:
            验证结果字典
        """
        self.logger.info(f"开始验证项目: {project_dir}")
        
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        project_path = Path(project_dir)
        output_dir = project_path / "output"
        
        # 1. 检查输出目录是否存在
        check_result = await self._check_directory_exists(output_dir)
        results["checks"]["output_directory"] = check_result
        if not check_result["passed"]:
            results["valid"] = False
            results["errors"].append(check_result["message"])
            return results
        
        # 2. 检查index.html是否存在
        html_path = output_dir / "index.html"
        check_result = await self._check_file_exists(html_path, "index.html")
        results["checks"]["html_file"] = check_result
        if not check_result["passed"]:
            results["valid"] = False
            results["errors"].append(check_result["message"])
        
        # 3. 检查game.js是否存在
        js_path = output_dir / "game.js"
        check_result = await self._check_file_exists(js_path, "game.js")
        results["checks"]["js_file"] = check_result
        if not check_result["passed"]:
            results["valid"] = False
            results["errors"].append(check_result["message"])
        
        # 如果基础文件不存在，直接返回
        if not results["valid"]:
            return results
        
        # 4. 检查HTML文件结构
        check_result = await self._check_html_structure(html_path)
        results["checks"]["html_structure"] = check_result
        if not check_result["passed"]:
            results["warnings"].append(check_result["message"])
        
        # 5. 检查JavaScript语法
        check_result = await self._check_javascript_syntax(js_path)
        results["checks"]["js_syntax"] = check_result
        if not check_result["passed"]:
            results["valid"] = False
            results["errors"].append(check_result["message"])
        
        # 6. 检查游戏是否可以运行
        check_result = await self._check_game_executable(html_path)
        results["checks"]["game_executable"] = check_result
        if not check_result["passed"]:
            results["valid"] = False
            results["errors"].append(check_result["message"])
        
        # 7. 检查游戏代码完整性
        check_result = await self._check_game_completeness(js_path)
        results["checks"]["game_completeness"] = check_result
        if not check_result["passed"]:
            results["warnings"].append(check_result["message"])
        
        self.logger.info(f"项目验证完成: valid={results['valid']}")
        return results
    
    async def _check_directory_exists(self, dir_path: Path) -> Dict[str, Any]:
        """检查目录是否存在"""
        exists = self.file_tool.is_directory(str(dir_path))
        return {
            "passed": exists,
            "message": f"输出目录存在" if exists else f"输出目录不存在: {dir_path}",
            "path": str(dir_path)
        }
    
    async def _check_file_exists(self, file_path: Path, file_name: str) -> Dict[str, Any]:
        """检查文件是否存在"""
        exists = self.file_tool.exists(str(file_path))
        
        if exists:
            # 检查文件是否为空
            try:
                content = await self.file_tool.read(str(file_path))
                if not content or len(content.strip()) < 50:
                    return {
                        "passed": False,
                        "message": f"{file_name}存在但内容过少（可能是空文件）",
                        "path": str(file_path)
                    }
            except:
                pass
        
        return {
            "passed": exists,
            "message": f"{file_name}存在且有内容" if exists else f"{file_name}不存在: {file_path}",
            "path": str(file_path)
        }
    
    async def _check_html_structure(self, html_path: Path) -> Dict[str, Any]:
        """检查HTML文件结构"""
        try:
            content = await self.file_tool.read(str(html_path))
            
            # 检查必要的HTML元素
            required_elements = [
                ("<!DOCTYPE", "DOCTYPE声明"),
                ("<html", "html标签"),
                ("<head", "head标签"),
                ("<body", "body标签"),
                ("<canvas", "canvas标签"),
                ("<script", "script标签")
            ]
            
            missing_elements = []
            for pattern, name in required_elements:
                if pattern not in content:
                    missing_elements.append(name)
            
            if missing_elements:
                return {
                    "passed": False,
                    "message": f"HTML结构不完整，缺少: {', '.join(missing_elements)}",
                    "details": missing_elements
                }
            
            return {
                "passed": True,
                "message": "HTML结构完整",
                "details": []
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"读取HTML文件失败: {str(e)}",
                "details": []
            }
    
    async def _check_javascript_syntax(self, js_path: Path) -> Dict[str, Any]:
        """检查JavaScript语法"""
        try:
            content = await self.file_tool.read(str(js_path))
            
            # 使用code_runner验证语法
            result = await self.code_runner.validate_syntax(content, "javascript")
            
            if result.get("valid"):
                return {
                    "passed": True,
                    "message": "JavaScript语法正确",
                    "details": []
                }
            else:
                return {
                    "passed": False,
                    "message": f"JavaScript语法错误: {result.get('error', '未知错误')}",
                    "details": [result.get('error', '')]
                }
                
        except Exception as e:
            return {
                "passed": False,
                "message": f"验证JavaScript语法失败: {str(e)}",
                "details": []
            }
    
    async def _check_game_executable(self, html_path: Path) -> Dict[str, Any]:
        """检查游戏是否可以执行"""
        try:
            content = await self.file_tool.read(str(html_path))
            
            # 使用code_runner执行HTML（仅检查语法）
            result = await self.code_runner.execute_html(content, timeout=10.0, check_only=True)
            
            if result.get("success"):
                return {
                    "passed": True,
                    "message": "游戏代码可以正常加载",
                    "details": []
                }
            else:
                error_msg = result.get("error", "未知错误")
                return {
                    "passed": False,
                    "message": f"游戏代码无法执行: {error_msg}",
                    "details": [error_msg]
                }
                
        except Exception as e:
            return {
                "passed": False,
                "message": f"执行游戏失败: {str(e)}",
                "details": []
            }
    
    async def _check_game_completeness(self, js_path: Path) -> Dict[str, Any]:
        """检查游戏代码完整性"""
        try:
            content = await self.file_tool.read(str(js_path))
            
            # 检查必要的游戏组件
            required_components = [
                ("gameLoop", "游戏循环"),
                ("update", "更新逻辑"),
                ("render", "渲染函数"),
                ("canvas", "Canvas引用"),
                ("ctx", "绘图上下文")
            ]
            
            missing_components = []
            for pattern, name in required_components:
                if pattern not in content:
                    missing_components.append(name)
            
            if missing_components:
                return {
                    "passed": False,
                    "message": f"游戏代码可能不完整，缺少: {', '.join(missing_components)}",
                    "details": missing_components
                }
            
            return {
                "passed": True,
                "message": "游戏代码包含必要组件",
                "details": []
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"检查游戏完整性失败: {str(e)}",
                "details": []
            }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        生成验证报告
        
        Args:
            results: 验证结果
        
        Returns:
            格式化的报告字符串
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("游戏验证报告")
        report_lines.append("=" * 60)
        
        # 总体结果
        status = "✅ 通过" if results["valid"] else "❌ 失败"
        report_lines.append(f"\n总体状态: {status}\n")
        
        # 详细检查项
        report_lines.append("详细检查:")
        for check_name, check_result in results["checks"].items():
            status_icon = "✅" if check_result["passed"] else "❌"
            report_lines.append(f"  {status_icon} {check_name}: {check_result['message']}")
        
        # 错误信息
        if results["errors"]:
            report_lines.append("\n错误:")
            for error in results["errors"]:
                report_lines.append(f"  ❌ {error}")
        
        # 警告信息
        if results["warnings"]:
            report_lines.append("\n警告:")
            for warning in results["warnings"]:
                report_lines.append(f"  ⚠️ {warning}")
        
        report_lines.append("\n" + "=" * 60)
        
        return "\n".join(report_lines)


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_validator():
        """测试游戏验证器"""
        print("\n" + "="*60)
        print("测试 GameValidator")
        print("="*60 + "\n")
        
        validator = GameValidator()
        
        # 测试一个不存在的项目
        print("1. 测试不存在的项目:")
        print("-" * 60)
        results = await validator.validate_project("projects/nonexistent_game")
        print(validator.generate_report(results))
        
        print("\n✅ GameValidator 测试完成！\n")
    
    asyncio.run(test_validator())
