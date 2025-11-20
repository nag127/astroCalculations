#!/usr/bin/env bash

# Render calls this script to start the FastAPI server.
# The host/port must match Render's expectations (0.0.0.0 and $PORT).

set -e

PORT=${PORT:-10000}

uvicorn server:app --host 0.0.0.0 --port "$PORT"
