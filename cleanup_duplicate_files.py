#!/usr/bin/env python3
"""
文档清理脚本 - 删除重复和过期的文档文件

功能:
1. 自动备份要删除的文件到 backup/ 目录
2. 删除根目录下的重复文档（保留 docs/ 中的最新版本）
3. 移动错放的文件到正确位置
4. 生成清理报告

安全特性:
- 删除前自动备份
- 详细的操作日志
- 可回滚（使用 restore_backup.py）

作者: Cursor AI
创建日期: 2026-02-11
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


class DocumentCleaner:
    """文档清理工具"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_before_cleanup"
        self.log = []
        
        # 要删除的文件列表（根目录下的重复/过期文件）
        self.files_to_delete = [
            "开发计划.md",           # docs/ 中有最新版本（1600行 vs 1529行）
            "P2前置任务清单.md",      # docs/ 中有相同版本
            "platform_constitution.md",  # docs/ 中有最新版本（1062行 vs 499行，严重过期）
            "P4开发完成总结.md",      # docs/ 中已有 P4_阶段完成报告.md
        ]
        
        # docs/ 中要删除的过期文件
        self.docs_files_to_delete = [
            "docs/README.md",  # 根目录有最新完整版本（181行 vs 65行）
        ]
        
        # 所有要删除的文件
        self.all_files_to_delete = self.files_to_delete + self.docs_files_to_delete
    
    def log_message(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log.append(log_entry)
        print(log_entry)
    
    def create_backup(self):
        """创建备份目录"""
        if self.backup_dir.exists():
            # 如果备份目录已存在，创建带时间戳的新目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_dir = self.project_root / f"backup_before_cleanup_{timestamp}"
        
        self.backup_dir.mkdir(exist_ok=True)
        self.log_message(f"创建备份目录: {self.backup_dir}")
    
    def backup_file(self, file_path: Path) -> bool:
        """备份单个文件"""
        if not file_path.exists():
            self.log_message(f"文件不存在，跳过备份: {file_path}", "WARNING")
            return False
        
        # 保持相对路径结构
        relative_path = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path
        
        # 创建备份目录
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 复制文件
        shutil.copy2(file_path, backup_path)
        self.log_message(f"已备份: {relative_path}")
        return True
    
    def delete_file(self, file_path: Path) -> bool:
        """删除文件"""
        if not file_path.exists():
            self.log_message(f"文件不存在，跳过删除: {file_path}", "WARNING")
            return False
        
        try:
            file_path.unlink()
            self.log_message(f"已删除: {file_path.relative_to(self.project_root)}", "SUCCESS")
            return True
        except Exception as e:
            self.log_message(f"删除失败: {file_path} - {e}", "ERROR")
            return False
    
    def analyze_files(self):
        """分析要清理的文件"""
        self.log_message("\n" + "="*80)
        self.log_message("文件分析报告")
        self.log_message("="*80)
        
        total_size = 0
        existing_files = []
        
        for file_name in self.all_files_to_delete:
            file_path = self.project_root / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                total_size += size
                existing_files.append((file_name, size))
                self.log_message(f"  📄 {file_name:40} {size:>10,} 字节")
            else:
                self.log_message(f"  ⚠️  {file_name:40} (不存在)", "WARNING")
        
        self.log_message(f"\n总计: {len(existing_files)} 个文件, {total_size:,} 字节")
        self.log_message("="*80 + "\n")
        
        return existing_files
    
    def show_comparison(self):
        """显示文件对比说明"""
        self.log_message("\n" + "="*80)
        self.log_message("文件对比说明")
        self.log_message("="*80)
        
        comparisons = [
            {
                "删除": "开发计划.md (根目录)",
                "保留": "docs/开发计划.md",
                "原因": "docs版本更新 (1600行 vs 1529行，多71行)",
            },
            {
                "删除": "platform_constitution.md (根目录)",
                "保留": "docs/platform_constitution.md",
                "原因": "docs版本最新 (1062行 vs 499行，包含P3-P4完整记录) ⚠️ 严重过期",
            },
            {
                "删除": "P2前置任务清单.md (根目录)",
                "保留": "docs/P2前置任务清单.md",
                "原因": "内容相同，统一放在docs目录",
            },
            {
                "删除": "P4开发完成总结.md (根目录)",
                "保留": "docs/P4_阶段完成报告.md",
                "原因": "docs中已有更规范的报告",
            },
            {
                "删除": "docs/README.md",
                "保留": "README.md (根目录)",
                "原因": "根目录版本是最新完整版 (181行 vs 65行)",
            },
        ]
        
        for i, comp in enumerate(comparisons, 1):
            self.log_message(f"\n{i}. {comp['删除']}")
            self.log_message(f"   ❌ 删除原因: {comp['原因']}")
            self.log_message(f"   ✅ 保留文件: {comp['保留']}")
        
        self.log_message("\n" + "="*80 + "\n")
    
    def clean(self, dry_run: bool = False):
        """执行清理"""
        self.log_message("\n" + "🚀 开始文档清理")
        self.log_message(f"项目根目录: {self.project_root}")
        self.log_message(f"运行模式: {'模拟运行（不实际删除）' if dry_run else '实际执行'}")
        
        # 显示文件对比说明
        self.show_comparison()
        
        # 分析文件
        existing_files = self.analyze_files()
        
        if not existing_files:
            self.log_message("没有需要清理的文件", "INFO")
            return
        
        if dry_run:
            self.log_message("\n⚠️  这是模拟运行，不会实际删除文件")
            self.log_message("如需实际执行，请运行: python cleanup_duplicate_files.py --execute")
            return
        
        # 创建备份
        self.create_backup()
        
        # 备份并删除文件
        self.log_message("\n" + "="*80)
        self.log_message("开始备份和删除")
        self.log_message("="*80)
        
        success_count = 0
        for file_name, _ in existing_files:
            file_path = self.project_root / file_name
            
            # 备份
            if self.backup_file(file_path):
                # 删除
                if self.delete_file(file_path):
                    success_count += 1
        
        # 生成总结报告
        self.log_message("\n" + "="*80)
        self.log_message("清理完成总结")
        self.log_message("="*80)
        self.log_message(f"✅ 成功清理: {success_count}/{len(existing_files)} 个文件")
        self.log_message(f"📦 备份位置: {self.backup_dir}")
        self.log_message(f"📝 日志条目: {len(self.log)} 条")
        
        # 保存日志
        self.save_log()
        
        # 显示后续步骤
        self.show_next_steps()
    
    def save_log(self):
        """保存清理日志"""
        log_file = self.backup_dir / "cleanup_log.txt"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(self.log))
        self.log_message(f"\n日志已保存: {log_file}")
    
    def show_next_steps(self):
        """显示后续步骤"""
        self.log_message("\n" + "="*80)
        self.log_message("📋 后续步骤")
        self.log_message("="*80)
        self.log_message("\n1. 验证清理结果:")
        self.log_message("   - 检查 docs/ 目录是否包含所有必要文档")
        self.log_message("   - 检查根目录是否只剩 README.md")
        self.log_message("\n2. 如需回滚:")
        self.log_message(f"   python restore_backup.py {self.backup_dir.name}")
        self.log_message("\n3. 确认无误后:")
        self.log_message(f"   可以删除备份目录: {self.backup_dir}")
        self.log_message("\n" + "="*80)


def main():
    """主函数"""
    import sys
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    
    # 判断是否为实际执行
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] in ["--execute", "-e"]:
        dry_run = False
    
    # 创建清理器
    cleaner = DocumentCleaner(str(project_root))
    
    # 执行清理
    cleaner.clean(dry_run=dry_run)
    
    print("\n" + "="*80)
    if dry_run:
        print("✅ 模拟运行完成！如需实际执行，请运行:")
        print("   python cleanup_duplicate_files.py --execute")
    else:
        print("✅ 清理完成！")
    print("="*80)


if __name__ == "__main__":
    main()
