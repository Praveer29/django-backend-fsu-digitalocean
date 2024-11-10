#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create a superuser without input (non-interactive)
# this command will create a superuser and it will use the env variables - DJANGO_SUPERUSER_USERNAME , DJANGO_SUPERUSER_EMAIL , DJANGO_SUPERUSER_PASSWORD
# after the superuser has been created when deployment, log in, and change the password and do not store the new password in the env variables in render
python manage.py createsuperuser --noinput || true
