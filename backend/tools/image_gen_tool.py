"""
文件: tools/image_gen_tool.py
职责: AI图片生成工具 - 封装Gemini 2.5 Flash Image API
依赖: google-genai, Pillow, config.py, utils/logger.py
被依赖: agents/artist_agent.py, tool_registry.py
关键接口:
  - ImageGenTool.generate(prompt, aspect_ratio, save_path) -> 生成图片
  - ImageGenTool.generate_game_asset(asset_spec, project_dir) -> 生成游戏素材
"""

import io
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

from google import genai
from google.genai import types
from PIL import Image

from config import Config
from utils.logger import setup_logger

logger = setup_logger("image_gen_tool")

# 每个项目最多生成的图片数量（成本控制）
MAX_IMAGES_PER_PROJECT = 20

# 支持的宽高比
VALID_ASPECT_RATIOS = [
    "1:1", "2:3", "3:2", "3:4", "4:3",
    "4:5", "5:4", "9:16", "16:9"
]


class ImageGenTool:
    """AI图片生成工具（Gemini 2.5 Flash Image / Nano Banana）
    
    使用Google Gemini 2.5 Flash Image模型生成游戏素材图片。
    复用已有的GOOGLE_API_KEY，与文本生成共用同一个API Key。
    
    主要方法:
    - generate(): 根据文本描述生成图片
    - generate_game_asset(): 根据素材规格生成游戏素材
    - get_generation_stats(): 获取生成统计信息
    """
    
    def __init__(self):
        """初始化图片生成工具"""
        if not Config.GOOGLE_API_KEY:
            logger.error("GOOGLE_API_KEY 未配置，图片生成将不可用")
            self.client = None
        else:
            self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
            logger.info("Gemini 图片生成客户端初始化成功")
        
        # 优先使用 gemini-2.0-flash-exp-image-generation（免费层可用）
        # 备选: gemini-2.5-flash-image（支持更多特性如aspect_ratio）
        self.model = "gemini-2.0-flash-exp-image-generation"
        self._supports_aspect_ratio = False  # 该模型不支持aspect_ratio
        
        # 统计信息
        self._stats = {
            "total_generated": 0,
            "total_failed": 0,
            "project_counts": {}  # project_id -> count
        }
    
    async def generate(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        根据文本描述生成图片
        
        Args:
            prompt: 图片描述（英文效果最佳）
            aspect_ratio: 宽高比，支持 "1:1", "3:4", "4:3", "9:16", "16:9" 等
            save_path: 保存路径（字符串），为None时不保存到磁盘
        
        Returns:
            {
                "success": True/False,
                "path": "本地保存路径（如有）",
                "prompt": "使用的Prompt",
                "text": "模型返回的文本（如有）",
                "error": "错误信息（如有）"
            }
        """
        if self.client is None:
            return {
                "success": False,
                "path": None,
                "prompt": prompt,
                "error": "GOOGLE_API_KEY 未配置"
            }
        
        # 验证宽高比
        if aspect_ratio not in VALID_ASPECT_RATIOS:
            logger.warning(
                f"不支持的宽高比 '{aspect_ratio}'，使用默认 '1:1'"
            )
            aspect_ratio = "1:1"
        
        logger.info(f"生成图片: {prompt[:60]}...")
        
        try:
            # 构建配置（根据模型能力调整）
            if self._supports_aspect_ratio:
                gen_config = types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE'],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                    ),
                )
            else:
                gen_config = types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE'],
                )
            
            # 调用 Gemini Image API（同步API，用线程包装）
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=[prompt],
                config=gen_config,
            )
            
            result = {
                "success": False,
                "path": None,
                "prompt": prompt,
                "text": None,
                "error": None
            }
            
            # 解析响应
            if not response.parts:
                result["error"] = "API返回空响应"
                self._stats["total_failed"] += 1
                return result
            
            for part in response.parts:
                if part.text is not None:
                    result["text"] = part.text
                elif part.inline_data is not None:
                    # 获取图片数据
                    image_data = part.inline_data.data
                    image = Image.open(io.BytesIO(image_data))
                    
                    if save_path:
                        save_path_obj = Path(save_path)
                        save_path_obj.parent.mkdir(
                            parents=True, exist_ok=True
                        )
                        image.save(str(save_path_obj))
                        result["path"] = str(save_path_obj)
                        logger.info(f"图片已保存: {save_path_obj}")
                    
                    result["success"] = True
                    self._stats["total_generated"] += 1
            
            if not result["success"]:
                result["error"] = "响应中未包含图片数据"
                self._stats["total_failed"] += 1
            
            return result
            
        except Exception as e:
            error_msg = f"图片生成失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._stats["total_failed"] += 1
            return {
                "success": False,
                "path": None,
                "prompt": prompt,
                "error": error_msg
            }
    
    async def generate_game_asset(
        self,
        asset_spec: Dict[str, Any],
        project_dir: str
    ) -> Dict[str, Any]:
        """
        根据素材规格生成游戏素材
        
        Args:
            asset_spec: 素材规格
                {
                    "name": "snake_head",
                    "description": "蛇头部，绿色，像素风",
                    "style": "pixel art",
                    "size": "64x64"（可选）
                }
            project_dir: 项目目录路径
        
        Returns:
            {
                "success": True/False,
                "asset_name": "素材名称",
                "path": "保存路径",
                "prompt": "使用的Prompt",
                "error": "错误信息（如有）"
            }
        """
        name = asset_spec.get("name", "unnamed_asset")
        description = asset_spec.get("description", "")
        style = asset_spec.get("style", "pixel art")
        
        # 检查项目图片数量限制
        project_id = Path(project_dir).name
        count = self._stats["project_counts"].get(project_id, 0)
        if count >= MAX_IMAGES_PER_PROJECT:
            return {
                "success": False,
                "asset_name": name,
                "path": None,
                "prompt": None,
                "error": f"项目已达到图片上限({MAX_IMAGES_PER_PROJECT}张)"
            }
        
        # 构建英文Prompt
        prompt = self._build_asset_prompt(
            name=name,
            description=description,
            style=style
        )
        
        # 确定保存路径
        save_path = str(
            Path(project_dir) / "output" / "assets" / f"{name}.png"
        )
        
        # 生成图片
        result = await self.generate(
            prompt=prompt,
            aspect_ratio="1:1",
            save_path=save_path
        )
        
        # 更新项目计数
        if result["success"]:
            self._stats["project_counts"][project_id] = count + 1
        
        return {
            "success": result["success"],
            "asset_name": name,
            "path": result["path"],
            "prompt": prompt,
            "error": result.get("error")
        }
    
    def _build_asset_prompt(
        self,
        name: str,
        description: str,
        style: str
    ) -> str:
        """
        构建游戏素材的英文绘图Prompt
        
        Args:
            name: 素材名称
            description: 素材描述
            style: 美术风格
        
        Returns:
            英文Prompt字符串
        """
        # 基础Prompt模板
        prompt_parts = [
            f"A {style} game asset:",
            f"{description}.",
            "Clean and simple design,",
            "suitable for a 2D game,",
            "transparent or solid color background,",
            "high contrast, clear edges.",
            f"Asset name: {name}."
        ]
        
        return " ".join(prompt_parts)
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        获取图片生成统计信息
        
        Returns:
            {
                "total_generated": 已生成数量,
                "total_failed": 失败数量,
                "project_counts": {项目ID: 数量}
            }
        """
        return dict(self._stats)
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self._stats = {
            "total_generated": 0,
            "total_failed": 0,
            "project_counts": {}
        }
