# api_server.py — Public POST endpoint with Bearer token auth (Challenge requirement)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pathlib import Path
import sys
import os
import subprocess
import json

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
from bots import get_bot

# Paths used by combined Docker (OpenClaw + API); override via env in container
OPENCLAW_DIR = os.environ.get("OPENCLAW_DIR", "/app/openclaw")
OPENCLAW_STATE_DIR = os.environ.get("OPENCLAW_STATE_DIR", "/data")

app = FastAPI(title="Incident Knowledge Assistant API", version="1.0.0")
security = HTTPBearer(auto_error=False)


@app.on_event("startup")
def validate_config_on_startup():
    """Production: fail fast if no bot is configured (e.g. missing MOLTBOT_URL/CLAWDBOT_URL/NANOBOT_URL)."""
    config.validate_bot_config()


class ChatRequest(BaseModel):
    """POST body: message and optional log/context."""
    message: str
    context: str = ""


def verify_bearer(credentials: HTTPAuthorizationCredentials | None = None) -> bool:
    """Verify Authorization: Bearer <token> (Challenge requirement)."""
    if not credentials:
        return False
    return credentials.credentials == config.API_BEARER_TOKEN


@app.get("/")
def root():
    return {"service": "Incident Knowledge Assistant", "docs": "/docs"}


@app.post("/chat")
def chat_post(
    body: ChatRequest,
    authorization: HTTPAuthorizationCredentials | None = Depends(security),
):
    """
    Public POST endpoint. Requires header: Authorization: Bearer <your_token>
    """
    if not verify_bearer(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing Bearer token")
    try:
        bot = get_bot()
        reply = bot.chat(body.message, context=body.context)
        # Return 429 when backend (e.g. Groq) rate limits so clients can retry
        if reply and "rate limit" in reply.lower():
            raise HTTPException(
                status_code=429,
                detail="Rate limit reached. Wait a few minutes or try again later.",
            )
        return {"reply": reply, "bot": bot.name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _ensure_qwen_portal_config():
    """Ensure openclaw.json in state dir has qwen-portal provider so 'models auth login' can run."""
    path = Path(OPENCLAW_STATE_DIR) / "openclaw.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    gateway_token = os.environ.get("OPENCLAW_GATEWAY_TOKEN") or getattr(config, "OPENCLAW_AUTH_TOKEN", "") or ""
    cfg = {
        "auth": {"profiles": {"qwen-portal:default": {"provider": "qwen-portal", "mode": "oauth"}}},
        "models": {
            "providers": {
                "qwen-portal": {
                    "baseUrl": "https://portal.qwen.ai/v1",
                    "apiKey": "qwen-oauth",
                    "api": "openai-completions",
                    "models": [
                        {"id": "coder-model", "name": "Qwen Coder", "reasoning": False, "input": ["text"], "contextWindow": 128000, "maxTokens": 8192},
                        {"id": "vision-model", "name": "Qwen Vision", "reasoning": False, "input": ["text", "image"], "contextWindow": 128000, "maxTokens": 8192},
                    ],
                }
            }
        },
        "gateway": {
            "http": {"endpoints": {"chatCompletions": {"enabled": True}}},
            "auth": {"mode": "token", "token": gateway_token},
        },
        "agents": {
            "defaults": {"model": {"primary": "qwen-portal/coder-model"}, "workspace": f"{OPENCLAW_STATE_DIR}/workspace"},
            "list": [{"id": "main", "default": True, "model": "qwen-portal/coder-model"}],
        },
        "plugins": {"entries": {"qwen-portal-auth": {"enabled": True}}},
    }
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)


def _stream_qwen_login():
    """Run openclaw models auth login --provider qwen-portal --set-default; yield stdout line by line."""
    _ensure_qwen_portal_config()
    env = {**os.environ, "OPENCLAW_STATE_DIR": OPENCLAW_STATE_DIR}
    proc = subprocess.Popen(
        ["node", "openclaw.mjs", "models", "auth", "login", "--provider", "qwen-portal", "--set-default"],
        cwd=OPENCLAW_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    try:
        for line in iter(proc.stdout.readline, ""):
            yield line
    finally:
        proc.wait()
        # Re-apply full config so gateway and model stay correct after login (login may overwrite openclaw.json)
        _ensure_qwen_portal_config()


@app.post("/auth/qwen-portal")
def auth_qwen_portal(authorization: HTTPAuthorizationCredentials | None = Depends(security)):
    """
    Run OpenClaw Qwen OAuth device-code login in the container and stream the command output (logs).
    Open the URL shown in the response in your browser, enter the code, approve; once done, tokens are
    saved and qwen-portal/coder-model is used for /chat. Requires Authorization: Bearer <token>.
    """
    if not verify_bearer(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing Bearer token")
    if not Path(OPENCLAW_DIR).joinpath("openclaw.mjs").exists():
        raise HTTPException(status_code=503, detail="OpenClaw not available (not running in combined image)")
    return StreamingResponse(
        _stream_qwen_login(),
        media_type="text/plain; charset=utf-8",
        headers={"X-Content-Type-Options": "nosniff"},
    )
