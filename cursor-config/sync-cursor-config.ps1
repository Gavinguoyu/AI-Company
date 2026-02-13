# Cursor 配置同步脚本
# 用法: 在 cursor-config 目录下运行此脚本

$ErrorActionPreference = "Stop"

Write-Host "=== Cursor 配置同步工具 ===" -ForegroundColor Cyan
Write-Host ""

# 获取当前脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 目标路径
$cursorUserPath = "$env:APPDATA\Cursor\User"
$cursorHomePath = "$env:USERPROFILE\.cursor"

# 确保目标目录存在
if (-not (Test-Path $cursorUserPath)) {
    Write-Host "创建 Cursor User 目录..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $cursorUserPath -Force | Out-Null
}

if (-not (Test-Path $cursorHomePath)) {
    Write-Host "创建 .cursor 目录..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $cursorHomePath -Force | Out-Null
}

# 同步 settings.json
$settingsSource = Join-Path $scriptDir "settings.json"
$settingsTarget = Join-Path $cursorUserPath "settings.json"
if (Test-Path $settingsSource) {
    Copy-Item $settingsSource $settingsTarget -Force
    Write-Host "[OK] settings.json 已同步" -ForegroundColor Green
} else {
    Write-Host "[跳过] settings.json 源文件不存在" -ForegroundColor Gray
}

# 同步 keybindings.json
$keybindingsSource = Join-Path $scriptDir "keybindings.json"
$keybindingsTarget = Join-Path $cursorUserPath "keybindings.json"
if (Test-Path $keybindingsSource) {
    Copy-Item $keybindingsSource $keybindingsTarget -Force
    Write-Host "[OK] keybindings.json 已同步" -ForegroundColor Green
} else {
    Write-Host "[跳过] keybindings.json 源文件不存在" -ForegroundColor Gray
}

# 检查 MCP 配置
$mcpTarget = Join-Path $cursorHomePath "mcp.json"
$mcpExample = Join-Path $scriptDir "mcp.json.example"

if (Test-Path $mcpTarget) {
    Write-Host "[跳过] mcp.json 已存在，保留现有配置" -ForegroundColor Yellow
    Write-Host "      如需更新，请手动编辑: $mcpTarget" -ForegroundColor Gray
} else {
    if (Test-Path $mcpExample) {
        Write-Host ""
        Write-Host "[注意] MCP 配置需要手动设置:" -ForegroundColor Yellow
        Write-Host "  1. 复制 mcp.json.example 到 $mcpTarget" -ForegroundColor White
        Write-Host "  2. 替换其中的占位符 (YOUR_GITHUB_TOKEN_HERE 等)" -ForegroundColor White
        Write-Host ""
        $copyMcp = Read-Host "是否现在复制模板? (Y/N)"
        if ($copyMcp -eq 'Y' -or $copyMcp -eq 'y') {
            Copy-Item $mcpExample $mcpTarget -Force
            Write-Host "[OK] mcp.json 模板已复制，请编辑配置" -ForegroundColor Green
            # 打开文件供编辑
            Start-Process "notepad" $mcpTarget
        }
    }
}

Write-Host ""
Write-Host "=== 同步完成 ===" -ForegroundColor Cyan
Write-Host "请重启 Cursor 使配置生效" -ForegroundColor Yellow
