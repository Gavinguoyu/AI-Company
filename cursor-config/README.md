# Cursor 配置同步指南

本文件夹包含 Cursor IDE 的配置文件，方便在多台电脑间同步设置。

## 配置文件说明

| 文件 | 用途 | 目标位置 |
|------|------|----------|
| `settings.json` | 编辑器设置 | `%APPDATA%\Cursor\User\settings.json` |
| `keybindings.json` | 快捷键绑定 | `%APPDATA%\Cursor\User\keybindings.json` |
| `mcp.json.example` | MCP配置模板 | `~/.cursor/mcp.json` |

## 快速同步步骤

### Windows 系统

1. **运行同步脚本**
   ```powershell
   .\sync-cursor-config.ps1
   ```

2. **手动配置 MCP (首次使用)**
   - 复制 `mcp.json.example` 到 `C:\Users\你的用户名\.cursor\mcp.json`
   - 替换其中的占位符：
     - `YOUR_PROJECTS_PATH` → 你的项目路径
     - `YOUR_DOCUMENTS_PATH` → 你的文档路径
     - `YOUR_GITHUB_TOKEN_HERE` → 你的 GitHub Personal Access Token

### 手动同步

如果脚本无法运行，可以手动复制：

```powershell
# 编辑器设置
Copy-Item "settings.json" "$env:APPDATA\Cursor\User\settings.json"

# 快捷键
Copy-Item "keybindings.json" "$env:APPDATA\Cursor\User\keybindings.json"

# MCP配置 (需要先修改占位符)
Copy-Item "mcp.json.example" "$env:USERPROFILE\.cursor\mcp.json"
```

## 获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选需要的权限 (repo, user)
4. 生成并复制 token

## 注意事项

- `mcp.json` 包含敏感信息（GitHub Token），已使用 `.example` 模板形式存储
- 请勿将包含真实 Token 的配置文件提交到 Git
- 同步后需要重启 Cursor 使配置生效
