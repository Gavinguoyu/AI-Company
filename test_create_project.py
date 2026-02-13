"""
测试创建项目API
"""
import requests
import json
import sys
import io

# 设置Windows控制台编码为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_create_project():
    """测试创建项目"""
    url = "http://localhost:8000/api/project/start"
    
    payload = {
        "project_name": "test_snake",
        "game_idea": "制作一个经典的贪吃蛇游戏"
    }
    
    print(f"🚀 发送请求到: {url}")
    print(f"📦 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"\n📡 响应状态码: {response.status_code}")
        print(f"📦 响应数据:")
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"\n✅ 测试成功！项目ID: {data.get('project_id')}")
                return True
            else:
                print(f"\n❌ 测试失败: {data.get('message')}")
                return False
        else:
            print(f"\n❌ API返回错误状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("测试创建项目API")
    print("="*60)
    
    success = test_create_project()
    
    print("\n" + "="*60)
    if success:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 测试失败，请检查错误信息")
    print("="*60)
