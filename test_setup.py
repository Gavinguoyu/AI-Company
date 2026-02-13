"""
环境测试脚本
运行此脚本验证环境配置是否正确
"""

import sys
import os
from pathlib import Path

# 设置控制台编码为 UTF-8（Windows 兼容）
if sys.platform == "win32":
    try:
        os.system("chcp 65001 > nul 2>&1")
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_python_version():
    """测试 Python 版本"""
    print("=" * 60)
    print("1. 测试 Python 版本")
    print("=" * 60)
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version >= (3, 11):
        print("✅ Python 版本符合要求（需要 3.11+）")
        return True
    else:
        print("❌ Python 版本过低，需要 3.11 或更高版本")
        return False

def test_imports():
    """测试必要的包是否可以导入"""
    print("\n" + "=" * 60)
    print("2. 测试依赖包")
    print("=" * 60)
    
    packages = [
        ("fastapi", "FastAPI Web 框架"),
        ("uvicorn", "ASGI 服务器"),
        ("websockets", "WebSocket 支持"),
        ("google.generativeai", "Google Gemini API"),
        ("openai", "OpenAI API"),
        ("litellm", "多模型支持"),
        ("pydantic", "数据验证"),
        ("dotenv", "环境变量管理"),
        ("yaml", "YAML 配置文件支持"),
        ("aiofiles", "异步文件操作"),
        ("httpx", "异步 HTTP 客户端"),
        ("PIL", "图像处理"),
    ]
    
    all_ok = True
    for package, description in packages:
        try:
            __import__(package)
            print(f"✅ {package:25s} - {description}")
        except ImportError:
            print(f"❌ {package:25s} - 导入失败")
            all_ok = False
    
    return all_ok

def test_config():
    """测试配置文件"""
    print("\n" + "=" * 60)
    print("3. 测试配置")
    print("=" * 60)
    
    try:
        from config import Config
        
        # 打印配置
        Config.print_config()
        
        # 验证配置
        if Config.validate():
            print("✅ 配置验证通过")
            return True
        else:
            print("❌ 配置验证失败")
            return False
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_directories():
    """测试目录结构"""
    print("\n" + "=" * 60)
    print("4. 测试目录结构")
    print("=" * 60)
    
    root = Path(__file__).parent
    required_dirs = [
        "backend",
        "backend/engine",
        "backend/agents",
        "backend/tools",
        "backend/workflows",
        "backend/api",
        "frontend",
        "frontend/css",
        "frontend/js",
        "frontend/assets",
        "projects",
        "docs",
        ".cursor/rules",
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        full_path = root / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - 不存在")
            all_ok = False
    
    return all_ok

def main():
    """主测试函数"""
    print("\n")
    print("*" * 60)
    print("    AI 游戏开发公司 - 环境测试")
    print("*" * 60)
    print("\n")
    
    results = []
    
    # 运行所有测试
    results.append(("Python 版本", test_python_version()))
    results.append(("依赖包", test_imports()))
    results.append(("配置文件", test_config()))
    results.append(("目录结构", test_directories()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:15s}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！环境配置完成！")
        print("\n下一步：开始 P1 阶段（Agent 引擎核心）")
    else:
        print("⚠️  部分测试失败，请检查上述错误信息")
    print("=" * 60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
