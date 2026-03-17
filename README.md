# Incident Knowledge Assistant — Giggso Build–Break Challenge (PS1)

A **Python-based** bot that processes incident descriptions (error logs) and provides **recommended fixes**. Built for the Build–Break Challenge with **dual-input** (upload/paste log), **chat interface**, **voice assistance**, and mandatory support for **MoltBot, ClawDBot, or Nanobot**.

---

## Features

- **Dual-input architecture**: Upload a log file **or** paste raw log/JSON; you can **swap or update** the input source at any time during the session.
- **Chat interface**: Ask questions about the incident and get recommended fixes in plain language.
- **Voice-based assistance**: Use the microphone for speech-to-text (open-source: SpeechRecognition + Google Web API) and optional text-to-speech (gTTS).
- **Mandatory bot integration**: Supports **MoltBot**, **ClawDBot**, or **Nanobot** (when URLs are provided); open-source fallback via **Ollama** or any **OpenAI-compatible** API.
- **Public POST endpoint**: Exposed API with **Bearer token** authentication (`Authorization: Bearer <token>`).

---

## Tech Stack (all open-source where applicable)

| Component        | Choice                                      |
|-----------------|---------------------------------------------|
| Frontend        | **Streamlit** (embedded HTML/CSS)           |
| API             | **FastAPI** + **Uvicorn**                   |
| Bots            | MoltBot / ClawDBot / Nanobot + **Ollama**   |
| Voice STT       | **SpeechRecognition** + Google (free)       |
| Voice TTS       | **gTTS** (Google TTS)                       |
| Config          | **python-dotenv**                           |

---

## Free public deployment (no cloud infra)

You can make the app and the **POST API** publicly available for free:

- **POST /chat API (public):** Deploy the API to **[Render](https://render.com)** or **[Railway](https://railway.app)** (free tier). Use the repo’s `render.yaml` or set start command `uvicorn api_server:app --host 0.0.0.0 --port $PORT` and add env vars (`API_BEARER_TOKEN`, `BOT_PROVIDER`, `OPENAI_COMPATIBLE_*`). You get a public URL like `https://your-api.onrender.com/chat` and `/docs`.
- **Streamlit UI:** **[Streamlit Community Cloud](https://share.streamlit.io)** or **[Hugging Face Spaces](https://huggingface.co/spaces)** — deploy `app.py` and set Secrets for a free LLM (e.g. Groq, OpenRouter).

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step instructions, env vars, and curl examples.

---

## Quick Start

### 1. Clone / unzip and install

```bash
cd incident-knowledge-assistant
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### 2. Configure environment

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS
```

Edit `.env`:

- `API_BEARER_TOKEN` — Set a secure token for the public POST endpoint.
- `BOT_PROVIDER` — One of: `moltbot`, `clawdbot`, `nanobot`, `openclaw`, `ollama`, `openai_compatible`.
- If using **MoltBot / ClawDBot / Nanobot**: set the corresponding `*_URL` (e.g. `MOLTBOT_URL=https://...`).
- If using **OpenClaw** ([openclaw.ai](https://openclaw.ai)): install OpenClaw (`npm i -g openclaw`, then `openclaw onboard`), enable the chat completions endpoint in OpenClaw config, then set `BOT_PROVIDER=openclaw`. Optional: `OPENCLAW_GATEWAY_URL` (default `http://localhost:18789`), `OPENCLAW_AUTH_TOKEN`, `OPENCLAW_AGENT_ID` (default `main`).
- If using **Ollama** (default): install [Ollama](https://ollama.ai) and run e.g. `ollama run llama3.2`; set `OLLAMA_BASE_URL` if different.

**Testing without Giggso URLs:** Run the local mock server, then point one of the bot URLs at it:

```bash
python scripts/mock_bot_server.py
```

In `.env` set e.g. `BOT_PROVIDER=clawdbot` and `CLAWDBOT_URL=http://localhost:9090/clawdbot`. Test URLs: `http://localhost:9090/moltbot`, `http://localhost:9090/clawdbot`, `http://localhost:9090/nanobot`.

**OpenClaw (Clawbot) integration** — [OpenClaw](https://openclaw.ai) is the open-source personal AI assistant (formerly Clawdbot/Moltbot). To use it as a bot backend:

1. Install OpenClaw: `npm i -g openclaw` (or use the [install script](https://openclaw.ai/)).
2. Run `openclaw onboard` and complete setup.
3. In your OpenClaw config (e.g. `~/.openclaw/config.yml`), enable the HTTP chat completions endpoint:
   ```yaml
   gateway:
     http:
       endpoints:
         chatCompletions:
           enabled: true
   ```
4. In this app’s `.env`: set `BOT_PROVIDER=openclaw`. Optionally set `OPENCLAW_GATEWAY_URL` (default `http://localhost:18789`), `OPENCLAW_AUTH_TOKEN` if you enabled gateway auth, and `OPENCLAW_AGENT_ID` (default `main`).

The app sends incident context and your question to the OpenClaw Gateway via its OpenAI-compatible `/v1/chat/completions` endpoint.

**Hackathon / personal use (no Giggso URLs)** — Use free, real backends for real-time multi-bot demos:

| Option | What to do | Real-time? |
|--------|------------|------------|
| **Ollama** | Install [Ollama](https://ollama.ai), run `ollama run llama3.2`. Set `BOT_PROVIDER=ollama`. | Yes, local. |
| **Mock “3 bots”** | Run `python scripts/mock_bot_server.py`. In `.env` set `MOLTBOT_URL=http://localhost:9090/moltbot`, `CLAWDBOT_URL=http://localhost:9090/clawdbot`, `NANOBOT_URL=http://localhost:9090/nanobot`. | Yes, local mock. |
| **Multi-bot mode** | Set `MULTI_BOT_ENABLED=true` in `.env`. The app will call **every** configured backend (Ollama + mock URLs + OpenAI-compatible) and show each reply. Great for hackathon demos. | Yes. |
| **OpenClaw** | Install [OpenClaw](https://openclaw.ai) (`npm i -g openclaw`, `openclaw onboard`). Enable `gateway.http.endpoints.chatCompletions.enabled: true` in OpenClaw config. Set `BOT_PROVIDER=openclaw`. Gateway runs on port 18789. | Yes, local. |
| **Free cloud LLM** | Use an OpenAI-compatible API (e.g. [Groq](https://console.groq.com) free tier, [OpenRouter](https://openrouter.ai) free models). Set `OPENAI_COMPATIBLE_URL`, `OPENAI_COMPATIBLE_API_KEY`, `BOT_PROVIDER=openai_compatible`. | Yes, over internet. |

**Example: multiple bots at once (no Giggso).** In one terminal run the mock server; in `.env` set:

```
BOT_PROVIDER=ollama
MULTI_BOT_ENABLED=true
CLAWDBOT_URL=http://localhost:9090/clawdbot
```

Start Ollama (`ollama run llama3.2`). Then run the app: each question goes to **Ollama + ClawDBot (mock)** and you see both answers in real time.

**How you get these URLs in real-time / production**

- **Giggso-hosted**: When you have access to Giggso’s MoltBot/ClawDBot/Nanobot, they provide the base URLs (e.g. `https://api.giggso.com/moltbot`) via their dashboard, API docs, or support. You set them once in your environment.
- **Your deployment**: In production you don’t “fetch” URLs at runtime — you **configure** them where the app runs:
  - **Env vars**: Set `MOLTBOT_URL`, `CLAWDBOT_URL`, `NANOBOT_URL` in `.env` (local) or in your host’s environment (systemd, Docker, etc.).
  - **Cloud / Kubernetes**: Inject the same variables from a secrets manager (e.g. AWS Secrets Manager, Azure Key Vault, HashiCorp Vault) or from Kubernetes Secrets/ConfigMaps when the container starts.
  - **CI/CD**: Your pipeline (GitHub Actions, GitLab CI, etc.) can write a `.env` or set env vars from stored secrets before starting the app.
- **Self-hosted / open-source**: If you run your own Moltbot/ClawdBot instance (e.g. Moltbot on `http://localhost:18789` or your server), use that base URL (e.g. `MOLTBOT_URL=http://your-server:18789`) in the same way.

The app reads these URLs from the environment at startup; there is no runtime “discovery” of URLs — you configure them where the app is deployed.

**Production deployment with the 3 bots (MoltBot / ClawDBot / Nanobot)**

- **No Ollama default** — The app uses the first available of the three bots when `BOT_PROVIDER=auto` (or when unset). If none of `MOLTBOT_URL`, `CLAWDBOT_URL`, `NANOBOT_URL` is set, the app fails at startup with a clear error (API server) or shows the error in the UI (Streamlit).
- **Single bot** — Set exactly one URL (e.g. `CLAWDBOT_URL=https://your-gateway/clawdbot`) and `BOT_PROVIDER=clawdbot` (or `auto`). The chatbot uses that bot in real time.
- **Multi-bot** — Set all three URLs and `MULTI_BOT_ENABLED=true` to send each message to every configured bot and show each reply. For production multi-bot, only the 3 bots are used unless you set `INCLUDE_FALLBACK_BOTS_IN_MULTI=true`.
- **Realtime in production** — Inject env vars when the container/process starts (e.g. Kubernetes Secret to env, or `.env` on the host). The API server runs `validate_bot_config()` on startup and will not start if no bot URL is set.

Example production env (single bot): set `API_BEARER_TOKEN`, `BOT_PROVIDER=clawdbot`, `CLAWDBOT_URL=https://api.your-company.com/clawdbot`. Example local testing (mock): set `BOT_PROVIDER=auto`, `CLAWDBOT_URL=http://localhost:9090/clawdbot` and run `python scripts/mock_bot_server.py` in another terminal.

### 3. Run the app

**Streamlit UI (default port 8501):**

```bash
streamlit run app.py
```

**API server (for public POST endpoint):**

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### 4. Use the UI

1. Open **Upload log file** or **Paste log text** and provide your error log (or use `sample_error.log`).
2. Optionally **swap** the source later by uploading another file or pasting again and clicking **Use pasted text as source**.
3. Type or use **Voice input** to ask questions (e.g. “What’s causing the NullPointerException?” or “How do I fix the database connection?”).
4. Read the assistant’s recommended fixes; you can play TTS if available.

### 5. Call the public POST endpoint

```bash
curl -X POST https://your-host/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is the root cause?\", \"context\": \"ERROR NullPointerException at PaymentService.process\"}"
```

Response:

```json
{ "reply": "...", "bot": "Ollama" }
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Streamlit (app.py)                                              │
│  • Dual input: file upload + paste (dynamic swap)                │
│  • Chat UI + embedded HTML/CSS                                   │
│  • Voice: STT (SpeechRecognition) → chat; TTS (gTTS) for replies │
└──────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  bots/ (BotProvider)                                             │
│  • MoltBot / ClawDBot / Nanobot (when URL set)                   │
│  • OpenClaw (openclaw.ai gateway, port 18789)                     │
│  • Ollama (default) / OpenAI-compatible (fallback)                │
└──────────────────────────────┬──────────────────────────────────┘
                                │
┌───────────────────────────────┴──────────────────────────────────┐
│  FastAPI (api_server.py)                                          │
│  • POST /chat — Bearer token auth                                  │
│  • Same bot backend as Streamlit                                  │
└──────────────────────────────────────────────────────────────────┘
```

- **config.py**: Loads `.env`; selects bot provider and URLs.
- **voice_utils.py**: `listen_and_transcribe()` (STT), `text_to_speech_audio()` (TTS).
- **Bot implementations**: `bots/moltbot.py`, `bots/clawdbot.py`, `bots/nanobot.py`, `bots/openclaw_bot.py`, `bots/ollama_bot.py`, `bots/openai_compatible.py`.

---

## Assumptions

- **MoltBot / ClawDBot / Nanobot**: Assumed to expose a `POST .../chat` with JSON `{ "message": "...", "context": "..." }` and a response field among `reply`, `text`, or `response`. If Giggso provides a different contract, only the corresponding `bots/*.py` file needs to be updated.
- **Voice**: Microphone and internet are available for Google STT; TTS uses gTTS (internet). No API keys required for default STT/TTS.
- **Log format**: Any text or JSON; the bot receives it as a single context string.

---

## Limitations

- Voice input is fixed to ~10 seconds per recording; no streaming STT.
- Bot response format for MoltBot/ClawDBot/Nanobot is assumed; real APIs may require small adapter changes.
- Public POST endpoint must be exposed (e.g. via cloud/ngrok) and protected only by Bearer token; consider rate limiting and HTTPS in production.

---

## Phase 1 Deliverables Checklist

- [x] **Source code**: This repository (zip and submit).
- [x] **README**: Usage, architecture, assumptions, limitations (this file).
- [ ] **Demonstration video**: Recording of the app running (to be submitted separately).
- [x] **Public POST endpoint**: `/chat` with `Authorization: Bearer <token>` (deploy and expose as required).

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE). You can use, modify, and distribute it freely (including for commercial use). Open-source dependencies (Streamlit, FastAPI, etc.) are used under their respective licenses.
