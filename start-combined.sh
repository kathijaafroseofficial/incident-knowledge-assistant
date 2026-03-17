#!/bin/sh
# Run OpenClaw gateway (internal port) then the Incident Knowledge API (Render $PORT).
# Post-deploy: OpenAI + OpenClaw only. Set OPENAI_API_KEY and OPENCLAW_GATEWAY_TOKEN in Render.

set -e

# OpenClaw state dir (ephemeral on Render free tier); workspace for deployed path
export OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-/data}"
mkdir -p "$OPENCLAW_STATE_DIR"
mkdir -p "$OPENCLAW_STATE_DIR/workspace"

# openclaw.json: OpenAI only. OpenClaw reads OPENAI_API_KEY from env for openai/gpt-5-nano.
# OPENCLAW_GATEWAY_TOKEN must be set in Render; use same value for OPENCLAW_AUTH_TOKEN when calling the API.
# Optional: OPENCLAW_DEFAULT_MODEL to override (e.g. openai/gpt-4o-mini).
if [ -n "$OPENCLAW_GATEWAY_TOKEN" ]; then
  PRIMARY_MODEL="${OPENCLAW_DEFAULT_MODEL:-openai/gpt-5-nano}"
  cat > "$OPENCLAW_STATE_DIR/openclaw.json" << EOF
{
  "gateway": {
    "http": { "endpoints": { "chatCompletions": { "enabled": true } } },
    "auth": { "mode": "token", "token": "$OPENCLAW_GATEWAY_TOKEN" }
  },
  "agents": {
    "defaults": {
      "model": { "primary": "$PRIMARY_MODEL" },
      "workspace": "$OPENCLAW_STATE_DIR/workspace"
    },
    "list": [{ "id": "main", "default": true, "model": "$PRIMARY_MODEL" }]
  }
}
EOF
fi

# Start OpenClaw gateway on 3000 (internal). NODE_OPTIONS caps heap for 512MB Render limit.
# --bind loopback: only 127.0.0.1 (no Control UI config; API is in same container)
cd /app/openclaw
node openclaw.mjs gateway --allow-unconfigured --port 3000 --bind loopback &
OPENCLAW_PID=$!

# Give gateway a moment to bind
sleep 3

# Incident Knowledge API on $PORT (Render sends traffic here)
export OPENCLAW_GATEWAY_URL="http://127.0.0.1:3000"
cd /app
exec /app/venv/bin/python3 -m uvicorn api_server:app --host 0.0.0.0 --port "${PORT:-8000}"
