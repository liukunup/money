#!/bin/bash

set -euo pipefail

echo "🚀 开始设置开发环境..."

# 1. 检查是否已安装 uv
if ! command -v uv &> /dev/null; then
    echo "📦 安装 uv 工具..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"  # 确保当前会话能用 uv
else
    echo "✅ uv 已安装"
fi

# 2. 创建虚拟环境（如果不存在）
if [ ! -d ".venv" ]; then
    echo "🛠️  创建虚拟环境 .venv ..."
    uv venv
else
    echo "✅ 虚拟环境 .venv 已存在"
fi

# 3. 激活虚拟环境
echo "🔌 激活虚拟环境..."
source .venv/bin/activate

# 4. 安装项目依赖
export UV_LINK_MODE=copy
echo "📥 安装项目（含依赖）..."
uv pip install .

# 5. 验证安装
echo "✅ 环境设置完成！"
echo "💡 请手动运行以下命令激活环境（如果未自动激活）："
echo "   source .venv/bin/activate"
echo "💡 启动 FastAPI 开发服务器："
echo "   uv run fastapi dev"