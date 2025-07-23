#!/bin/bash
set -e

# Wait for the database to be ready
until pg_isready -h db -U postgres; do
  echo "Waiting for postgres..."
  sleep 2
done

# Run ETL (optional: check if already seeded)
python api/etl.py

# Start the app
exec uvicorn api.main:app --host 0.0.0.0 --port 8000