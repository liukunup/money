# 使用国内加速镜像源
FROM mcr.microsoft.com/devcontainers/python:3.12

# 安装系统级工具（调试/开发辅助）
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        curl \
        git \
        vim \
        zsh \
        httpie \
        entr \
        watchexec \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 开发工具链（全局）
RUN pip3 install --no-cache-dir \
    black \
    ruff \
    pylint \
    mypy \
    pytest \
    python-dotenv \
    watchfiles \
    httpx \
    "uvicorn[standard]" \
    fastapi

# 设置默认 Shell 为 zsh（可选）
COPY .zshrc /home/vscode/.zshrc
RUN chsh -s $(which zsh) vscode

# 设置工作目录
WORKDIR /workspace

# 切换到非 root 用户
USER vscode