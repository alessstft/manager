#!/bin/bash
set -e

echo "==> Applying migrations..."
python manage.py migrate --noinput

echo "==> Seeding dev users (admin / worker)..."
python manage.py seed_dev_login --employee

echo "==> Starting dev server at http://0.0.0.0:8000"
exec python manage.py runserver 0.0.0.0:8000