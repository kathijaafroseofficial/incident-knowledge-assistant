#!/bin/sh
# Run OpenClaw gateway (internal port) then the Incident Knowledge API (Render $PORT).
# Both run in the same container so the API can call OpenClaw at 127.0.0.1.

set -e

# OpenClaw state dir (ephemeral on Render free tier); workspace for deployed path
export OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-/data}"
mkdir -p "$OPENCLAW_STATE_DIR"
mkdir -p "$OPENCLAW_STATE_DIR/workspace"

# Create openclaw.json from env so chat completions work (no persistent disk)
# OPENCLAW_GATEWAY_TOKEN must be set in Render; same token as OPENCLAW_AUTH_TOKEN for the API.
# Model: default OpenAI GPT-5-nano (set OPENAI_API_KEY). Set OPENCLAW_DEFAULT_MODEL to override.
# Set OPENCLAW_USE_QWEN_PORTAL=true for qwen-portal; set GROQ_API_KEY for Groq Llama.
if [ -n "$OPENCLAW_GATEWAY_TOKEN" ]; then
  USE_QWEN_PORTAL="${OPENCLAW_USE_QWEN_PORTAL:-false}"
  if [ -n "$OPENCLAW_DEFAULT_MODEL" ]; then
    PRIMARY_MODEL="$OPENCLAW_DEFAULT_MODEL"
  elif [ "$USE_QWEN_PORTAL" = "true" ]; then
    PRIMARY_MODEL="qwen-portal/coder-model"
  elif [ -n "$GROQ_API_KEY" ]; then
    PRIMARY_MODEL="groq/llama-3.1-8b-instant"
  else
    PRIMARY_MODEL="openai/gpt-5-nano"
  fi

  if [ "$USE_QWEN_PORTAL" = "true" ] || [ "$PRIMARY_MODEL" = "qwen-portal/coder-model" ] || [ "$PRIMARY_MODEL" = "qwen-portal/vision-model" ]; then
    # Config with qwen-portal provider and OAuth profile; workspace = deployed path
    cat > "$OPENCLAW_STATE_DIR/openclaw.json" << EOF
{
  "auth": {
    "profiles": {
      "qwen-portal:default": {
        "provider": "qwen-portal",
        "mode": "oauth"
      }
    }
  },
  "models": {
    "providers": {
      "qwen-portal": {
        "baseUrl": "https://portal.qwen.ai/v1",
        "apiKey": "qwen-oauth",
        "api": "openai-completions",
        "models": [
          { "id": "coder-model", "name": "Qwen Coder", "reasoning": false, "input": ["text"], "contextWindow": 128000, "maxTokens": 8192 },
          { "id": "vision-model", "name": "Qwen Vision", "reasoning": false, "input": ["text", "image"], "contextWindow": 128000, "maxTokens": 8192 }
        ]
      }
    }
  },
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
  },
  "plugins": {
    "entries": {
      "qwen-portal-auth": { "enabled": true }
    }
  }
}
EOF
  else
    # Groq/default config with workspace = deployed path
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
    "list": [{ "id": "main", "default": true }]
  }
}
EOF
  fi
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
