# setup-dev-env.ps1

Write-Host "🚀 开始设置开发环境..." -ForegroundColor Green

# 1. 检查是否已安装 uv
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "📦 安装 uv 工具..." -ForegroundColor Yellow
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"  # 立即生效
} else {
    Write-Host "✅ uv 已安装" -ForegroundColor Green
}

# 2. 创建虚拟环境（如果不存在）
if (!(Test-Path ".venv")) {
    Write-Host "🛠️  创建虚拟环境 .venv ..." -ForegroundColor Yellow
    uv venv
} else {
    Write-Host "✅ 虚拟环境 .venv 已存在" -ForegroundColor Green
}

# 3. 激活虚拟环境
Write-Host "🔌 激活虚拟环境..." -ForegroundColor Yellow
. .venv\Scripts\Activate.ps1

# 4. 安装项目依赖
Write-Host "📥 安装项目（含依赖）..." -ForegroundColor Yellow
uv pip install . --link-mode=copy

# 5. 验证安装
Write-Host "✅ 环境设置完成！" -ForegroundColor Green
Write-Host "💡 请确保已激活虚拟环境（如新开终端，请手动运行）：" -ForegroundColor Cyan
Write-Host "   .venv\Scripts\Activate.ps1"
Write-Host "💡 启动 FastAPI 开发服务器：" -ForegroundColor Cyan
Write-Host "   uv run fastapi dev"