#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r myproject/requirements.txt
python myproject/manage.py collectstatic --no-input
python myproject/manage.py migrate --noinput
