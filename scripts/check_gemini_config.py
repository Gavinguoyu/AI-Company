"""
验证Gemini API配置是否正确

运行此脚本检查:
1. API Key是否已设置
2. 模型名称是否正确
3. 能否成功调用API
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_configuration():
    """检查配置"""
    print("=" * 60)
    print("Gemini API 配置检查")
    print("=" * 60)
    
    # 1. 检查API Key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置")
        print("\n请在项目根目录创建 .env 文件，并添加:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    else:
        print(f"✓ GEMINI_API_KEY 已设置 (长度: {len(api_key)})")
    
    # 2. 检查模型名称
    model_name = os.getenv('DEFAULT_MODEL', 'gemini-1.5-flash')
    print(f"✓ 模型名称: {model_name}")
    
    # 3. 尝试调用API
    print("\n正在测试API调用...")
    try:
        import google.generativeai as genai
        
        # 配置API Key
        genai.configure(api_key=api_key)
        
        # 创建模型
        model = genai.GenerativeModel(model_name)
        
        # 发送测试请求
        response = model.generate_content("测试：请回复'配置成功'")
        
        print("✓ API调用成功！")
        print(f"响应: {response.text[:100]}")
        
        return True
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        print("\n可能的原因:")
        print("1. API Key无效")
        print("2. 模型名称错误（尝试: gemini-1.5-flash 或 gemini-1.5-pro）")
        print("3. 网络连接问题")
        return False

if __name__ == "__main__":
    success = check_configuration()
    sys.exit(0 if success else 1)
