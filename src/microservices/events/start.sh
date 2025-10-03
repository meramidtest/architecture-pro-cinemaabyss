#!/usr/bin/env bash
set -euo pipefail

_term() {
  echo "[entrypoint] Caught signal, forwarding to children..."
  kill -TERM "$GUNICORN_PID" 2>/dev/null || true
  kill -TERM "$CONSUMER_PID" 2>/dev/null || true
  wait "$GUNICORN_PID" 2>/dev/null || true
  wait "$CONSUMER_PID" 2>/dev/null || true
}
trap _term SIGTERM SIGINT

/usr/local/bin/python -u server.py &
GUNICORN_PID=$!

/usr/local/bin/python -u consumer.py &
CONSUMER_PID=$!

wait -n "$GUNICORN_PID" "$CONSUMER_PID"
kill -TERM "$GUNICORN_PID" "$CONSUMER_PID" 2>/dev/null || true
wait
