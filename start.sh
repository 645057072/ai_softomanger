#!/bin/bash

# 启动脚本

echo "================================"
echo "  考试系统启动脚本  "
echo "================================"

# 检查是否安装了Docker
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装Docker，请先安装Docker"
    exit 1
fi

# 检查是否安装了Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未安装Docker Compose，请先安装Docker Compose"
    exit 1
fi

# 构建并启动服务
echo "正在构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "正在等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 显示访问地址
echo "================================"
echo "服务已启动，访问地址:"
echo "前端: https://localhost"
echo "后端API: https://localhost/api"
echo "================================"
