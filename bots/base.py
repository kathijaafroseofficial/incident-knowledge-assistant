# bots/base.py — Abstract bot interface and factory (MoltBot, ClawDBot, Nanobot, fallbacks)
from abc import ABC, abstractmethod
import sys
from pathlib import Path

# Add project root for config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


class BotProvider(ABC):
    """Abstract base for all bot providers (MoltBot, ClawDBot, Nanobot, Ollama, etc.)."""

    @abstractmethod
    def chat(self, user_message: str, context: str = "") -> str:
        """Send user message with optional context (e.g. log content); return assistant reply."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name of this provider."""
        pass


def _require_bot_config() -> None:
    """Raise with clear message when no valid 3-bot (or other) provider is configured."""
    msg = (
        "No bot configured. Set one of MOLTBOT_URL, CLAWDBOT_URL, NANOBOT_URL and ensure BOT_PROVIDER "
        "matches (moltbot | clawdbot | nanobot), or set BOT_PROVIDER=auto to use the first available. "
        "For local testing run: python scripts/mock_bot_server.py"
    )
    raise RuntimeError(msg)


def get_bot() -> BotProvider:
    """
    Factory: returns the configured bot. Production default is first available of
    MoltBot / ClawDBot / Nanobot (by URL). No Ollama fallback unless BOT_PROVIDER=ollama.
    """
    provider = (config.BOT_PROVIDER or "").strip() or config._first_available_giggso_bot()
    # Giggso 3 bots (production primary)
    if provider == "moltbot":
        if not config.MOLTBOT_URL:
            raise RuntimeError("BOT_PROVIDER=moltbot but MOLTBOT_URL is not set. Set MOLTBOT_URL in .env or environment.")
        from .moltbot import MoltBotProvider
        return MoltBotProvider()
    if provider == "clawdbot":
        if not config.CLAWDBOT_URL:
            raise RuntimeError("BOT_PROVIDER=clawdbot but CLAWDBOT_URL is not set. Set CLAWDBOT_URL in .env or environment.")
        from .clawdbot import ClawDBotProvider
        return ClawDBotProvider()
    if provider == "nanobot":
        if not config.NANOBOT_URL:
            raise RuntimeError("BOT_PROVIDER=nanobot but NANOBOT_URL is not set. Set NANOBOT_URL in .env or environment.")
        from .nanobot import NanobotProvider
        return NanobotProvider()
    # Other backends (optional)
    if provider == "ollama":
        from .ollama_bot import OllamaBotProvider
        return OllamaBotProvider()
    if provider == "openclaw":
        from .openclaw_bot import OpenClawBotProvider
        return OpenClawBotProvider()
    if provider == "openai_compatible" and config.OPENAI_COMPATIBLE_URL:
        from .openai_compatible import OpenAICompatibleProvider
        return OpenAICompatibleProvider()
    # No valid provider: fail with clear message (no silent Ollama fallback)
    _require_bot_config()


def get_available_bots() -> list[tuple[str, BotProvider]]:
    """
    Returns all bots that are configured (for multi-bot mode). Production: only the 3 bots
    (MoltBot, ClawDBot, Nanobot) when INCLUDE_FALLBACK_BOTS_IN_MULTI is false.
    """
    out: list[tuple[str, BotProvider]] = []
    # Always include the 3 Giggso-style bots when their URL is set
    if config.MOLTBOT_URL:
        from .moltbot import MoltBotProvider
        out.append(("MoltBot", MoltBotProvider()))
    if config.CLAWDBOT_URL:
        from .clawdbot import ClawDBotProvider
        out.append(("ClawDBot", ClawDBotProvider()))
    if config.NANOBOT_URL:
        from .nanobot import NanobotProvider
        out.append(("Nanobot", NanobotProvider()))
    # Optional fallbacks (only when explicitly enabled for multi-bot)
    if getattr(config, "INCLUDE_FALLBACK_BOTS_IN_MULTI", False):
        if getattr(config, "OPENCLAW_GATEWAY_URL", ""):
            from .openclaw_bot import OpenClawBotProvider
            out.append(("OpenClaw", OpenClawBotProvider()))
        from .ollama_bot import OllamaBotProvider
        out.append(("Ollama", OllamaBotProvider()))
        if config.OPENAI_COMPATIBLE_URL:
            from .openai_compatible import OpenAICompatibleProvider
            out.append(("OpenAI-compatible", OpenAICompatibleProvider()))
    return out
