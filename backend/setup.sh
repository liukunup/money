#!/bin/bash

set -euo pipefail

echo "🚀 开始设置开发环境..."

# echo "🔄 更换 pip 源..."
# pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
# pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
# pip install --no-cache-dir --upgrade pip setuptools wheel

# echo "🔄 更换 apt 源..."
# sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g'      /etc/apt/sources.list.d/debian.sources
# sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# 检查是否已安装 uv
if ! command -v uv &> /dev/null; then
    echo "📦 安装 uv 工具..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"  # 确保当前会话能用 uv
else
    echo "✅ uv 已安装"
fi

# 创建虚拟环境（如果不存在）
if [ ! -d ".venv" ]; then
    echo "🛠️  创建虚拟环境 .venv ..."
    uv venv
else
    echo "✅ 虚拟环境 .venv 已存在"
fi

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source .venv/bin/activate

# 安装项目依赖
echo "📥 安装项目依赖..."
uv pip install --link-mode=copy .

# 验证安装
echo "✅ 环境设置完成！"
echo "💡 请手动运行以下命令激活环境（如果未自动激活）："
echo "   source .venv/bin/activate"
echo "💡 启动 FastAPI 开发服务器："
echo "   uv run fastapi dev"
