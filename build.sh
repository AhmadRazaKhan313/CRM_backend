#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_permissions

python manage.py seed_organization --email "$ADMIN_EMAIL" --password "$ADMIN_PASSWORD" --name "$ADMIN_NAME"
