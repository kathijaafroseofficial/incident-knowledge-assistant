#!/bin/sh
# Run OpenClaw gateway (internal port) then the Incident Knowledge API (Render $PORT).
# Both run in the same container so the API can call OpenClaw at 127.0.0.1.

set -e

# OpenClaw state dir (ephemeral on Render free tier)
export OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-/data}"
mkdir -p "$OPENCLAW_STATE_DIR"

# Create openclaw.json from env so chat completions work (no persistent disk)
# OPENCLAW_GATEWAY_TOKEN must be set in Render; same token as OPENCLAW_AUTH_TOKEN for the API.
# Model: use GROQ_API_KEY for free Qwen (Groq); else ANTHROPIC_API_KEY for Claude.
if [ -n "$OPENCLAW_GATEWAY_TOKEN" ]; then
  if [ -n "$GROQ_API_KEY" ]; then
    PRIMARY_MODEL="${OPENCLAW_DEFAULT_MODEL:-groq/qwen/qwen3-32b}"
  else
    PRIMARY_MODEL="${OPENCLAW_DEFAULT_MODEL:-anthropic/claude-3-5-sonnet-latest}"
  fi
  cat > "$OPENCLAW_STATE_DIR/openclaw.json" << EOF
{
  "gateway": {
    "http": { "endpoints": { "chatCompletions": { "enabled": true } } },
    "auth": { "mode": "token", "token": "$OPENCLAW_GATEWAY_TOKEN" }
  },
  "agents": {
    "defaults": { "model": { "primary": "$PRIMARY_MODEL" } },
    "list": [{ "id": "main", "default": true }]
  }
}
EOF
fi

# Start OpenClaw gateway on 3000 (internal); API will use OPENCLAW_GATEWAY_URL=http://127.0.0.1:3000
# --bind loopback = default; only 127.0.0.1 (no Control UI config needed; API is in same container)
cd /app/openclaw
node openclaw.mjs gateway --allow-unconfigured --port 3000 --bind loopback &
OPENCLAW_PID=$!

# Give gateway a moment to bind
sleep 3

# Run the Incident Knowledge API on $PORT (Render sends traffic here)
# In this container OpenClaw is always on 3000 — force URL so API never uses default 18789
export OPENCLAW_GATEWAY_URL="http://127.0.0.1:3000"
cd /app
exec /app/venv/bin/python3 -m uvicorn api_server:app --host 0.0.0.0 --port "${PORT:-8000}"
