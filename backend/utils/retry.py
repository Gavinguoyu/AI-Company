"""
文件: utils/retry.py
职责: 重试机制工具，支持指数退避策略
依赖: asyncio（Python标准库）
被依赖: llm_client.py 等需要重试的模块
"""

import os
import sys
import asyncio
import functools
from typing import Callable, Type, Tuple
import logging

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

# 使用标准 logger
logger = logging.getLogger(__name__)


def async_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    异步函数重试装饰器（指数退避策略）
    
    当被装饰的函数抛出指定异常时，会自动重试，每次重试的延迟时间呈指数增长。
    
    Args:
        max_attempts: 最大尝试次数（包括首次调用），默认 3 次
        base_delay: 基础延迟时间（秒），默认 1.0 秒
        max_delay: 最大延迟时间（秒），默认 60.0 秒
        exponential_base: 指数基数，默认 2.0
        exceptions: 需要重试的异常类型元组，默认捕获所有异常
    
    重试延迟计算公式:
        delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
    
    示例:
        如果 base_delay=2.0, exponential_base=2.0:
        - 第1次失败: 等待 2.0 秒后重试
        - 第2次失败: 等待 4.0 秒后重试
        - 第3次失败: 等待 8.0 秒后重试
    
    使用示例:
        @async_retry(max_attempts=3, base_delay=2.0)
        async def call_api():
            # 可能失败的 API 调用
            response = await some_api_call()
            return response
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    # 尝试执行函数
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    # 如果已经是最后一次尝试，直接抛出异常
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} 失败，已达最大重试次数 {max_attempts}，"
                            f"最后的错误: {str(e)}"
                        )
                        raise
                    
                    # 计算延迟时间（指数退避）
                    delay = min(
                        base_delay * (exponential_base ** (attempt - 1)),
                        max_delay
                    )
                    
                    # 记录警告日志
                    logger.warning(
                        f"{func.__name__} 第 {attempt} 次尝试失败: {str(e)}, "
                        f"将在 {delay:.1f} 秒后进行第 {attempt + 1} 次重试..."
                    )
                    
                    # 等待后重试
                    await asyncio.sleep(delay)
            
            # 理论上不应该执行到这里
            raise last_exception
        
        return wrapper
    return decorator


# 测试代码
if __name__ == "__main__":
    print("\n" + "="*60)
    print("测试重试机制")
    print("="*60 + "\n")
    
    # 配置日志（便于观察重试过程）
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # 测试 1: 模拟前2次失败，第3次成功
    print("\n测试 1: 前2次失败，第3次成功")
    print("-" * 60)
    
    call_count = 0
    
    @async_retry(max_attempts=3, base_delay=1.0)
    async def test_retry_success():
        global call_count
        call_count += 1
        print(f"  → 第 {call_count} 次调用")
        
        if call_count < 3:
            raise Exception("模拟失败")
        
        return "成功！"
    
    async def run_test1():
        global call_count
        call_count = 0
        result = await test_retry_success()
        print(f"\n✅ 最终结果: {result}")
        print(f"   总共调用了 {call_count} 次\n")
    
    asyncio.run(run_test1())
    
    # 测试 2: 全部失败（达到最大重试次数）
    print("\n测试 2: 全部失败（达到最大重试次数）")
    print("-" * 60)
    
    fail_count = 0
    
    @async_retry(max_attempts=3, base_delay=0.5)
    async def test_retry_fail():
        global fail_count
        fail_count += 1
        print(f"  → 第 {fail_count} 次调用")
        raise Exception("持续失败")
    
    async def run_test2():
        global fail_count
        fail_count = 0
        try:
            await test_retry_fail()
        except Exception as e:
            print(f"\n❌ 最终失败: {str(e)}")
            print(f"   总共调用了 {fail_count} 次\n")
    
    asyncio.run(run_test2())
    
    # 测试 3: 测试指数退避延迟
    print("\n测试 3: 验证指数退避延迟")
    print("-" * 60)
    
    import time
    
    @async_retry(max_attempts=4, base_delay=1.0, exponential_base=2.0)
    async def test_delay():
        raise Exception("测试延迟")
    
    async def run_test3():
        start_time = time.time()
        try:
            await test_delay()
        except:
            pass
        total_time = time.time() - start_time
        
        # 理论延迟: 1s + 2s + 4s = 7s（加上执行时间约7-8秒）
        print(f"\n   总耗时: {total_time:.1f} 秒")
        print(f"   预期延迟: 1s + 2s + 4s = 7s（加上执行时间）")
        print(f"   延迟策略验证: {'✅ 正确' if 7 <= total_time <= 10 else '❌ 异常'}\n")
    
    asyncio.run(run_test3())
    
    # 测试 4: 自定义配置
    print("\n测试 4: 自定义配置（最多5次，基础延迟0.5秒）")
    print("-" * 60)
    
    custom_count = 0
    
    @async_retry(max_attempts=5, base_delay=0.5, max_delay=10.0)
    async def test_custom():
        global custom_count
        custom_count += 1
        if custom_count < 4:
            raise Exception("继续失败")
        return "第4次成功"
    
    async def run_test4():
        global custom_count
        custom_count = 0
        result = await test_custom()
        print(f"\n✅ 最终结果: {result}")
        print(f"   总共调用了 {custom_count} 次\n")
    
    asyncio.run(run_test4())
    
    print("="*60)
    print("✅ 重试机制测试完成！")
    print("="*60 + "\n")
