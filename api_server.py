# api_server.py — Public POST endpoint with Bearer token auth (Challenge requirement)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
from bots import get_bot

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
        return {"reply": reply, "bot": bot.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
