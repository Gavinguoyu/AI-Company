"""
回归测试运行器
用于快速验证之前阶段的功能未被破坏

使用方法:
    python tests/run_regression.py

特点:
    - 只测试关键功能，不深入测试
    - 单个测试失败不影响其他测试
    - 快速反馈（目标5分钟内完成）
"""

import subprocess
import sys
import io
from pathlib import Path
from typing import List, Tuple
import time

# 设置Windows控制台编码为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 测试列表：(名称, 测试文件, 测试函数名)
TESTS: List[Tuple[str, str, str]] = [
    ("P1-LLM客户端基础", "test_p0_p1_integration.py", "test_llm_client"),
    ("P2-消息总线路由", "test_p2_integration.py", "test_message_routing"),
    ("P3-文件工具读写", "test_p3_tools.py", "test_file_tool"),
    ("P4-工作流初始化", "test_p4_workflow.py", "test_workflow_init"),
    ("P5-API健康检查", "test_p5_web_api.py", "test_health_check"),
    # P6完成后添加:
    # ("P6-WebSocket连接", "test_p6.py", "test_websocket_connection"),
    # P7完成后添加:
    # ("P7-决策机制", "test_p7.py", "test_decision_mechanism"),
    # P8无需添加（P8是完整测试，不是单元测试）
    # P9完成后添加:
    # ("P9-图片生成", "test_p9.py", "test_image_generation"),
]


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """打印测试头部"""
    print()
    print("=" * 70)
    print(f"{Colors.BOLD}🔍 回归测试运行器{Colors.RESET}")
    print("=" * 70)
    print(f"测试数量: {len(TESTS)}")
    print(f"目标时间: 5分钟内")
    print("=" * 70)
    print()


def run_single_test(name: str, test_file: str, test_func: str) -> bool:
    """
    运行单个测试
    
    Args:
        name: 测试名称
        test_file: 测试文件名
        test_func: 测试函数名
    
    Returns:
        True if passed, False otherwise
    """
    test_path = Path(__file__).parent / test_file
    
    # 检查文件是否存在
    if not test_path.exists():
        print(f"{Colors.YELLOW}⚠️  {name}{Colors.RESET} - 测试文件不存在，跳过")
        return True  # 不算失败
    
    try:
        # 运行测试（使用pytest -k 参数只运行特定函数）
        result = subprocess.run(
            [
                sys.executable,
                "-m", "pytest",
                str(test_path),
                "-k", test_func,
                "-v",
                "--tb=short",
                "--timeout=30"  # 单个测试最多30秒
            ],
            capture_output=True,
            text=True,
            timeout=60  # 整个进程最多60秒
        )
        
        # 判断是否通过
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ {name}{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}❌ {name}{Colors.RESET}")
            # 只打印关键错误信息（最后10行）
            error_lines = result.stdout.split('\n')[-10:]
            for line in error_lines:
                if line.strip():
                    print(f"   {Colors.RED}{line}{Colors.RESET}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}❌ {name}{Colors.RESET} - 超时（>60秒）")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ {name}{Colors.RESET} - 异常: {e}")
        return False


def run_all_tests() -> int:
    """
    运行所有回归测试
    
    Returns:
        0 if all passed, 1 otherwise
    """
    print_header()
    
    start_time = time.time()
    results = []
    
    # 依次运行测试
    for name, test_file, test_func in TESTS:
        result = run_single_test(name, test_file, test_func)
        results.append((name, result))
    
    # 计算统计
    elapsed = time.time() - start_time
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    # 打印总结
    print()
    print("=" * 70)
    print(f"{Colors.BOLD}📊 测试结果汇总{Colors.RESET}")
    print("=" * 70)
    
    for name, result in results:
        status = f"{Colors.GREEN}✅{Colors.RESET}" if result else f"{Colors.RED}❌{Colors.RESET}"
        print(f"{status} {name}")
    
    print("=" * 70)
    print(f"通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"总耗时: {elapsed:.1f}秒")
    
    # 判断是否成功
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 所有回归测试通过！{Colors.RESET}")
        print("=" * 70)
        return 0
    else:
        failed = total - passed
        print(f"{Colors.RED}{Colors.BOLD}⚠️ {failed}个测试失败{Colors.RESET}")
        print("=" * 70)
        return 1


def main():
    """主函数"""
    try:
        return run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ 测试被中断{Colors.RESET}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}❌ 发生错误: {e}{Colors.RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
