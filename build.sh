#!/usr/bin/env bash

set -o errexit

echo "========================================="
echo "JanMitra Production Build"
echo "========================================="

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running Django system checks..."
python manage.py check

echo "========================================="
echo "JanMitra build completed successfully"
echo "========================================="
