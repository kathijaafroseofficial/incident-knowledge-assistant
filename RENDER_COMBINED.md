# Deploy API + OpenClaw in one Render service (no second app)

This deploys the **Incident Knowledge API** and **OpenClaw gateway** in a **single** Render Web Service. One URL for your API; OpenClaw runs inside the same container and is used at `http://127.0.0.1:3000`.

## When to use this

- You want **one** Render service (one URL, one billable service).
- You're okay with a **longer first build** (OpenClaw is built from source in the image; can take 10–20 minutes).
- You want the API to use **OpenClaw** as the bot (same as when you run locally with OpenClaw).

## Steps on Render

1. **New Web Service** → connect your **incident-knowledge-assistant** GitHub repo.

2. **Settings:**
   - **Environment:** Docker  
   - **Dockerfile path:** `Dockerfile.combined`  
   - **Docker context:** (leave default, repo root)  
   - **Plan:** Free (or your chosen plan)

3. **Environment variables** — In Render: open your Docker service → **Environment** (left sidebar) → Add each key below. Use the exact values in the “Value” column.

   **Required:** API auth + gateway (same for all)

   | Key | Value (what to set) |
   |-----|----------------------|
   | `API_BEARER_TOKEN` | A secret you create (e.g. [randomkeygen.com](https://randomkeygen.com)). For `Authorization: Bearer <token>` on `POST /chat`. |
   | `BOT_PROVIDER` | `openclaw` |
   | `OPENCLAW_GATEWAY_URL` | `http://127.0.0.1:3000` |
   | `OPENCLAW_GATEWAY_TOKEN` | A secret you create (gateway auth). |
   | `OPENCLAW_AUTH_TOKEN` | **Same value** as `OPENCLAW_GATEWAY_TOKEN` |

   **Model — free Groq (no paid key):**

   | Key | Value (what to set) |
   |-----|----------------------|
   | `GROQ_API_KEY` | Free key from [console.groq.com](https://console.groq.com). Default model is **Llama 3.1 8B** (higher free limits). |

   **Model — optional (Claude):** Only if you prefer Claude over Qwen: set `ANTHROPIC_API_KEY` (from [console.anthropic.com](https://console.anthropic.com)). If both `GROQ_API_KEY` and `ANTHROPIC_API_KEY` are set, Groq (Qwen) is used.

   **Optional:** `OPENCLAW_DEFAULT_MODEL` — default is `groq/llama-3.1-8b-instant`. Use `groq/qwen/qwen3-32b` for Qwen, or `anthropic/claude-3-5-sonnet-latest` for Claude. `OPENCLAW_AGENT_ID` = `main` (default).  
   **Do not set:** `PORT` — Render sets it automatically.

   **If you see "API rate limit reached":** The default is now Llama 3.1 8B (higher free limits). If you set `OPENCLAW_DEFAULT_MODEL=groq/qwen/qwen3-32b`, Qwen has a lower quota (1,000 req/day); wait and retry or remove that env to use Llama.

   **Sample (copy and replace placeholders in Render → Environment):**

   ```
   API_BEARER_TOKEN=your-secret-for-post-chat-min-32-chars
   BOT_PROVIDER=openclaw
   OPENCLAW_GATEWAY_URL=http://127.0.0.1:3000
   OPENCLAW_GATEWAY_TOKEN=your-gateway-secret-same-as-below
   OPENCLAW_AUTH_TOKEN=your-gateway-secret-same-as-above
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   Replace `your-secret-for-post-chat-min-32-chars` and `your-gateway-secret-same-as-above` with your own random strings (e.g. from [randomkeygen.com](https://randomkeygen.com)). Use the **same** value for `OPENCLAW_GATEWAY_TOKEN` and `OPENCLAW_AUTH_TOKEN`. Get `GROQ_API_KEY` at [console.groq.com](https://console.groq.com).

4. **Advanced → Start Command:** leave empty (the image uses `ENTRYPOINT`).

5. **Create Web Service.** The first build can take 10–20 minutes (building OpenClaw). Later deploys are faster if the cache is reused.

6. When it’s live, your **API** is at `https://<your-service>.onrender.com` (e.g. `POST /chat`, `GET /docs`). OpenClaw is **not** exposed publicly; only the API is.

## Summary

- **One Render app** = API + OpenClaw in one container.
- **Public URL** = your API only (`/chat`, `/docs`).
- **OpenClaw** runs on port 3000 inside the container; the API calls it at `http://127.0.0.1:3000`.
- No second Render service and no separate OpenClaw URL to manage.

**Build note:** The image skips OpenClaw's web UI build to avoid TypeScript errors in Docker. The gateway and `/v1/chat/completions` work; the in-browser Control UI is not included.

## If the build fails (OOM or timeout)

Render’s free tier has limited memory. If the OpenClaw build fails:

1. Use **two services** instead: one for the API (current repo, `requirements-api.txt`), one for OpenClaw (e.g. from [openclaw/openclaw](https://github.com/openclaw/openclaw) with its Dockerfile), and set `OPENCLAW_GATEWAY_URL` to the second service’s URL.
2. Or use **Groq** on a single API service: set `BOT_PROVIDER=openai_compatible`, `OPENAI_COMPATIBLE_URL`, `OPENAI_COMPATIBLE_API_KEY` and do not use the combined Dockerfile.
