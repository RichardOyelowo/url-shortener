set -e
    
alembic upgrade head
fastapi run app/main.py --host 0.0.0.0 --port "${PORT:-8000}"
