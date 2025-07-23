#!/bin/bash
set -e


# Start the app
exec uvicorn api.main:app --host 0.0.0.0 --port 8000