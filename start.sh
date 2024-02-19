#!/bin/bash
alembic revision --autogenerate -m "init"
alembic upgrade head
exec uvicorn main:app --port=8001 --host=0.0.0.0