#!/usr/bin/env bash
# 在服务器项目根目录执行：停止旧容器并重新构建、启动（含前端静态与后端）
# 优先使用 docker compose；当前用户无权限时使用 sudo docker compose

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

run_dc() {
  if docker compose version >/dev/null 2>&1; then
    docker compose "$@"
  elif sudo docker compose version >/dev/null 2>&1; then
    sudo docker compose "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose "$@"
  elif sudo docker-compose version >/dev/null 2>&1; then
    sudo docker-compose "$@"
  else
    echo "ERROR: 未找到 docker compose，请安装 Docker Compose 插件或 docker-compose"
    exit 127
  fi
}

echo "=== 执行 compose 重建（down -> up -d --build）==="

# Nginx 官方镜像内 worker 非 root，挂载的 frontend/dist 若权限过严会 403；部署前放宽读与目录执行位
if [ -d frontend/dist ]; then
  chmod -R a+rX frontend/dist || true
fi

run_dc down --remove-orphans || true
for name in exam-system-redis exam-system-backend exam-system-frontend exam-system-nginx; do
  docker rm -f "$name" 2>/dev/null || sudo docker rm -f "$name" 2>/dev/null || true
done

run_dc up -d --build --force-recreate
run_dc restart nginx || true

echo "=== 部署命令已执行完毕 ==="
