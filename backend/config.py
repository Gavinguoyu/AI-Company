"""
文件: backend/config.py
职责: 后端配置管理，从环境变量读取配置
依赖: python-dotenv
被依赖: 所有后端模块
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """应用配置类"""
    
    # =====================================================
    # API Keys
    # =====================================================
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    # =====================================================
    # 服务器配置
    # =====================================================
    SERVER_HOST: str = os.getenv("SERVER_HOST", "localhost")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    
    # =====================================================
    # 模型配置
    # =====================================================
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
    ENABLE_CONTEXT_CACHE: bool = os.getenv("ENABLE_CONTEXT_CACHE", "true").lower() == "true"
    MAX_PROJECT_TOKENS: int = int(os.getenv("MAX_PROJECT_TOKENS", "500000"))
    
    # =====================================================
    # 调试配置
    # =====================================================
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # =====================================================
    # 日志配置
    # =====================================================
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    
    # =====================================================
    # LLM 重试配置
    # =====================================================
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
    LLM_RETRY_BASE_DELAY: float = float(os.getenv("LLM_RETRY_BASE_DELAY", "2.0"))
    LLM_RETRY_MAX_DELAY: float = float(os.getenv("LLM_RETRY_MAX_DELAY", "30.0"))
    
    # =====================================================
    # 路径配置
    # =====================================================
    ROOT_DIR: Path = Path(__file__).parent.parent
    BACKEND_DIR: Path = ROOT_DIR / "backend"
    FRONTEND_DIR: Path = ROOT_DIR / "frontend"
    PROJECTS_DIR: Path = ROOT_DIR / "projects"
    DOCS_DIR: Path = ROOT_DIR / "docs"
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        if not cls.GOOGLE_API_KEY:
            print("❌ 错误: 未设置 GOOGLE_API_KEY")
            print("请编辑 .env 文件并填入你的 Google Gemini API Key")
            return False
        
        print("✅ 配置验证通过")
        return True
    
    @classmethod
    def print_config(cls):
        """打印当前配置（隐藏敏感信息）"""
        print("\n" + "="*50)
        print("当前配置")
        print("="*50)
        print(f"服务器地址: {cls.SERVER_HOST}:{cls.SERVER_PORT}")
        print(f"主力模型: {cls.DEFAULT_MODEL}")
        print(f"上下文缓存: {'启用' if cls.ENABLE_CONTEXT_CACHE else '禁用'}")
        print(f"Token 预算: {cls.MAX_PROJECT_TOKENS:,}")
        print(f"调试模式: {'启用' if cls.DEBUG_MODE else '禁用'}")
        
        api_key_masked = cls.GOOGLE_API_KEY[:8] + "..." if cls.GOOGLE_API_KEY else "未设置"
        print(f"Google API Key: {api_key_masked}")
        print("="*50 + "\n")


# 导出配置实例
config = Config()
