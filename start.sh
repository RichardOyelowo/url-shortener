#!/bin/bash
alembic upgrade head
echo "SECRET_KEY: $SECRET_KEY"
echo "ADMIN_PASSWORD: $ADMIN_PASSWORD"
fastapi run app/main.py --port 80