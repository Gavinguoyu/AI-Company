#!/usr/bin/env python3
"""
备份恢复脚本 - 恢复被清理的文件

功能:
- 从备份目录恢复所有文件
- 恢复原始目录结构
- 生成恢复报告

使用方法:
    python restore_backup.py backup_before_cleanup
    或
    python restore_backup.py backup_before_cleanup_20260211_143025

作者: Cursor AI
创建日期: 2026-02-11
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


class BackupRestorer:
    """备份恢复工具"""
    
    def __init__(self, project_root: str, backup_dir_name: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / backup_dir_name
        self.log = []
    
    def log_message(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log.append(log_entry)
        print(log_entry)
    
    def validate_backup(self) -> bool:
        """验证备份目录"""
        if not self.backup_dir.exists():
            self.log_message(f"备份目录不存在: {self.backup_dir}", "ERROR")
            return False
        
        if not self.backup_dir.is_dir():
            self.log_message(f"备份路径不是目录: {self.backup_dir}", "ERROR")
            return False
        
        # 检查是否有文件
        files = list(self.backup_dir.rglob("*"))
        if not files:
            self.log_message("备份目录为空", "ERROR")
            return False
        
        self.log_message(f"发现备份文件: {len([f for f in files if f.is_file()])} 个")
        return True
    
    def restore(self, dry_run: bool = False) -> bool:
        """恢复备份"""
        self.log_message("\n" + "="*80)
        self.log_message("🔄 开始恢复备份")
        self.log_message("="*80)
        self.log_message(f"项目根目录: {self.project_root}")
        self.log_message(f"备份目录: {self.backup_dir}")
        self.log_message(f"运行模式: {'模拟运行（不实际恢复）' if dry_run else '实际执行'}")
        
        # 验证备份
        if not self.validate_backup():
            return False
        
        # 获取所有备份文件
        backup_files = [f for f in self.backup_dir.rglob("*") if f.is_file()]
        
        # 排除日志文件
        backup_files = [f for f in backup_files if f.name != "cleanup_log.txt"]
        
        self.log_message(f"\n找到 {len(backup_files)} 个文件待恢复")
        
        if dry_run:
            self.log_message("\n⚠️  这是模拟运行，不会实际恢复文件")
            self.log_message("模拟恢复列表:")
            for backup_file in backup_files:
                relative_path = backup_file.relative_to(self.backup_dir)
                target_path = self.project_root / relative_path
                self.log_message(f"  📄 {relative_path} → {target_path}")
            self.log_message("\n如需实际执行，请运行:")
            self.log_message(f"   python restore_backup.py {self.backup_dir.name} --execute")
            return True
        
        # 实际恢复
        self.log_message("\n" + "="*80)
        self.log_message("开始恢复文件")
        self.log_message("="*80)
        
        success_count = 0
        for backup_file in backup_files:
            relative_path = backup_file.relative_to(self.backup_dir)
            target_path = self.project_root / relative_path
            
            try:
                # 创建目标目录
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 检查目标文件是否存在
                if target_path.exists():
                    self.log_message(f"⚠️  目标文件已存在，将被覆盖: {relative_path}", "WARNING")
                
                # 复制文件
                shutil.copy2(backup_file, target_path)
                self.log_message(f"✅ 已恢复: {relative_path}")
                success_count += 1
                
            except Exception as e:
                self.log_message(f"❌ 恢复失败: {relative_path} - {e}", "ERROR")
        
        # 生成总结报告
        self.log_message("\n" + "="*80)
        self.log_message("恢复完成总结")
        self.log_message("="*80)
        self.log_message(f"✅ 成功恢复: {success_count}/{len(backup_files)} 个文件")
        
        if success_count == len(backup_files):
            self.log_message("\n🎉 所有文件恢复成功！")
            return True
        else:
            self.log_message(f"\n⚠️  部分文件恢复失败: {len(backup_files) - success_count} 个", "WARNING")
            return False


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python restore_backup.py <backup_dir_name> [--execute]")
        print("\n示例:")
        print("  python restore_backup.py backup_before_cleanup")
        print("  python restore_backup.py backup_before_cleanup --execute")
        print("\n可用的备份目录:")
        
        # 列出所有备份目录
        project_root = Path(__file__).parent
        backup_dirs = [d for d in project_root.iterdir() 
                      if d.is_dir() and d.name.startswith("backup_")]
        
        if backup_dirs:
            for backup_dir in backup_dirs:
                file_count = len([f for f in backup_dir.rglob("*") if f.is_file()])
                print(f"  - {backup_dir.name} ({file_count} 个文件)")
        else:
            print("  (没有找到备份目录)")
        
        return
    
    # 获取参数
    project_root = Path(__file__).parent
    backup_dir_name = sys.argv[1]
    dry_run = True
    
    if len(sys.argv) > 2 and sys.argv[2] in ["--execute", "-e"]:
        dry_run = False
    
    # 创建恢复器
    restorer = BackupRestorer(str(project_root), backup_dir_name)
    
    # 执行恢复
    success = restorer.restore(dry_run=dry_run)
    
    print("\n" + "="*80)
    if dry_run:
        print("✅ 模拟运行完成！如需实际执行，请运行:")
        print(f"   python restore_backup.py {backup_dir_name} --execute")
    elif success:
        print("✅ 恢复完成！")
    else:
        print("⚠️  恢复过程中出现错误，请检查日志")
    print("="*80)


if __name__ == "__main__":
    main()
