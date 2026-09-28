#!/bin/bash
set -e

echo "Waiting for MySQL..."
while ! mysqladmin ping -h "${MYSQL_HOST:-db}" -P "${MYSQL_PORT:-3306}" --silent; do
  sleep 1
done
echo "MySQL is ready!"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec "$@"
