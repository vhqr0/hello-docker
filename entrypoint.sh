#!/usr/bin/env bash

set -e

if [ "$ENV" = 'DEV' ]; then
    echo "running dev server"
    exec python3 /app/identidock.py
else
    echo "running prod server"
    exec uwsgi --http 0.0.0.0:5000 --wsgi-file /app/identidock.py --callable app
fi
