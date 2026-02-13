"""
文档完整性验证脚本
验证所有文档是否在正确位置
"""

import os
import sys
from pathlib import Path

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

root = Path(__file__).parent
docs_dir = root / "docs"

print("\n" + "="*70)
print(" "*20 + "文档完整性验证")
print("="*70 + "\n")

# 应该在 docs/ 目录的文档
required_docs = [
    ("文档索引.md", "文档总目录"),
    ("开发计划.md", "项目总纲"),
    ("platform_constitution.md", "平台宪法"),
    ("README.md", "项目详细说明"),
    ("测试总结.md", "P0-P1 测试总结"),
    ("测试报告_P0_P1.md", "P0-P1 详细测试报告"),
    ("P1_测试报告.md", "P1 专项测试报告"),
    ("改进措施实施指南.md", "改进方案详解"),
    ("P2前置任务清单.md", "P2 前置任务清单"),
    ("P2前置任务完成报告.md", "P2 前置任务报告"),
    ("文档整理完成报告.md", "文档整理总结"),
]

print("1. 验证文档存在性")
print("-" * 70)

all_exist = True
for doc_name, description in required_docs:
    doc_path = docs_dir / doc_name
    exists = doc_path.exists()
    status = "[OK]" if exists else "[MISS]"
    print(f"  {status} {description:25s} - docs/{doc_name}")
    if not exists:
        all_exist = False

# 验证根目录 README
print("\n2. 验证根目录 README")
print("-" * 70)
root_readme = root / "README.md"
if root_readme.exists():
    print(f"  [OK] 根目录 README 存在")
else:
    print(f"  [MISS] 根目录 README 不存在")
    all_exist = False

# 检查根目录是否还有其他 md 文件（应该没有）
print("\n3. 检查根目录整洁度")
print("-" * 70)
root_md_files = list(root.glob("*.md"))
root_md_files = [f for f in root_md_files if f.name != "README.md"]

if len(root_md_files) == 0:
    print(f"  [OK] 根目录无多余文档（只有 README.md）")
else:
    print(f"  [WARN] 根目录还有 {len(root_md_files)} 个文档应移至 docs/:")
    for f in root_md_files:
        print(f"    - {f.name}")

# 统计
print("\n4. 文档统计")
print("-" * 70)
all_docs = list(docs_dir.glob("*.md"))
print(f"  docs/ 目录文档总数: {len(all_docs)}")
print(f"  要求文档数量: {len(required_docs)}")

# 列出所有文档
print("\n  所有文档:")
for i, doc in enumerate(sorted(all_docs), 1):
    size_kb = doc.stat().st_size / 1024
    print(f"    {i:2d}. {doc.name:40s} ({size_kb:6.1f} KB)")

# 总结
print("\n" + "="*70)
print(" "*25 + "验证结果")
print("="*70)

if all_exist and len(root_md_files) == 0:
    print("\n[OK] 所有文档验证通过！")
    print("\n  - 所有必需文档都在 docs/ 目录")
    print("  - 根目录整洁（只有 README.md）")
    print("  - 文档结构完整")
    print("\n下一步: 开始 P2 阶段开发")
else:
    print("\n[WARN] 发现问题，请检查上述输出")

print("\n" + "="*70 + "\n")

sys.exit(0 if all_exist else 1)
