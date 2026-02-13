"""
文件: utils/logger.py
职责: 统一的日志系统，支持控制台输出和文件输出
依赖: logging（Python标准库）
被依赖: 所有需要日志的模块
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

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


def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: Path = None
):
    """
    设置日志器
    
    Args:
        name: 日志器名称（通常是模块名，如 "llm_client.gemini-2.0-flash"）
        log_level: 日志级别（DEBUG/INFO/WARNING/ERROR）
        log_to_file: 是否输出到文件
        log_dir: 日志文件目录，默认为项目根目录的 logs/
    
    Returns:
        配置好的 logger 实例
    
    使用示例:
        from utils.logger import setup_logger
        
        logger = setup_logger("my_module", log_level="INFO")
        logger.info("这是一条信息")
        logger.warning("这是一条警告")
        logger.error("这是一条错误", exc_info=True)
    """
    # 获取或创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除已有的处理器（避免重复添加）
    logger.handlers.clear()
    
    # 定义日志格式
    # 格式：时间 | 模块名 | 级别 | 消息
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 1. 控制台处理器（始终启用）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 2. 文件处理器（可选）
    if log_to_file:
        # 确定日志目录
        if log_dir is None:
            # 默认：项目根目录的 logs/
            log_dir = Path(__file__).parent.parent.parent / "logs"
        
        # 创建日志目录
        log_dir.mkdir(exist_ok=True)
        
        # 日志文件名：模块名_日期.log
        # 例如：llm_client.gemini-2.0-flash_20260211.log
        safe_name = name.replace("/", "_").replace("\\", "_")  # 替换路径分隔符
        log_file = log_dir / f"{safe_name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 测试代码
if __name__ == "__main__":
    print("\n" + "="*60)
    print("测试日志系统")
    print("="*60 + "\n")
    
    # 创建测试 logger
    logger = setup_logger(
        "test_logger",
        log_level="DEBUG",
        log_to_file=True
    )
    
    print("\n1. 测试不同日志级别:")
    print("-" * 60)
    logger.debug("这是一条 DEBUG 级别的消息（详细调试信息）")
    logger.info("这是一条 INFO 级别的消息（一般信息）")
    logger.warning("这是一条 WARNING 级别的消息（警告信息）")
    logger.error("这是一条 ERROR 级别的消息（错误信息）")
    
    print("\n2. 测试带异常信息的日志:")
    print("-" * 60)
    try:
        # 故意触发一个异常
        result = 1 / 0
    except Exception as e:
        logger.error("捕获到异常", exc_info=True)  # exc_info=True 会记录完整堆栈
    
    print("\n3. 测试不同模块的 logger:")
    print("-" * 60)
    logger_llm = setup_logger("llm_client.gemini-2.0-flash", log_level="INFO")
    logger_agent = setup_logger("agent.test_planner", log_level="INFO")
    
    logger_llm.info("LLM 客户端初始化成功")
    logger_agent.info("Agent 开始工作")
    
    print("\n4. 检查日志文件:")
    print("-" * 60)
    log_dir = Path(__file__).parent.parent.parent / "logs"
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        print(f"日志目录: {log_dir}")
        print(f"日志文件数量: {len(log_files)}")
        for log_file in log_files:
            print(f"  - {log_file.name}")
    else:
        print("日志目录不存在")
    
    print("\n" + "="*60)
    print("✅ 日志系统测试完成！")
    print("="*60 + "\n")
