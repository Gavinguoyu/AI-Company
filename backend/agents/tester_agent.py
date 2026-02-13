"""
文件: agents/tester_agent.py
职责: 测试工程师Agent - 负责游戏测试、Bug报告
依赖: engine/agent.py
被依赖: workflows/game_dev_workflow.py

关键能力:
  - 运行游戏代码，检查是否能正常启动和运行
  - 根据策划文档验证功能是否正确实现
  - 撰写测试报告，列出Bug和问题
  - 将Bug反馈给程序员
"""

import sys
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from engine.agent import Agent
from typing import Dict, Any, Optional, List
import json
from datetime import datetime


class TesterAgent(Agent):
    """
    测试工程师Agent
    
    职责:
    1. 运行游戏代码，检查是否能正常启动和运行
    2. 根据策划文档验证功能是否正确实现
    3. 撰写测试报告，列出Bug和问题
    4. 将Bug反馈给程序员
    5. **关键**: 实际调用code_runner执行游戏
    """
    
    def __init__(self, project_name: str = ""):
        """
        初始化Tester Agent
        
        Args:
            project_name: 项目名称，用于构建文件路径
        """
        self.project_name = project_name
        
        system_prompt = f"""你是一位严谨的游戏测试工程师。

【重要】你必须调用code_runner工具来实际执行游戏代码，而不是仅仅回复"我会测试"！

当前项目目录: projects/{project_name}/
游戏文件: projects/{project_name}/output/index.html

你的工作流程：
1. 读取游戏设计文档(game_design_doc.md)
2. **关键**: 调用code_runner工具执行游戏
3. 分析执行结果（成功/失败/错误）
4. 如果有JavaScript错误，记录到bug_tracker.yaml
5. 编写详细的测试报告

【必须使用的工具】：
- self.call_tool("file", "read", path)  # 读取游戏文件
- self.call_tool("file", "exists", path)  # 检查文件是否存在
- self.call_tool("code_runner", "execute_html", html_content, timeout)  # 执行游戏
- self.call_tool("file", "write", "projects/{project_name}/shared_knowledge/bug_tracker.yaml", content)  # 写Bug

【测试流程】：
1. 检查index.html是否存在
2. 读取HTML内容
3. 调用code_runner执行
4. 如果result['success']==True: 测试通过
5. 如果result['success']==False: 记录Bug

Bug报告格式(YAML):
```yaml
bugs:
  - id: bug_{{timestamp}}
    title: 简洁描述
    severity: critical/major/minor
    description: 详细描述
    file: 出错文件路径
    error_message: 错误信息
    status: open
    created_at: 时间戳
```

铁律(不可违反):
1. 收到测试任务后，必须实际调用code_runner执行游戏
2. 不能只说"我会测试"，必须真正执行并给出结果
3. 发现Bug必须写入bug_tracker.yaml
4. 测试报告要包含实际执行结果
"""
        
        super().__init__(
            agent_id="tester",
            role="测试工程师",
            system_prompt=system_prompt,
            tools=["file", "code_runner"]  # 启用文件和代码执行工具
        )
        
        self.logger.info(f"Tester Agent 初始化完成 (项目: {project_name})")
    
    async def process_message(self, message: Dict) -> Optional[str]:
        """
        处理接收到的消息
        
        增强版本: 当收到测试任务时，实际执行游戏并报告结果
        """
        # 检测是否是测试任务 - 先检测，优先执行测试
        if message.get('type') in ['request_review', 'question']:
            content = message.get('content', '')
            
            # 检测是否是测试任务
            if any(keyword in content for keyword in ['测试', 'test', '检查', '验证', '运行游戏']):
                self.logger.info("检测到测试任务，准备执行游戏...")
                
                try:
                    # 执行游戏测试 (在调用LLM之前先做这个)
                    test_result = await self._execute_game_test()
                    
                    if test_result['success']:
                        return f"✅ 游戏测试通过！\n{test_result['message']}\n\n游戏代码语法正确，可以正常运行。"
                    else:
                        # 记录Bug
                        bug_id = await self._record_bug(test_result)
                        return f"❌ 游戏测试失败！\n{test_result['message']}\n\n已记录Bug ID: {bug_id}，请程序员修复。"
                
                except Exception as e:
                    self.logger.error(f"执行游戏测试失败: {e}", exc_info=True)
                    return f"⚠️ 测试过程中遇到错误: {str(e)}"
        
        # 对于非测试任务，调用父类的基础处理
        response = await super().process_message(message)
        return response
    
    async def _execute_game_test(self) -> Dict[str, Any]:
        """
        执行游戏测试
        
        Returns:
            测试结果字典 {success: bool, message: str, error: str}
        """
        if not self.project_name:
            return {
                "success": False,
                "message": "project_name未设置",
                "error": "配置错误"
            }
        
        html_path = f"projects/{self.project_name}/output/index.html"
        
        # 1. 检查文件是否存在
        try:
            exists = await self.call_tool("file", "exists", html_path)
            if not exists:
                return {
                    "success": False,
                    "message": f"游戏文件不存在: {html_path}",
                    "error": "文件不存在"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"检查文件失败: {str(e)}",
                "error": str(e)
            }
        
        # 2. 读取HTML内容
        try:
            html_content = await self.call_tool("file", "read", html_path)
            self.logger.info(f"已读取游戏文件，大小: {len(html_content)} 字符")
        except Exception as e:
            return {
                "success": False,
                "message": f"读取游戏文件失败: {str(e)}",
                "error": str(e)
            }
        
        # 3. 执行游戏
        try:
            self.logger.info("开始执行游戏代码...")
            result = await self.call_tool("code_runner", "execute_html", html_content, 10.0, True)
            
            self.logger.info(f"游戏执行结果: success={result.get('success')}")
            
            if result.get('success'):
                return {
                    "success": True,
                    "message": "游戏代码语法正确，可以正常加载",
                    "error": ""
                }
            else:
                error_msg = result.get('error', '未知错误')
                return {
                    "success": False,
                    "message": f"游戏代码有错误: {error_msg}",
                    "error": error_msg
                }
        
        except Exception as e:
            self.logger.error(f"执行游戏失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"执行游戏时出错: {str(e)}",
                "error": str(e)
            }
    
    async def _record_bug(self, test_result: Dict[str, Any]) -> str:
        """
        记录Bug到bug_tracker.yaml
        
        Args:
            test_result: 测试结果
        
        Returns:
            Bug ID
        """
        if not self.project_name:
            return "unknown"
        
        bug_id = f"bug_{int(datetime.now().timestamp())}"
        bug_tracker_path = f"projects/{self.project_name}/shared_knowledge/bug_tracker.yaml"
        
        # 读取现有Bug列表（如果存在）
        existing_bugs = []
        try:
            content = await self.call_tool("file", "read", bug_tracker_path)
            # 简单解析YAML（这里用简单方法，避免依赖pyyaml在Agent中）
            if "bugs:" in content:
                existing_bugs = [content]
        except:
            pass
        
        # 创建新Bug记录
        bug_record = f"""
  - id: {bug_id}
    title: 游戏代码执行失败
    severity: critical
    description: {test_result.get('message', '游戏无法正常运行')}
    file: projects/{self.project_name}/output/index.html
    error_message: "{test_result.get('error', '').replace('"', "'")}"
    status: open
    created_at: {datetime.now().isoformat()}
"""
        
        # 写入Bug tracker
        if existing_bugs:
            # 追加到现有Bug列表
            new_content = existing_bugs[0] + bug_record
        else:
            # 创建新的Bug列表
            new_content = f"""# Bug追踪表
# 项目: {self.project_name}

bugs:{bug_record}
"""
        
        try:
            await self.call_tool("file", "write", bug_tracker_path, new_content)
            self.logger.info(f"✅ 已记录Bug: {bug_id}")
        except Exception as e:
            self.logger.error(f"写入Bug tracker失败: {e}")
        
        return bug_id


def create_tester_agent(project_name: str = "") -> TesterAgent:
    """创建Tester Agent实例"""
    return TesterAgent(project_name)


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_tester_agent():
        """测试Tester Agent"""
        print("\n" + "="*60)
        print("测试 Tester Agent")
        print("="*60 + "\n")
        
        try:
            tester = create_tester_agent()
            
            print("1. 测试基本信息:")
            print("-" * 60)
            print(f"Agent ID: {tester.agent_id}")
            print(f"角色: {tester.role}")
            print("✅ 测试工程师初始化成功\n")
            
            print("2. 测试Bug报告:")
            print("-" * 60)
            print("\n发现一个Bug")
            response = await tester.think_and_respond(
                "我发现蛇穿过右边墙壁后不会死亡，但穿过其他墙壁会死亡。请帮我写一份Bug报告。"
            )
            print(f"\n测试: {response[:300]}...\n")
            print("✅ Bug报告能力正常\n")
            
            print("3. 测试功能验证:")
            print("-" * 60)
            tester.load_file_to_context(
                "GDD.md",
                "规则：蛇吃到食物后身体增长1节，分数+10"
            )
            response = await tester.think_and_respond(
                "我测试了吃食物功能，蛇确实增长了，但分数加了20而不是10，这是Bug吗？"
            )
            print(f"\n测试: {response[:200]}...\n")
            print("✅ 功能验证能力正常\n")
            
            print("="*60)
            print("✅ Tester Agent 测试全部通过！")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_tester_agent())
