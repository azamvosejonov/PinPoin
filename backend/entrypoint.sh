#!/bin/bash
set -e

export PYTHONPATH="/app"

alembic upgrade head
exec uvicorn app.api:app --host 0.0.0.0 --port 8000
