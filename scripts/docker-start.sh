#!/usr/bin/env bash
# 容器入口：可选一次性 SQLite→MySQL 迁移，再初始化表并启动 Gunicorn
# 构建上下文必须为项目根目录（与 Dockerfile 中 COPY 一致），勿使用 build: ./exam_system

set -e
export FLASK_CONFIG="${FLASK_CONFIG:-production}"

SQLITE_DB="${SQLITE_DB:-/app/exam_system/exam_system.db}"
MARKER_DIR="/app/uploads"
MARKER="${SQLITE_IMPORT_MARKER:-${MARKER_DIR}/.sqlite_migrated_to_mysql}"
mkdir -p "$MARKER_DIR"

if [ "${SKIP_SQLITE_AUTO_IMPORT:-0}" != "1" ] && [ -f "$SQLITE_DB" ] && [ ! -f "$MARKER" ]; then
  echo "[docker-start] 检测到 SQLite 文件，执行一次性迁移到 MySQL: $SQLITE_DB"
  python scripts/migrate_sqlite_to_mysql.py --sqlite "$SQLITE_DB"
  touch "$MARKER"
  echo "[docker-start] 迁移完成，已写入标记 $MARKER（删除该文件可再次尝试导入）"
fi

echo "[docker-start] 初始化数据库表与默认数据..."
python -c "from exam_system.app import create_app; create_app()"

echo "[docker-start] 启动 Gunicorn..."
exec gunicorn "exam_system.app:app" -w 4 -b "0.0.0.0:5001" --timeout 300
