"""
验证Gemini API配置 - 简化版
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Gemini API Configuration Check")
print("=" * 60)

# 检查API Key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("[X] GEMINI_API_KEY NOT SET")
    print("\nPlease create .env file with:")
    print("GEMINI_API_KEY=your_api_key_here")
    print("DEFAULT_MODEL=gemini-1.5-flash")
else:
    print(f"[OK] GEMINI_API_KEY set (length: {len(api_key)})")
    
    # 检查模型
    model = os.getenv('DEFAULT_MODEL', 'gemini-1.5-flash')
    print(f"[OK] Model: {model}")
    
    # 测试API
    print("\nTesting API connection...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model_obj = genai.GenerativeModel(model)
        response = model_obj.generate_content("Say 'OK' if you can read this")
        print("[OK] API call successful!")
        print(f"Response: {response.text[:50]}")
    except Exception as e:
        print(f"[FAIL] API call failed: {e}")
        print("\nPossible issues:")
        print("1. Invalid API Key")
        print("2. Wrong model name (try: gemini-1.5-flash)")
        print("3. Network connection problem")

print("=" * 60)
