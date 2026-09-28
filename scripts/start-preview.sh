#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
backend_dir="$root_dir/backend/jcourse_api-master"
if [ ! -f "$root_dir/.env.preview.local" ] || [ ! -x "$backend_dir/.venv/bin/python" ] || [ ! -d "$root_dir/frontend/node_modules" ]; then
  echo 'Run ./scripts/setup-preview.sh first.' >&2
  exit 1
fi
set -a
source "$root_dir/.env.preview.local"
set +a
export USE_SQLITE=1 DEBUG=False SESSION_COOKIE_SECURE=False CSRF_COOKIE_SECURE=False

(
  cd "$backend_dir"
  .venv/bin/python manage.py runserver --noreload 127.0.0.1:18000
) &
backend_pid=$!
trap 'kill "$backend_pid" 2>/dev/null || true' EXIT

cd "$root_dir/frontend"
REMOTE_URL=http://127.0.0.1:18000 npm run dev -- --hostname 127.0.0.1 --port 3000
