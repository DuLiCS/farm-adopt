#!/bin/bash
set -e

echo "=== 山南记 部署脚本 ==="

# 1. 构建用户端
echo ">>> 构建用户端..."
cd farm-adopt-uniapp
npm install
npm run build:h5
cd ..
mkdir -p dist/uniapp
cp -r farm-adopt-uniapp/dist/build/h5/* dist/uniapp/

# 2. 构建管理后台
echo ">>> 构建管理后台..."
cd admin-panel
npm install
npm run build
cd ..
mkdir -p dist/admin
cp -r admin-panel/dist/* dist/admin/

# 3. 启动服务
echo ">>> 启动服务..."
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

echo "=== 部署完成 ==="
