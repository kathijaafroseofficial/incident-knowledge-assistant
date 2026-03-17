# bots/openclaw_bot.py — OpenClaw (openclaw.ai) integration — personal AI assistant gateway
# OpenClaw is the open-source evolution of Clawdbot/Moltbot; gateway runs on port 18789 by default.
# Docs: https://open-claw.bot/docs/api/gateway/ and https://clawdocs.org/reference/gateway-api/
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from .base import BotProvider
import requests
from compliance import (
    COMPLIANCE_SYSTEM_PROMPT,
    validate_input,
    validate_output,
)


class OpenClawBotProvider(BotProvider):
    """
    OpenClaw provider: talks to your local OpenClaw Gateway (openclaw.ai).
    Uses the OpenAI-compatible POST /v1/chat/completions endpoint.
    Enable in OpenClaw config: gateway.http.endpoints.chatCompletions.enabled: true
    """

    @property
    def name(self) -> str:
        return "OpenClaw"

    def chat(self, user_message: str, context: str = "") -> str:
        # Compliance: reject prompt injection / adversarial input; return fixed message
        ok, refusal = validate_input(user_message, context)
        if not ok:
            return refusal
        # Build user prompt with incident context (same pattern as other bots)
        prompt = user_message
        if context:
            prompt = (
                "Use the following error log / incident data as context. "
                "Provide clear, actionable recommended fixes.\n\n"
                f"Context:\n{context}\n\nUser question: {user_message}"
            )
        headers = {"Content-Type": "application/json"}
        # Gateway auth: Bearer token if OPENCLAW_AUTH_TOKEN is set (auth enabled in OpenClaw)
        if getattr(config, "OPENCLAW_AUTH_TOKEN", ""):
            headers["Authorization"] = f"Bearer {config.OPENCLAW_AUTH_TOKEN}"
        # Agent selection: which OpenClaw agent handles the chat (default: main)
        agent_id = getattr(config, "OPENCLAW_AGENT_ID", "main") or "main"
        headers["x-openclaw-agent-id"] = agent_id
        # System message for compliance (prompt injection, leakage, safety, edge cases)
        messages = [
            {"role": "system", "content": COMPLIANCE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        try:
            r = requests.post(
                f"{config.OPENCLAW_GATEWAY_URL.rstrip('/')}/v1/chat/completions",
                json={"model": "openclaw", "messages": messages},
                headers=headers,
                timeout=120,
            )
            r.raise_for_status()
            data = r.json()
            # OpenAI-compatible response shape
            choice = (data.get("choices") or [{}])[0]
            reply = (choice.get("message") or {}).get("content", "").strip()
            # Compliance: if output looks like leakage or bypass, do not show model output
            out_ok, out_refusal = validate_output(reply)
            if not out_ok:
                return out_refusal
            return reply
        except Exception as e:
            return (
                f"OpenClaw error: {e}. "
                "Ensure the OpenClaw Gateway is running (default port 18789) and "
                "gateway.http.endpoints.chatCompletions.enabled is true in OpenClaw config."
            )
