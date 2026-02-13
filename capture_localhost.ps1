# PowerShell脚本 - 自动打开浏览器并等待
# 使用方法: .\capture_localhost.ps1

Write-Host "🌐 正在打开浏览器访问 http://localhost:8000/" -ForegroundColor Green

# 启动默认浏览器
Start-Process "http://localhost:8000/"

Write-Host "⏳ 等待3秒让页面加载..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "📸 请手动截图验证以下内容:" -ForegroundColor Cyan
Write-Host "   1. 页面是否正常加载" -ForegroundColor White
Write-Host "   2. 是否看到 '2D像素风办公室' 区域 (Canvas画布)" -ForegroundColor White  
Write-Host "   3. Canvas背景是否为深蓝色 (#2c3e50)" -ForegroundColor White
Write-Host "   4. 是否显示5个Agent精灵:" -ForegroundColor White
Write-Host "      - 👨‍💼 项目经理 (左上)" -ForegroundColor White
Write-Host "      - 📋 游戏策划 (右上)" -ForegroundColor White
Write-Host "      - 👨‍💻 程序员 (左下)" -ForegroundColor White
Write-Host "      - 🎨 美术设计 (右下)" -ForegroundColor White
Write-Host "      - 🧪 测试工程师 (底部中间)" -ForegroundColor White
Write-Host "   5. 按F12打开控制台,检查是否有错误" -ForegroundColor White
Write-Host ""
Write-Host "💡 提示: 使用 Win+Shift+S 进行截图" -ForegroundColor Green
Write-Host ""

# 可选: 如果安装了Selenium,可以自动截图
$useSelenium = Read-Host "是否尝试使用Selenium自动截图? (需要先安装) [y/N]"

if ($useSelenium -eq 'y' -or $useSelenium -eq 'Y') {
    Write-Host "⚠️ 需要先安装Selenium:" -ForegroundColor Yellow
    Write-Host "   Install-Module Selenium -Scope CurrentUser" -ForegroundColor White
    Write-Host ""
    Write-Host "然后运行 selenium_screenshot.ps1" -ForegroundColor White
}

Read-Host "Press Enter to exit"
