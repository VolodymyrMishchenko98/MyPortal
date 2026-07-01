#!/usr/bin/env bash
# Render запускає цей файл при кожному деплої
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
