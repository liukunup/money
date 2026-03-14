FROM python:3.12-slim-bullseye

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 构建前端
COPY webui /app/webui
WORKDIR /app/webui
RUN npm install && npm run build

# 安装后端依赖
COPY app /app/app
COPY pyproject.toml /app
COPY scripts /app/scripts
WORKDIR /app
RUN uv sync --frozen --no-cache

# 安装 Nginx
RUN apt-get update && apt-get install -y nginx

# 创建数据目录
RUN mkdir -p /app/data

# 配置 Nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动脚本
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser
CMD ["/app/entrypoint.sh"]
