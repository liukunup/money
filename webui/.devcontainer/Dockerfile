# 使用国内加速的官方 Node.js Dev Container 镜像（含 npm, yarn, pnpm, git, zsh, docker CLI）
FROM mcr.microsoft.com/devcontainers/javascript-node:24

# 安装额外开发工具
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        vim \
        curl \
        httpie \
        entr \
        watchexec \
    && rm -rf /var/lib/apt/lists/*

# 安装常用全局包（Vue CLI 可选，Vite 项目通常不需要）
USER node
RUN npm install -g \
    typescript \
    ts-node \
    pnpm \
    vite \
    @vitejs/plugin-vue \
    eslint \
    prettier \
    npm-check-updates

# 设置默认 Shell 为 zsh（提升体验）
COPY .zshrc /home/node/.zshrc
RUN chsh -s $(which zsh) node

# 设置工作目录
WORKDIR /workspace

# 使用非 root 用户（安全）
USER node