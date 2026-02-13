"""
P6阶段前端测试
测试前端文件是否存在，结构是否正确
"""

import os
import sys
from pathlib import Path

# 设置Windows控制台编码为UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def test_frontend_structure():
    """测试前端文件结构"""
    print("📋 测试前端文件结构...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    required_files = [
        "index.html",
        "css/style.css",
        "js/websocket.js",
        "js/chat_panel.js",
        "js/status_panel.js",
        "js/file_browser.js",
        "js/office_view.js",
        "js/app.js"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = frontend_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist


def test_html_structure():
    """测试HTML文件内容"""
    print("\n📋 测试HTML结构...")
    
    html_file = Path(__file__).parent / "frontend" / "index.html"
    
    if not html_file.exists():
        print("  ❌ index.html 不存在")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_elements = [
        'id="ws-status"',
        'id="office-view"',
        'id="chat-messages"',
        'id="project-status"',
        'id="file-browser"',
        'type="module"',
        'src="/js/app.js"'
    ]
    
    all_found = True
    for element in required_elements:
        if element in content:
            print(f"  ✅ {element}")
        else:
            print(f"  ❌ {element} 未找到")
            all_found = False
    
    return all_found


def test_js_modules():
    """测试JavaScript模块"""
    print("\n📋 测试JavaScript模块...")
    
    js_dir = Path(__file__).parent / "frontend" / "js"
    
    modules = {
        "websocket.js": ["class WebSocketClient", "export"],
        "chat_panel.js": ["class ChatPanel", "export"],
        "status_panel.js": ["class StatusPanel", "export"],
        "file_browser.js": ["class FileBrowser", "export"],
        "office_view.js": ["class OfficeView", "export"],
        "app.js": ["import", "WebSocketClient", "ChatPanel"]
    }
    
    all_valid = True
    for filename, keywords in modules.items():
        file_path = js_dir / filename
        if not file_path.exists():
            print(f"  ❌ {filename} 不存在")
            all_valid = False
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        module_valid = True
        for keyword in keywords:
            if keyword not in content:
                print(f"  ❌ {filename}: 缺少 '{keyword}'")
                module_valid = False
                all_valid = False
        
        if module_valid:
            print(f"  ✅ {filename}")
    
    return all_valid


def test_css_file():
    """测试CSS文件"""
    print("\n📋 测试CSS样式...")
    
    css_file = Path(__file__).parent / "frontend" / "css" / "style.css"
    
    if not css_file.exists():
        print("  ❌ style.css 不存在")
        return False
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_classes = [
        ".app-container",
        ".app-header",
        ".office-view",
        ".chat-panel",
        ".status-panel",
        ".file-browser",
        ".agent-card",
        ".chat-message"
    ]
    
    all_found = True
    for css_class in required_classes:
        if css_class in content:
            print(f"  ✅ {css_class}")
        else:
            print(f"  ❌ {css_class} 未找到")
            all_found = False
    
    return all_found


def main():
    """运行所有测试"""
    print("="*60)
    print("🧪 P6阶段前端测试")
    print("="*60)
    
    results = []
    
    # 测试1: 文件结构
    results.append(("文件结构", test_frontend_structure()))
    
    # 测试2: HTML结构
    results.append(("HTML结构", test_html_structure()))
    
    # 测试3: JavaScript模块
    results.append(("JavaScript模块", test_js_modules()))
    
    # 测试4: CSS样式
    results.append(("CSS样式", test_css_file()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print("="*60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
