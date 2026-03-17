#!/bin/sh
# Run OpenClaw gateway (internal port) then the Incident Knowledge API (Render $PORT).
# Both run in the same container so the API can call OpenClaw at 127.0.0.1.

set -e

# OpenClaw state dir (ephemeral on Render free tier)
export OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-/data}"
mkdir -p "$OPENCLAW_STATE_DIR"

# Create openclaw.json from env so chat completions work (no persistent disk)
# OPENCLAW_GATEWAY_TOKEN must be set in Render; same token as OPENCLAW_AUTH_TOKEN for the API.
if [ -n "$OPENCLAW_GATEWAY_TOKEN" ]; then
  cat > "$OPENCLAW_STATE_DIR/openclaw.json" << EOF
{
  "gateway": {
    "http": { "endpoints": { "chatCompletions": { "enabled": true } } },
    "auth": { "mode": "token", "token": "$OPENCLAW_GATEWAY_TOKEN" }
  },
  "agents": {
    "defaults": { "model": { "primary": "anthropic/claude-3-5-sonnet-latest" } },
    "list": [{ "id": "main", "default": true }]
  }
}
EOF
fi

# Start OpenClaw gateway on 3000 (internal); API will use OPENCLAW_GATEWAY_URL=http://127.0.0.1:3000
cd /app/openclaw
node openclaw.mjs gateway --allow-unconfigured --port 3000 --bind 0.0.0.0 &
OPENCLAW_PID=$!

# Give gateway a moment to bind
sleep 3

# Run the Incident Knowledge API on $PORT (Render sends traffic here)
cd /app
exec /app/venv/bin/python3 -m uvicorn api_server:app --host 0.0.0.0 --port "${PORT:-8000}"
