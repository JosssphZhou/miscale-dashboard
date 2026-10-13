#!/bin/sh
# 首次启动保持蓝牙关闭；确认型号和权限后使用 --connect。
set -eu
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then
  printf '%s\n' '请先按 README 安装依赖，创建 .venv。' >&2
  exit 1
fi
if [ ! -f .env ]; then
  cp .env.example .env
fi
case "${1:-}" in
  '') MISCALE_SCANNER=off ;;
  --connect) MISCALE_SCANNER=on ;;
  *) printf '%s\n' '用法：scripts/start-local.sh [--connect]' >&2; exit 2 ;;
esac
export MISCALE_SCANNER
# 容器使用 /data，本地脚本使用独立的项目 data 目录。
export MISCALE_DB="${MISCALE_DB:-./data/miscale.db}"
exec .venv/bin/python -m uvicorn app.main:app --env-file .env --host 127.0.0.1 --port "${MISCALE_PORT:-18800}"
