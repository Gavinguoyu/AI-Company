"""
文件: engine/context_cache.py
职责: Gemini Context Caching管理 - 缓存常用文档减少Token消耗
依赖: google-genai, config.py
被依赖: engine/llm_client.py, workflows/game_dev_workflow.py

P11新增功能:
- 缓存GDD/TDD等长文档，避免每次请求重复发送
- 支持缓存过期和自动刷新
- 统计缓存命中率
"""

import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import hashlib

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from config import Config
from utils.logger import setup_logger

# 尝试导入新版 google-genai SDK
try:
    from google import genai
    from google.genai import types
    NEW_SDK_AVAILABLE = True
except ImportError:
    NEW_SDK_AVAILABLE = False
    print("警告: google-genai 未安装，Context Caching功能将不可用")


class ContextCacheManager:
    """
    Gemini Context Caching 管理器
    
    用于缓存常用的大文本内容（如GDD、TDD、项目规范等），
    减少每次API调用的Token消耗。
    
    使用示例:
        cache_manager = ContextCacheManager()
        
        # 缓存GDD文档
        cache_key = await cache_manager.cache_content(
            content=gdd_content,
            display_name="gdd_snake_game"
        )
        
        # 后续请求使用缓存
        response = await cache_manager.generate_with_cache(
            cache_name=cache_key,
            new_prompt="根据GDD编写游戏代码"
        )
    """
    
    def __init__(self):
        """初始化缓存管理器"""
        self.logger = setup_logger("context_cache")
        self.api_key = Config.GOOGLE_API_KEY
        
        # 缓存存储: {cache_key: {name, content_hash, created_at, ttl}}
        self._caches: Dict[str, Dict[str, Any]] = {}
        
        # 统计信息
        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_creates": 0,
            "tokens_saved": 0
        }
        
        # 初始化客户端
        self._client = None
        if NEW_SDK_AVAILABLE and self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
                self.logger.info("Context Caching 客户端初始化成功")
            except Exception as e:
                self.logger.error(f"Context Caching 客户端初始化失败: {e}")
        
        # 默认缓存TTL（秒）- Gemini缓存最长1小时
        self.default_ttl = 3600  # 1小时
        
        # 最小缓存内容大小（字符数）- 小于此值不缓存
        self.min_cache_size = 500
        
    def _get_content_hash(self, content: str) -> str:
        """计算内容哈希，用于检测内容是否变化"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _estimate_tokens(self, text: str) -> int:
        """估算文本的Token数量（简单估算：1 token ≈ 4 字符）"""
        return len(text) // 4
    
    async def cache_content(
        self,
        content: str,
        display_name: str,
        ttl_seconds: int = None
    ) -> Optional[str]:
        """
        缓存内容到Gemini Context Cache
        
        Args:
            content: 要缓存的内容
            display_name: 缓存显示名称（用于标识）
            ttl_seconds: 缓存过期时间（秒），默认1小时
            
        Returns:
            缓存名称（用于后续请求），如果失败返回None
        """
        if not NEW_SDK_AVAILABLE or not self._client:
            self.logger.warning("Context Caching不可用，跳过缓存")
            return None
        
        # 检查内容大小
        if len(content) < self.min_cache_size:
            self.logger.debug(f"内容太小({len(content)}字符)，跳过缓存")
            return None
        
        ttl = ttl_seconds or self.default_ttl
        
        try:
            # 检查是否已有相同内容的缓存
            content_hash = self._get_content_hash(content)
            cache_key = f"{display_name}_{content_hash}"
            
            if cache_key in self._caches:
                cached = self._caches[cache_key]
                # 检查缓存是否过期
                if datetime.now() < cached["expires_at"]:
                    self.logger.info(f"缓存命中: {display_name}")
                    self._stats["cache_hits"] += 1
                    self._stats["tokens_saved"] += self._estimate_tokens(content)
                    return cached["name"]
            
            self.logger.info(f"创建新缓存: {display_name} ({len(content)}字符)")
            
            # 在线程池中执行同步API调用
            loop = asyncio.get_event_loop()
            
            # 创建缓存内容
            cache_content = types.Content(
                role="user",
                parts=[types.Part(text=content)]
            )
            
            # 创建缓存
            cached_content = await loop.run_in_executor(
                None,
                lambda: self._client.caches.create(
                    model="gemini-2.0-flash",
                    config=types.CreateCachedContentConfig(
                        display_name=display_name,
                        contents=[cache_content],
                        ttl=f"{ttl}s"
                    )
                )
            )
            
            # 记录缓存信息
            self._caches[cache_key] = {
                "name": cached_content.name,
                "display_name": display_name,
                "content_hash": content_hash,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=ttl),
                "token_count": self._estimate_tokens(content)
            }
            
            self._stats["cache_creates"] += 1
            self.logger.info(f"缓存创建成功: {cached_content.name}")
            
            return cached_content.name
            
        except Exception as e:
            self.logger.error(f"创建缓存失败: {e}", exc_info=True)
            return None
    
    async def generate_with_cache(
        self,
        cache_name: str,
        new_prompt: str,
        system_instruction: str = None
    ) -> Optional[str]:
        """
        使用缓存生成响应
        
        Args:
            cache_name: 缓存名称
            new_prompt: 新的提示词
            system_instruction: 系统指令（可选）
            
        Returns:
            生成的响应文本，如果失败返回None
        """
        if not NEW_SDK_AVAILABLE or not self._client or not cache_name:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            
            # 构建请求内容
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=new_prompt)]
                )
            ]
            
            # 构建生成配置
            config = types.GenerateContentConfig(
                cached_content=cache_name,
                temperature=0.7,
                max_output_tokens=8192
            )
            
            if system_instruction:
                config.system_instruction = system_instruction
            
            # 生成响应
            response = await loop.run_in_executor(
                None,
                lambda: self._client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=config
                )
            )
            
            self._stats["cache_hits"] += 1
            return response.text
            
        except Exception as e:
            self.logger.error(f"使用缓存生成失败: {e}", exc_info=True)
            self._stats["cache_misses"] += 1
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            **self._stats,
            "active_caches": len(self._caches),
            "hit_rate": (
                self._stats["cache_hits"] / 
                (self._stats["cache_hits"] + self._stats["cache_misses"])
                if (self._stats["cache_hits"] + self._stats["cache_misses"]) > 0
                else 0
            )
        }
    
    async def cleanup_expired(self) -> int:
        """清理过期的缓存记录"""
        now = datetime.now()
        expired_keys = [
            k for k, v in self._caches.items()
            if v["expires_at"] < now
        ]
        
        for key in expired_keys:
            del self._caches[key]
            self.logger.debug(f"清理过期缓存: {key}")
        
        return len(expired_keys)
    
    def clear_all(self):
        """清除所有缓存记录"""
        self._caches.clear()
        self.logger.info("所有缓存已清除")


# 全局单例
_cache_manager: Optional[ContextCacheManager] = None


def get_cache_manager() -> ContextCacheManager:
    """获取全局缓存管理器单例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = ContextCacheManager()
    return _cache_manager


# 测试代码
if __name__ == "__main__":
    async def test_cache():
        print("\n" + "="*60)
        print("测试 Context Caching")
        print("="*60 + "\n")
        
        cache = get_cache_manager()
        
        # 测试缓存内容
        test_content = "这是一个测试内容。" * 100  # 600+字符
        
        cache_name = await cache.cache_content(
            content=test_content,
            display_name="test_cache"
        )
        
        if cache_name:
            print(f"✅ 缓存创建成功: {cache_name}")
            
            # 测试统计
            stats = cache.get_stats()
            print(f"缓存统计: {stats}")
        else:
            print("⚠️ 缓存不可用（可能需要安装 google-genai）")
        
        print("\n" + "="*60)
    
    asyncio.run(test_cache())
