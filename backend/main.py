"""
文件: backend/main.py
职责: FastAPI 应用入口，启动 Web 服务器
依赖: fastapi, uvicorn, config.py
"""

import sys
from pathlib import Path

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from config import Config
from utils.logger import setup_logger
from api.http_routes import router as http_router
from api.websocket_handler import router as ws_router


# 创建日志器
logger = setup_logger("main", log_level=Config.LOG_LEVEL, log_to_file=Config.LOG_TO_FILE)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("="*60)
    logger.info("AI 游戏开发公司 启动中...")
    logger.info("="*60)
    
    # 验证配置
    if not Config.validate():
        logger.error("配置验证失败，请检查 .env 文件")
        sys.exit(1)
    
    # 打印配置信息
    Config.print_config()
    
    logger.info("✅ 应用启动成功")
    logger.info(f"📡 API 文档: http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/api/docs")
    logger.info(f"🌐 前端界面: http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/")
    logger.info("="*60)
    
    yield  # 应用运行中
    
    # 关闭时执行
    logger.info("="*60)
    logger.info("AI 游戏开发公司 正在关闭...")
    logger.info("="*60)


def create_app() -> FastAPI:
    """
    创建并配置 FastAPI 应用
    
    Returns:
        配置好的 FastAPI 应用实例
    """
    app = FastAPI(
        title="AI 游戏开发公司",
        description="一个模拟真实游戏公司的 AI 多智能体协作平台",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan
    )
    
    # 配置 CORS（允许前端跨域访问）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该设置具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(http_router, prefix="/api")
    app.include_router(ws_router)
    
    # 挂载项目输出目录（用于Play按钮访问游戏文件）
    projects_dir = Config.PROJECTS_DIR
    if projects_dir.exists():
        app.mount("/projects", StaticFiles(directory=str(projects_dir), html=True), name="projects")
        logger.info(f"项目文件已挂载: {projects_dir}")
    else:
        logger.warning(f"项目目录不存在: {projects_dir}")
    
    # 挂载静态文件（前端）- 必须在projects之后，因为"/"是catch-all
    frontend_dir = Config.FRONTEND_DIR
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
        logger.info(f"前端静态文件已挂载: {frontend_dir}")
    else:
        logger.warning(f"前端目录不存在: {frontend_dir}")
    
    return app


# 创建应用实例
app = create_app()


def main():
    """主函数：启动服务器"""
    try:
        # 使用 uvicorn 运行服务器
        uvicorn.run(
            "main:app",
            host=Config.SERVER_HOST,
            port=Config.SERVER_PORT,
            reload=Config.DEBUG_MODE,  # 开发模式下启用热重载
            log_level=Config.LOG_LEVEL.lower()
        )
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
