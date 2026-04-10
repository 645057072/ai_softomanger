#!/usr/bin/env bash
# 在已 docker compose up 的项目根目录执行：将宿主机上的 SQLite 文件迁移到 compose 中的 MySQL。
# 依赖：backend 镜像已构建；exam_system/exam_system.db 存在；db（MySQL）服务健康。

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

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
    echo "ERROR: 未找到 docker compose"
    exit 127
  fi
}

SQLITE_IN_CONTAINER="/app/exam_system/exam_system.db"
# 继承 compose 中 backend 的 MYSQL_*（来自宿主机 .env），无需在脚本里写密码
run_dc run --rm \
  -e FLASK_CONFIG=production \
  backend \
  python scripts/migrate_sqlite_to_mysql.py --sqlite "$SQLITE_IN_CONTAINER"
