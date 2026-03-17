# Giggso Incident Bot

A **Python-based** incident assistant that takes error logs (upload or paste) and returns **recommended fixes** via chat. It includes a **Streamlit UI** (Giggso Incident Bot), a **public REST API** with Bearer auth, **compliance checks** (prompt injection, leakage, safety), and optional **voice input**. The default backend is **OpenClaw** with **OpenAI** (e.g. GPT-5-nano).

---

## Features

- **Giggso Incident Bot UI** — Streamlit chat with incident context (upload file or paste log), prompt box, and highlighted **voice input**.
- **Dual input** — Upload a log file or paste raw log/JSON; you can change the source anytime.
- **Compliance** — Input validation (prompt injection / adversarial patterns), system prompt for safe behavior, and output checks (no leakage). Non-compliant requests get fixed refusal messages.
- **OpenClaw + OpenAI** — OpenClaw gateway with OpenAI models (default `openai/gpt-5-nano`). One combined Docker image runs both API and OpenClaw.
- **Public API** — `POST /chat` with `Authorization: Bearer <token>`; same bot and compliance as the UI.
- **Voice** — Optional speech-to-text (SpeechRecognition + Google) and text-to-speech (gTTS) in the UI.
- **Other backends** — Optional: MoltBot/ClawDBot/Nanobot (URLs), Ollama, or any OpenAI-compatible API (e.g. Groq, OpenRouter).

---

## Tech stack

| Component   | Choice                          |
|------------|-----------------------------------|
| Frontend   | **Streamlit** (Giggso Incident Bot UI) |
| API        | **FastAPI** + **Uvicorn**        |
| Default bot| **OpenClaw** + **OpenAI**        |
| Compliance | **compliance.py** (input/output + system prompt) |
| Voice STT  | **SpeechRecognition** + Google   |
| Voice TTS  | **gTTS**                        |
| Config     | **python-dotenv** (`.env`)       |

---

## Quick start (local)

### 1. Clone and install

```bash
cd incident-knowledge-assistant
python -m venv venv
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD): venv\Scripts\activate.bat
# Linux/macOS:   source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment

```bash
copy .env.example .env   # Windows
# cp .env.example .env    # Linux/macOS
```

Edit `.env`:

- **OpenClaw + OpenAI (recommended):**  
  `BOT_PROVIDER=openclaw`  
  `OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789` (or `3000` if you run OpenClaw on 3000)  
  Set `OPENCLAW_AUTH_TOKEN` if your OpenClaw gateway uses auth.  
  OpenClaw reads `OPENAI_API_KEY` from the environment for the default model.

- **API auth:**  
  `API_BEARER_TOKEN` — used for `Authorization: Bearer <token>` on `POST /chat`.

- **Other bots:**  
  For MoltBot/ClawDBot/Nanobot set the corresponding `*_URL` and `BOT_PROVIDER`.  
  For Ollama: `BOT_PROVIDER=ollama`, run `ollama run llama3.2`.  
  For OpenAI-compatible (Groq/OpenRouter): `BOT_PROVIDER=openai_compatible`, `OPENAI_COMPATIBLE_URL`, `OPENAI_COMPATIBLE_API_KEY`.

### 3. Run OpenClaw (if using OpenClaw backend)

Install and run OpenClaw locally (e.g. `npm i -g openclaw`, `openclaw onboard`), enable the chat completions endpoint in config, and start the gateway (default port 18789 or 3000). See [OpenClaw docs](https://openclaw.ai).

### 4. Run the app

**Streamlit UI (Giggso Incident Bot):**

```bash
python -m streamlit run app.py
```

Open http://localhost:8501. Use the prompt box or chat input to send messages; use **Voice input** for speech-to-text.

**API server (optional, e.g. port 8000):**

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

---

## Deployment (Render — one service)

Deploy the **API and OpenClaw in a single container** (OpenAI only, no Groq/Qwen in the image):

1. **Render** → New Web Service → Connect repo.
2. **Settings:** Environment = Docker, Dockerfile = `Dockerfile.combined`.
3. **Environment variables:**

   | Key | Value |
   |-----|--------|
   | `API_BEARER_TOKEN` | Your secret (for `Authorization: Bearer`) |
   | `BOT_PROVIDER` | `openclaw` |
   | `OPENCLAW_GATEWAY_URL` | `http://127.0.0.1:3000` |
   | `OPENCLAW_GATEWAY_TOKEN` | Your gateway secret |
   | `OPENCLAW_AUTH_TOKEN` | Same as `OPENCLAW_GATEWAY_TOKEN` |
   | `OPENAI_API_KEY` | Your OpenAI API key |

   Optional: `OPENCLAW_DEFAULT_MODEL` (e.g. `openai/gpt-4o-mini`).

4. Create the service. First build can take 10–20 minutes (OpenClaw built from source).  
5. API base URL: `https://<your-service>.onrender.com` → `POST /chat`, `GET /docs`.

See **[RENDER_COMBINED.md](RENDER_COMBINED.md)** for full steps, memory/512MB notes, and troubleshooting.

---

## API usage

**POST /chat**

```bash
curl -X POST https://your-api.onrender.com/chat \
  -H "Authorization: Bearer YOUR_API_BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the root cause?", "context": "ERROR NullPointerException at PaymentService.process"}'
```

Response:

```json
{ "reply": "...", "bot": "OpenClaw" }
```

- **401** — Missing or invalid Bearer token.  
- **429** — Rate limit (e.g. from OpenAI); retry later.  
- **500** — Server or bot error (see `detail`).

Compliance is applied in the same way as in the UI: input/output checks and system prompt.

---

## Project structure

```
incident-knowledge-assistant/
├── app.py              # Streamlit UI (Giggso Incident Bot)
├── api_server.py       # FastAPI app: POST /chat, GET /docs
├── config.py            # Env and bot provider selection
├── compliance.py        # Input/output validation + system prompt
├── voice_utils.py       # STT / TTS helpers
├── bots/
│   ├── base.py         # BotProvider, get_bot()
│   ├── openclaw_bot.py # OpenClaw + compliance
│   ├── openai_compatible.py
│   ├── ollama_bot.py
│   └── ...
├── Dockerfile.combined  # API + OpenClaw (OpenAI) single image
├── start-combined.sh   # Start OpenClaw gateway then uvicorn
├── requirements.txt    # Full app (Streamlit + API)
├── requirements-api.txt # API only (e.g. Render combined)
├── .env.example
├── RENDER_COMBINED.md  # Render deploy details
└── DEPLOYMENT.md       # Other deployment options
```

---

## Compliance

The **OpenClaw bot** (used by both the UI and the API) applies:

- **Input:** Rejects messages that look like prompt injection or manipulation (e.g. “ignore previous instructions”, “reveal system prompt”) and returns a fixed refusal.
- **System prompt:** Instructs the model to avoid role changes, hallucination, data leakage, and safety bypass.
- **Output:** If the model reply looks like leakage or bypass, it is replaced with a generic compliance message so the model’s text is not shown.

See **compliance.py** for patterns and messages.

---

## Configuration summary

| Variable | Purpose |
|----------|---------|
| `API_BEARER_TOKEN` | Auth for `POST /chat`. |
| `BOT_PROVIDER` | `openclaw` \| `ollama` \| `openai_compatible` \| `moltbot` \| `clawdbot` \| `nanobot` \| `auto`. |
| `OPENCLAW_GATEWAY_URL` | OpenClaw gateway URL (e.g. `http://127.0.0.1:18789` or `http://127.0.0.1:3000` in Docker). |
| `OPENCLAW_AUTH_TOKEN` | Gateway Bearer token (if enabled). |
| `OPENCLAW_AGENT_ID` | Agent id (default `main`). |
| `OPENAI_API_KEY` | Used by OpenClaw for default OpenAI model. |
| `OPENCLAW_DEFAULT_MODEL` | Override model (e.g. `openai/gpt-4o-mini`). |
| `OPENAI_COMPATIBLE_URL` / `OPENAI_COMPATIBLE_API_KEY` | For `BOT_PROVIDER=openai_compatible`. |

---

## License

MIT — see [LICENSE](LICENSE).
