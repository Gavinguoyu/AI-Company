"""
文件: engine/llm_client.py
职责: 封装LLM API调用，主力使用Gemini 3 Pro，兼容多模型切换
依赖: google.generativeai, config.py
被依赖: engine/agent.py

P11新增功能:
- 集成Context Caching，支持缓存长文档减少Token消耗
- 添加响应长度限制配置
"""

import os
import sys
from typing import List, Dict, Any, Optional
import asyncio
from pathlib import Path

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

try:
    import google.generativeai as genai
except ImportError:
    print("警告: google.generativeai 未安装，请运行: pip install google-generativeai")
    raise

from config import Config
from utils.logger import setup_logger
from utils.retry import async_retry

# P11: 导入缓存管理器
try:
    from engine.context_cache import get_cache_manager, ContextCacheManager
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False


class LLMClient:
    """
    LLM API 客户端
    负责与 Google Gemini API 通信
    
    P11新增:
    - 支持Context Caching减少Token消耗
    - 支持响应长度限制
    """
    
    def __init__(self, model_name: Optional[str] = None, enable_cache: bool = True):
        """
        初始化 LLM 客户端
        
        Args:
            model_name: 模型名称，默认使用配置文件中的模型
            enable_cache: 是否启用缓存（P11新增）
        """
        self.model_name = model_name or Config.DEFAULT_MODEL
        self.api_key = Config.GOOGLE_API_KEY
        self.enable_cache = enable_cache and CACHE_AVAILABLE
        
        if not self.api_key:
            raise ValueError("未设置 GOOGLE_API_KEY，请检查 .env 文件")
        
        # 配置 Gemini API
        genai.configure(api_key=self.api_key)
        
        # 创建生成配置
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # 创建模型实例
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config
        )
        
        # 创建日志器
        self.logger = setup_logger(
            f"llm_client.{self.model_name}",
            log_level=Config.LOG_LEVEL,
            log_to_file=Config.LOG_TO_FILE
        )
        
        # P11: 初始化缓存管理器
        self._cache_manager: Optional[ContextCacheManager] = None
        if self.enable_cache:
            try:
                self._cache_manager = get_cache_manager()
                self.logger.info("Context Caching 已启用")
            except Exception as e:
                self.logger.warning(f"Context Caching 初始化失败: {e}")
                self.enable_cache = False
        
        # P11: 缓存已加载的文档（用于多轮对话）
        self._cached_documents: Dict[str, str] = {}
        
        self.logger.info(f"LLM客户端初始化成功: {self.model_name}")
    
    @async_retry(
        max_attempts=Config.LLM_MAX_RETRIES,
        base_delay=Config.LLM_RETRY_BASE_DELAY,
        max_delay=Config.LLM_RETRY_MAX_DELAY,
        exceptions=(Exception,)
    )
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        生成 LLM 响应（异步，带重试机制）
        
        失败时会自动重试，重试策略：
        - 第1次失败：等待 2 秒后重试
        - 第2次失败：等待 4 秒后重试
        - 第3次失败：抛出异常
        
        Args:
            messages: 对话历史，格式为 [{"role": "user/model", "content": "..."}]
            system_prompt: 系统提示词（Agent 的角色定义）
        
        Returns:
            LLM 生成的响应文本
        """
        try:
            # 构建完整的提示
            prompt_parts = []
            
            # 添加系统提示词
            if system_prompt:
                prompt_parts.append(f"## 系统角色定义\n{system_prompt}\n")
            
            # 添加对话历史
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "user":
                    prompt_parts.append(f"**用户**: {content}")
                elif role == "model" or role == "assistant":
                    prompt_parts.append(f"**助手**: {content}")
            
            # 合并为完整提示
            full_prompt = "\n\n".join(prompt_parts)
            
            self.logger.debug(f"调用 LLM: {self.model_name}")
            self.logger.debug(f"提示词长度: {len(full_prompt)} 字符")
            
            # 在新线程中调用同步API（因为 Gemini SDK 不支持原生异步）
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(full_prompt)
            )
            
            # 提取响应文本
            response_text = response.text
            
            self.logger.info("LLM 响应完成")
            self.logger.debug(f"响应长度: {len(response_text)} 字符")
            
            return response_text
            
        except Exception as e:
            error_msg = f"LLM API 调用失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)
    
    def count_tokens(self, text: str) -> int:
        """
        估算文本的 token 数量
        
        Args:
            text: 要计算的文本
        
        Returns:
            估算的 token 数量
        """
        try:
            # 使用 Gemini 的 token 计数功能
            result = self.model.count_tokens(text)
            return result.total_tokens
        except Exception as e:
            # 如果失败，使用简单估算：1 token ≈ 4 字符
            return len(text) // 4
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取当前模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model_name": self.model_name,
            "api_key_configured": bool(self.api_key),
            "generation_config": self.generation_config,
            "cache_enabled": self.enable_cache
        }
    
    # ==================== P11新增方法 ====================
    
    def cache_document(self, doc_name: str, content: str) -> bool:
        """
        缓存文档内容（用于后续请求复用）
        
        Args:
            doc_name: 文档名称（如 "gdd", "tdd"）
            content: 文档内容
            
        Returns:
            是否成功缓存
        """
        if not self.enable_cache:
            return False
        
        self._cached_documents[doc_name] = content
        self.logger.debug(f"文档已缓存: {doc_name} ({len(content)}字符)")
        return True
    
    def clear_cached_documents(self):
        """清除已缓存的文档"""
        self._cached_documents.clear()
        self.logger.debug("已清除所有缓存的文档")
    
    def get_cached_documents_summary(self) -> Dict[str, int]:
        """获取已缓存文档的摘要（名称 -> 字符数）"""
        return {name: len(content) for name, content in self._cached_documents.items()}
    
    async def generate_response_with_cached_context(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_response_tokens: int = None
    ) -> str:
        """
        使用缓存的上下文生成响应（P11优化版）
        
        这个方法会：
        1. 将缓存的文档作为上下文
        2. 只发送用户消息和必要的系统提示
        3. 大幅减少重复发送的Token
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            max_response_tokens: 最大响应Token数（可选）
            
        Returns:
            LLM生成的响应文本
        """
        try:
            # 构建提示
            prompt_parts = []
            
            # 添加缓存的文档（如果有）
            if self._cached_documents:
                doc_context = "## 参考文档\n\n"
                for doc_name, content in self._cached_documents.items():
                    # 限制每个文档的大小，避免过大
                    max_doc_size = 5000  # 字符
                    truncated = content[:max_doc_size]
                    if len(content) > max_doc_size:
                        truncated += f"\n... (已截断，原文档{len(content)}字符)"
                    doc_context += f"### {doc_name}\n{truncated}\n\n"
                prompt_parts.append(doc_context)
            
            # 添加系统提示词
            if system_prompt:
                prompt_parts.append(f"## 系统角色定义\n{system_prompt}\n")
            
            # 添加用户消息
            prompt_parts.append(f"**用户**: {user_message}")
            
            # 合并提示
            full_prompt = "\n\n".join(prompt_parts)
            
            # 检查是否使用缓存API
            if self.enable_cache and self._cache_manager and len(self._cached_documents) > 0:
                # 尝试使用缓存
                combined_docs = "\n\n".join(
                    f"### {name}\n{content[:3000]}"
                    for name, content in self._cached_documents.items()
                )
                
                cache_name = await self._cache_manager.cache_content(
                    content=combined_docs,
                    display_name=f"docs_{hash(combined_docs) % 10000}"
                )
                
                if cache_name:
                    # 使用缓存生成
                    response = await self._cache_manager.generate_with_cache(
                        cache_name=cache_name,
                        new_prompt=user_message,
                        system_instruction=system_prompt
                    )
                    if response:
                        self.logger.info("✅ 使用缓存生成响应成功")
                        return response
            
            # 回退到普通生成
            self.logger.debug(f"调用 LLM: {self.model_name}")
            self.logger.debug(f"提示词长度: {len(full_prompt)} 字符")
            
            # 配置生成参数
            gen_config = self.generation_config.copy()
            if max_response_tokens:
                gen_config["max_output_tokens"] = max_response_tokens
            
            # 在线程池中调用同步API
            loop = asyncio.get_event_loop()
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=gen_config
            )
            
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(full_prompt)
            )
            
            response_text = response.text
            
            self.logger.info("LLM 响应完成")
            self.logger.debug(f"响应长度: {len(response_text)} 字符")
            
            return response_text
            
        except Exception as e:
            error_msg = f"LLM API 调用失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if self.enable_cache and self._cache_manager:
            return self._cache_manager.get_stats()
        return {"cache_enabled": False}


# 测试代码
if __name__ == "__main__":
    async def test_llm_client():
        """测试 LLM 客户端"""
        print("\n" + "="*60)
        print("测试 LLM 客户端")
        print("="*60 + "\n")
        
        try:
            # 创建客户端
            client = LLMClient()
            
            # 打印模型信息
            info = client.get_model_info()
            print(f"模型名称: {info['model_name']}")
            print(f"API Key 已配置: {info['api_key_configured']}")
            print(f"生成配置: {info['generation_config']}\n")
            
            # 测试简单对话
            messages = [
                {"role": "user", "content": "你好！请用一句话介绍你自己。"}
            ]
            
            system_prompt = "你是一个友好的AI助手。"
            
            print("发送测试消息...")
            response = await client.generate_response(messages, system_prompt)
            
            print("\n" + "="*60)
            print("收到响应:")
            print("="*60)
            print(response)
            print("="*60 + "\n")
            
            # 测试 token 计数
            token_count = client.count_tokens(response)
            print(f"响应的 Token 数量: {token_count}\n")
            
            print("✅ LLM 客户端测试通过！")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 运行测试
    asyncio.run(test_llm_client())
