#!/bin/bash
set -e

echo "Starting Money application..."

# 初始化数据库（如果需要）
if [ ! -f /app/data/money.db ]; then
    echo "Initializing database..."
    python -m scripts.init_db
fi

# 启动后端服务
echo "Starting FastAPI backend..."
cd /app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 等待后端启动
echo "Waiting for backend to start..."
sleep 5

# 启动 Nginx
echo "Starting Nginx..."
nginx -g "daemon off;"
