#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
backend_dir="$root_dir/backend/jcourse_api-master"

if ! command -v uv >/dev/null || ! command -v npm >/dev/null; then
  echo 'Need uv and npm on PATH.' >&2
  exit 1
fi

if [ ! -f "$root_dir/.env.preview.local" ]; then
  printf 'SECRET_KEY=%s\nHASH_SALT=%s\n' "$(openssl rand -hex 32)" "$(openssl rand -hex 32)" > "$root_dir/.env.preview.local"
  chmod 600 "$root_dir/.env.preview.local"
fi
set -a
source "$root_dir/.env.preview.local"
set +a
export USE_SQLITE=1 DEBUG=False

uv venv --python 3.13 "$backend_dir/.venv"
req_file="$(mktemp)"
trap 'rm -f "$req_file"' EXIT
sed '/^mysqlclient/d' "$backend_dir/requirements.txt" > "$req_file"
uv pip install --python "$backend_dir/.venv/bin/python" -r "$req_file"

(
  cd "$backend_dir"
  .venv/bin/python manage.py migrate --noinput
  .venv/bin/python manage.py sync_hkustgz_courses
  .venv/bin/python manage.py shell -c 'import pathlib,secrets; from django.contrib.auth.models import User; p=pathlib.Path("../../.preview-login"); u,created=User.objects.get_or_create(username="preview"); password=secrets.token_urlsafe(16) if created or not p.exists() else p.read_text().split("password: ",1)[1].strip(); u.set_password(password); u.save(); p.write_text("username: preview\npassword: "+password+"\n"); p.chmod(0o600)'
)
(
  cd "$root_dir/frontend"
  npm install --no-audit --no-fund --legacy-peer-deps --registry=https://registry.npmjs.org/
)
echo "Ready. Run ./scripts/start-preview.sh and see .preview-login for the local account."
