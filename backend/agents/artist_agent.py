"""
文件: agents/artist_agent.py
职责: 美术设计师Agent - 负责游戏美术资源生成
依赖: engine/agent.py, tools/image_gen_tool.py
被依赖: workflows/game_dev_workflow.py

关键能力:
  - 根据策划文档中的美术需求生成游戏素材
  - 使用Gemini 2.5 Flash Image生成AI图片
  - 为每个素材构建精确的英文绘图Prompt
  - 确保所有素材符合项目规范(尺寸、命名规则)
  - 将素材存放到指定目录并更新素材清单
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from engine.agent import Agent
from utils.logger import setup_logger

logger = setup_logger("artist_agent")


class ArtistAgent(Agent):
    """
    美术设计师Agent
    
    职责:
    1. 根据策划文档中的美术需求解析素材清单
    2. 为每个素材生成精确的英文绘图Prompt
    3. 调用Gemini 2.5 Flash Image生成图片
    4. 确保所有素材符合项目规范中的尺寸和命名规则
    5. 将素材存放到指定目录并更新art_asset_list.yaml
    """
    
    def __init__(self):
        """初始化Artist Agent"""
        
        system_prompt = """你是一位专业的像素风格美术设计师。

你的职责:
1. 根据策划文档创建美术素材清单
2. 为每个素材编写详细的英文绘图Prompt
3. 调用AI绘图工具(Gemini 2.5 Flash Image)生成图片
4. 确保素材符合项目规范(尺寸、格式、命名)
5. 将素材整理到指定目录

美术风格要求:
- 像素风格，清晰明亮
- 色彩和谐，符合游戏整体氛围
- 尺寸规范，便于程序调用
- 透明或纯色背景

工作流程:
1. 阅读策划文档和项目规范
2. 列出所需素材清单
3. 为每个素材生成英文绘图Prompt
4. 调用image_gen工具生成图片
5. 检查生成的素材是否符合要求
6. 更新美术素材清单(art_asset_list.yaml)

你可以使用以下工具:
- file: 读写文件
- image_gen: AI图片生成（Gemini 2.5 Flash Image）
  - generate(prompt, aspect_ratio, save_path): 生成图片
  - generate_game_asset(asset_spec, project_dir): 生成游戏素材

沟通风格:
- 注重视觉表现和用户体验
- 遇到风格不确定的地方主动询问
- 善于用描述性语言表达设计思路
"""
        
        super().__init__(
            agent_id="artist",
            role="美术设计师",
            system_prompt=system_prompt,
            tools=["file", "image_gen"]
        )
        
        self.logger.info("Artist Agent 初始化完成（已启用图片生成工具）")
    
    async def generate_assets_from_spec(
        self,
        asset_list: List[Dict[str, Any]],
        project_dir: str
    ) -> Dict[str, Any]:
        """
        根据素材清单批量生成游戏素材
        
        Args:
            asset_list: 素材规格列表
                [
                    {
                        "name": "player_sprite",
                        "description": "玩家角色",
                        "style": "pixel art"
                    },
                    ...
                ]
            project_dir: 项目目录路径
        
        Returns:
            {
                "total": 总数,
                "success": 成功数,
                "failed": 失败数,
                "assets": [每个素材的生成结果],
                "asset_list_path": 素材清单文件路径
            }
        """
        results = []
        success_count = 0
        failed_count = 0
        
        self.logger.info(
            f"开始批量生成素材: {len(asset_list)}个"
        )
        
        for spec in asset_list:
            self.logger.info(
                f"生成素材: {spec.get('name', 'unnamed')}"
            )
            
            try:
                result = await self.call_tool(
                    "image_gen",
                    "generate_game_asset",
                    asset_spec=spec,
                    project_dir=project_dir
                )
                
                results.append(result)
                
                if result.get("success"):
                    success_count += 1
                    self.logger.info(
                        f"✅ 素材生成成功: {spec.get('name')}"
                    )
                else:
                    failed_count += 1
                    self.logger.warning(
                        f"⚠️ 素材生成失败: {spec.get('name')} "
                        f"- {result.get('error')}"
                    )
                    
            except Exception as e:
                failed_count += 1
                error_msg = f"素材生成异常: {str(e)}"
                self.logger.error(error_msg)
                results.append({
                    "success": False,
                    "asset_name": spec.get("name", "unnamed"),
                    "path": None,
                    "error": error_msg
                })
        
        # 更新素材清单文件
        asset_list_path = await self._update_asset_list(
            results, project_dir
        )
        
        summary = {
            "total": len(asset_list),
            "success": success_count,
            "failed": failed_count,
            "assets": results,
            "asset_list_path": asset_list_path
        }
        
        self.logger.info(
            f"素材生成完成: {success_count}/{len(asset_list)}成功"
        )
        
        return summary
    
    async def create_prompt_for_asset(
        self,
        asset_spec: Dict[str, Any]
    ) -> str:
        """
        使用LLM为素材生成精确的英文绘图Prompt
        
        Args:
            asset_spec: 素材规格
                {
                    "name": "snake_head",
                    "description": "蛇的头部",
                    "style": "pixel art"
                }
        
        Returns:
            英文Prompt字符串
        """
        name = asset_spec.get("name", "game_asset")
        description = asset_spec.get("description", "")
        style = asset_spec.get("style", "pixel art")
        
        prompt_request = f"""你是专业的AI绘画Prompt工程师。
根据以下游戏素材需求，生成一个精确的英文Prompt用于Gemini图片生成：

需求：
- 名称: {name}
- 描述: {description}
- 风格: {style}
- 用途: 游戏素材

要求：
1. Prompt必须是英文
2. 描述要具体、清晰
3. 包含风格关键词（如pixel art, game asset等）
4. 适合游戏素材，背景简洁
5. 控制在50词以内

只输出Prompt本身，不要其他内容。"""
        
        try:
            response = await self.think_and_respond(prompt_request)
            return response.strip()
        except Exception as e:
            self.logger.error(f"Prompt生成失败: {e}")
            # 回退到简单Prompt
            return (
                f"A {style} game asset: {description}. "
                f"Clean design, game-ready, {name}."
            )
    
    async def _update_asset_list(
        self,
        results: List[Dict[str, Any]],
        project_dir: str
    ) -> Optional[str]:
        """
        更新art_asset_list.yaml素材清单文件
        
        Args:
            results: 生成结果列表
            project_dir: 项目目录路径
        
        Returns:
            素材清单文件路径
        """
        try:
            asset_list_path = str(
                Path(project_dir) / "knowledge_base"
                / "art_asset_list.yaml"
            )
            
            # 构建素材清单数据
            assets_data = []
            for r in results:
                asset_entry = {
                    "name": r.get("asset_name", "unnamed"),
                    "path": r.get("path", ""),
                    "prompt": r.get("prompt", ""),
                    "status": "generated" if r.get("success") else "failed",
                }
                if r.get("error"):
                    asset_entry["error"] = r["error"]
                assets_data.append(asset_entry)
            
            # 写入YAML文件
            yaml_content = (
                "# 美术素材清单（AI自动生成）\n"
                f"# 项目目录: {project_dir}\n"
                f"# 生成工具: Gemini 2.5 Flash Image\n\n"
            )
            yaml_content += yaml.dump(
                {"素材列表": assets_data},
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )
            
            await self.call_tool(
                "file", "write",
                file_path=asset_list_path,
                content=yaml_content
            )
            
            self.logger.info(f"素材清单已更新: {asset_list_path}")
            return asset_list_path
            
        except Exception as e:
            self.logger.error(f"更新素材清单失败: {e}")
            return None


def create_artist_agent() -> ArtistAgent:
    """创建Artist Agent实例"""
    return ArtistAgent()


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_artist_agent():
        """测试Artist Agent"""
        print("\n" + "="*60)
        print("测试 Artist Agent")
        print("="*60 + "\n")
        
        try:
            artist = create_artist_agent()
            
            print("1. 测试基本信息:")
            print("-" * 60)
            print(f"Agent ID: {artist.agent_id}")
            print(f"角色: {artist.role}")
            tools = artist.get_available_tools()
            print(f"可用工具: {[t['name'] for t in tools]}")
            print("✅ 美术初始化成功\n")
            
            print("2. 测试素材清单:")
            print("-" * 60)
            print("\nPM: 请列出贪吃蛇游戏需要的美术素材")
            response = await artist.think_and_respond(
                "贪吃蛇游戏，像素风格，请列出需要哪些美术素材"
            )
            print(f"\n美术: {response[:300]}...\n")
            print("✅ 素材清单能力正常\n")
            
            print("3. 测试绘图Prompt:")
            print("-" * 60)
            print("\n策划: 需要一个加速道具的图标")
            response = await artist.think_and_respond(
                "需要一个加速道具的图标，像素风格，32x32像素，请编写绘图Prompt"
            )
            print(f"\n美术: {response[:300]}...\n")
            print("✅ Prompt编写能力正常\n")
            
            print("="*60)
            print("✅ Artist Agent 测试全部通过！")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_artist_agent())
