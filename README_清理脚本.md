# 📦 文档清理脚本使用指南

> **一键清理项目中的重复和过期文档**  
> 安全、可靠、易用

---

## 🚀 30秒快速开始

### 第一步：查看清理效果

```bash
python cleanup_duplicate_files.py
```

这会显示哪些文件会被删除，**不会实际删除任何文件**。

### 第二步：实际执行清理

```bash
python cleanup_duplicate_files.py --execute
```

自动备份 → 清理文件 → 生成日志

### 第三步：验证结果

```bash
dir *.md        # 根目录应该只有 README.md
dir docs\*.md   # docs/ 包含所有开发文档
```

---

## 📋 要清理的文件（5个）

| 文件 | 位置 | 问题 | 保留版本 |
|------|------|------|---------|
| 开发计划.md | 根目录 | 旧版本 (1529行) | docs/开发计划.md (1600行) |
| platform_constitution.md | 根目录 | **严重过期** (499行) | docs/platform_constitution.md (1062行) |
| P2前置任务清单.md | 根目录 | 重复 | docs/P2前置任务清单.md |
| P4开发完成总结.md | 根目录 | 重复 | docs/P4_阶段完成报告.md |
| README.md | docs/ | 旧版本 (65行) | README.md (根目录, 181行) |

---

## ⚠️ 最严重的问题

**根目录的 `platform_constitution.md` 严重过期**：
- ❌ 只有 499 行（docs 版本有 1062 行）
- ❌ 缺失 P3 阶段（工具系统）记录
- ❌ 缺失 P4 阶段（游戏开发工作流）记录

**如果误用会导致**：
- AI 认为 P3、P4 阶段未完成
- 可能重复开发已实现的功能
- 上下文记忆严重错误

---

## ✅ 清理后效果

### 清理前（混乱）
```
根目录: 5个 .md 文件（混乱）
docs/: 6个 .md 文件
```

### 清理后（规范）
```
根目录: 1个 .md 文件（README.md 项目入口）
docs/: 5个 .md 文件（所有开发文档集中）
```

---

## 🛡️ 安全保障

1. ✅ **自动备份**
   - 删除前自动备份所有文件到 `backup_before_cleanup/`
   - 保持原始目录结构

2. ✅ **可完全回滚**
   ```bash
   python restore_backup.py backup_before_cleanup --execute
   ```

3. ✅ **模拟运行**
   - 先模拟查看效果
   - 确认无误后再执行

4. ✅ **详细日志**
   - 记录每个操作
   - 保存在 `backup_before_cleanup/cleanup_log.txt`

---

## 📚 详细文档

| 文档 | 内容 | 适用场景 |
|------|------|---------|
| **如何清理重复文档.txt** | 30秒快速开始 | 快速上手 |
| **CLEANUP_GUIDE.md** | 详细使用指南 | 完整学习 |
| **CLEANUP_DEMO.md** | 使用演示 | 了解过程 |
| **清理脚本生成报告.md** | 技术报告 | 深入了解 |

---

## ❓ 常见问题

### Q: 清理是否安全？
**A:** 非常安全！自动备份 + 可回滚 + 模拟运行。

### Q: 如何撤销清理？
**A:** 运行 `python restore_backup.py backup_before_cleanup --execute`

### Q: 备份可以删除吗？
**A:** 清理后验证无误，保留 1-2 天后可删除。

### Q: 模拟运行会删除文件吗？
**A:** 不会！模拟运行只显示效果，不会删除任何文件。

---

## 🎯 推荐流程

```
1. 模拟运行
   python cleanup_duplicate_files.py
   ↓
2. 查看输出，确认清理内容
   ↓
3. 实际执行
   python cleanup_duplicate_files.py --execute
   ↓
4. 验证结果
   dir *.md
   dir docs\*.md
   ↓
5. 确认无误后，1-2天后删除备份
   rmdir /s backup_before_cleanup
```

---

## 📞 获取帮助

1. 查看详细指南: `CLEANUP_GUIDE.md`
2. 查看使用演示: `CLEANUP_DEMO.md`
3. 查看操作日志: `backup_before_cleanup/cleanup_log.txt`
4. 恢复文件: `python restore_backup.py backup_before_cleanup --execute`

---

**创建日期**: 2026-02-11  
**版本**: v1.0  
**作者**: Cursor AI

---

## 🎉 现在就开始

```bash
# 第一次使用？先模拟运行看看效果
python cleanup_duplicate_files.py

# 确认无误？立即执行清理
python cleanup_duplicate_files.py --execute
```

**安全提示**: 所有文件都会自动备份，可随时完全回滚，放心使用！
