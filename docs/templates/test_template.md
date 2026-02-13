# 阶段测试模板

> **用途**: AI生成测试脚本时遵循的标准模板  
> **原则**: 增量测试、快速验证、自动化执行

---

## 📋 测试脚本标准结构

### 文件命名
```
test_p{X}_{module_name}.py
```

### 标准导入
```python
"""
P{X}阶段测试脚本
测试范围: {简要描述本阶段的核心功能}
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入本阶段的核心模块
from backend.{module_path} import {ClassName}
```

---

## 🧪 测试用例结构

### 1. 导入测试（5分钟）
```python
async def test_imports():
    """验证核心模块能否正常导入"""
    print("\n" + "="*60)
    print("📦 测试1: 模块导入")
    print("="*60)
    
    try:
        from backend.{module} import {Class1, Class2}
        print("✅ 导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
```

### 2. 初始化测试（5分钟）
```python
async def test_initialization():
    """验证核心类能否正常实例化"""
    print("\n" + "="*60)
    print("🔧 测试2: 对象初始化")
    print("="*60)
    
    try:
        obj = ClassName(required_params)
        assert obj is not None
        print("✅ 初始化成功")
        return True
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False
```

### 3. 核心功能测试（10-15分钟）
```python
async def test_core_feature_1():
    """测试核心功能1"""
    print("\n" + "="*60)
    print("⚙️ 测试3: {功能名称}")
    print("="*60)
    
    try:
        obj = ClassName()
        result = await obj.key_method(params)
        
        # 验证结果
        assert result is not None
        assert {条件1}
        assert {条件2}
        
        print(f"✅ {功能名称}正常")
        return True
    except Exception as e:
        print(f"❌ {功能名称}失败: {e}")
        return False

async def test_core_feature_2():
    """测试核心功能2"""
    # 类似结构...
    pass
```

### 4. 集成测试（10分钟）
```python
async def test_integration():
    """快速集成测试：验证与之前阶段的集成"""
    print("\n" + "="*60)
    print("🔗 测试4: 集成测试")
    print("="*60)
    
    try:
        # 只测关键集成点，不深入测试旧功能
        from backend.engine.{previous_module} import {PreviousClass}
        
        old_obj = PreviousClass()
        new_obj = NewClass()
        
        # 测试它们能否协同工作
        result = await new_obj.integrate_with(old_obj)
        assert result is True
        
        print("✅ 集成正常")
        return True
    except Exception as e:
        print(f"❌ 集成失败: {e}")
        return False
```

---

## 🎯 测试执行和报告

### 主函数结构
```python
async def main():
    """运行所有测试"""
    print("="*60)
    print(f"🧪 P{X}阶段测试")
    print("="*60)
    
    tests = [
        ("模块导入", test_imports),
        ("对象初始化", test_initialization),
        ("核心功能1", test_core_feature_1),
        ("核心功能2", test_core_feature_2),
        ("集成测试", test_integration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}异常: {e}")
            results.append((name, False))
    
    # 统计结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print("="*60)
    print(f"通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print(f"⚠️ {total - passed}个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

---

## ⚠️ 测试编写规则

### ✅ 应该做的
1. **只测新功能**：只测试本阶段新增的功能
2. **快速验证**：每个测试用例5-15分钟完成
3. **清晰输出**：使用emoji和分隔线，输出易读
4. **独立测试**：每个测试函数独立，互不依赖
5. **异常处理**：所有测试都要有try-except

### ❌ 不应该做的
1. ❌ **重复测旧功能**：不要重新测试P1-P{X-1}的功能（有回归测试）
2. ❌ **过度详细**：不要测试每个参数组合，只测关键场景
3. ❌ **依赖外部**：不要依赖网络、数据库等外部资源（除非必要）
4. ❌ **硬编码路径**：使用相对路径或动态获取
5. ❌ **无意义断言**：断言要验证实际逻辑，不要assert True

---

## 📝 测试结果记录

### 测试通过后
在 `platform_constitution.md` 中简单记录：

```markdown
### 测试验证
✅ 模块导入测试通过
✅ 核心功能测试通过 ({X}/{X})
✅ 集成测试通过
✅ 回归测试通过
```

### 测试失败后
1. 分析错误原因
2. 修复代码
3. 重新运行测试
4. 最多重试3次
5. 如仍失败，上报用户

---

## 🔄 回归测试集成

### run_regression.py更新
每完成一个阶段，将该阶段的关键测试加入回归测试：

```python
# tests/run_regression.py
TESTS = [
    ("P1-LLM客户端", "test_p1.py", "test_llm_client"),
    ("P2-消息总线", "test_p2.py", "test_message_routing"),
    ("P3-文件工具", "test_p3.py", "test_file_tool"),
    ("P4-工作流", "test_p4.py", "test_workflow_init"),
    ("P{X}-{核心功能}", "test_p{X}.py", "test_{关键功能}"),  # 新增
]
```

---

## 💡 测试示例参考

### 简单阶段（P7, P9）- 3-5个测试
```python
tests = [
    ("导入", test_imports),
    ("初始化", test_initialization),
    ("核心功能", test_core_feature),
]
```

### 正常阶段（P5, P6, P10）- 5-8个测试
```python
tests = [
    ("导入", test_imports),
    ("初始化", test_initialization),
    ("核心功能1", test_feature_1),
    ("核心功能2", test_feature_2),
    ("核心功能3", test_feature_3),
    ("集成", test_integration),
]
```

### 复杂阶段（P8）- 8-12个测试
```python
tests = [
    ("导入", test_imports),
    ("初始化", test_initialization),
    ("功能1", test_feature_1),
    ("功能2", test_feature_2),
    ("功能3", test_feature_3),
    ("功能4", test_feature_4),
    ("集成1", test_integration_1),
    ("集成2", test_integration_2),
    ("端到端", test_end_to_end),
]
```

---

**模板版本**: v1.0  
**适用阶段**: P6-P10  
**预期Token消耗**: 生成测试脚本 ~1万tokens (vs 原5万)
