#!/bin/bash
set -e

export PYTHONPATH="/app"

python -m app.create_initial_admin || echo "[bootstrap] create_initial_admin failed (non-fatal)"

alembic upgrade head
exec uvicorn app.api:app --host 0.0.0.0 --port 8000
