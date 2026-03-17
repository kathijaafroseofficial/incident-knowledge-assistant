# Free Public Deployment (No Cloud Infra Required)

This project is **free and open source** (MIT License). You can make it publicly available at no cost using the following **free hosting** options—no AWS/GCP/Azure or paid cloud needed.

---

## Deploy the POST API publicly (free)

The **POST /chat** endpoint can be exposed on the internet at no cost using Render’s free tier (or Railway). No cloud account or infra is required beyond signing up and connecting your repo.

### Render (recommended for API)

1. **Push this repo to GitHub** (if not already).
2. Go to [render.com](https://render.com) and sign in (e.g. with GitHub).
3. **New → Web Service** → connect your GitHub repo and select this repository.
4. **Configure:**
   - **Name:** e.g. `incident-knowledge-api`
   - **Runtime:** Python
   - **Build command:** `pip install -r requirements-api.txt` (use `requirements-api.txt` to avoid building PyAudio/voice libs on the server)
   - **Start command:** `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
5. **Environment variables** (required; add in the Render dashboard):
   - `API_BEARER_TOKEN` — Set a strong random token (e.g. generate with `openssl rand -hex 24`). Clients must send `Authorization: Bearer <this_token>`.
   - `BOT_PROVIDER` — `openai_compatible`
   - `OPENAI_COMPATIBLE_URL` — e.g. `https://api.groq.com/openai/v1` (Groq free tier) or `https://openrouter.ai/api/v1` (OpenRouter).
   - `OPENAI_COMPATIBLE_API_KEY` — Your API key (Groq or OpenRouter). Mark as **Secret** in Render.
6. Click **Create Web Service**. Render will build and deploy; your API will be at `https://<your-service-name>.onrender.com`.
7. **Test:**
   ```bash
   curl -X POST https://<your-service-name>.onrender.com/chat \
     -H "Authorization: Bearer YOUR_API_BEARER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "What causes a NullPointerException?", "context": "ERROR at PaymentService.process"}'
   ```
   Open `https://<your-service-name>.onrender.com/docs` for interactive Swagger UI.

**One-click from repo:** If your repo has a `render.yaml` (this project does), you can use **Render Dashboard → New → Blueprint** and select the repo; then add the environment variables above in the service’s **Environment** tab.

### Railway (alternative)

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. **New Project** → **Deploy from GitHub repo** → select this repo.
3. Railway will detect the app. Set **Start Command** to: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
4. In **Variables**, add the same keys as above: `API_BEARER_TOKEN`, `BOT_PROVIDER`, `OPENAI_COMPATIBLE_URL`, `OPENAI_COMPATIBLE_API_KEY`.
5. Deploy; use the generated public URL (e.g. `https://your-app.up.railway.app`) for **POST /chat** and **/docs**.

### Notes

- Free tiers may spin down after inactivity; the first request after idle can be slow (cold start).
- Keep `API_BEARER_TOKEN` secret and only share it with trusted clients or your own frontend.
- For a public **UI** as well, deploy the Streamlit app separately (Option 1 or 2 below); the UI can call your deployed API if you add an optional “API URL + token” setting later.

---

## Use OpenClaw with the API on Render (deploy OpenClaw for free)

Your API on Render runs in the **cloud**. It cannot reach `127.0.0.1:18789` — that is your own PC. You have two choices:

### Option A: One Render app with API + OpenClaw (no second service)

Deploy **both** the Incident Knowledge API and OpenClaw in a **single** Render Web Service. OpenClaw runs inside the same container on port 3000; the API listens on `$PORT` and calls OpenClaw at `http://127.0.0.1:3000`. One URL, one service.

See **[RENDER_COMBINED.md](RENDER_COMBINED.md)** for steps: use **Dockerfile.combined**, set env vars (`BOT_PROVIDER=openclaw`, `OPENCLAW_GATEWAY_URL=http://127.0.0.1:3000`, `OPENCLAW_GATEWAY_TOKEN`, `OPENCLAW_AUTH_TOKEN`, `ANTHROPIC_API_KEY`). First build can take 10–20 min (OpenClaw built from source).

### Option B: Use a cloud LLM on Render (easiest, no OpenClaw)

Don't use OpenClaw for the **deployed** API. On Render set:

- `BOT_PROVIDER` = `openai_compatible`
- `OPENAI_COMPATIBLE_URL` = `https://api.groq.com/openai/v1` (or OpenRouter)
- `OPENAI_COMPATIBLE_API_KEY` = your key

Then the API talks to Groq/OpenRouter from the cloud. No OpenClaw deployment needed. Use OpenClaw only when running the app **locally**.

### Option C: Deploy OpenClaw on Fly.io (free tier), then point Render at it

Deploy the OpenClaw gateway to **Fly.io** so it has a **public URL**. Then in Render set `BOT_PROVIDER=openclaw` and `OPENCLAW_GATEWAY_URL=https://your-openclaw-app.fly.dev`.

**1. Install Fly CLI and log in:** [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl/) then `fly auth login` (Fly free tier may require a card on file).

**2. Clone OpenClaw and create the app:**

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
fly apps create my-openclaw
fly volumes create openclaw_data --size 1 --region iad
```

**3. Configure `fly.toml`** in the openclaw repo (use at least 2GB RAM). See [OpenClaw Fly.io docs](https://open-claw.bot/docs/deployment/docker). Key: `processes.app` = `node dist/index.js gateway --allow-unconfigured --port 3000 --bind lan`, and `[http_service]` with `internal_port = 3000`, `force_https = true`, plus `[mounts]` for `/data`.

**4. Set Fly secrets:** `fly secrets set OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)` and add your model API keys (e.g. ANTHROPIC_API_KEY).

**5. Deploy:** `fly deploy`. Then `fly ssh console` and create `/data/openclaw.json` with **chat completions enabled** and the same gateway token:

```json
{
  "gateway": {
    "http": { "endpoints": { "chatCompletions": { "enabled": true } } },
    "auth": { "mode": "token", "token": "SAME_AS_OPENCLAW_GATEWAY_TOKEN" }
  },
  "agents": { "defaults": { "model": { "primary": "anthropic/claude-3-5-sonnet-latest" } }, "list": [{ "id": "main", "default": true }] }
}
```

Then `exit` and `fly machine restart --all`.

**6. Public URL:** `https://my-openclaw.fly.dev` (replace with your app name).

**7. In Render → Environment:** Set `BOT_PROVIDER=openclaw`, `OPENCLAW_GATEWAY_URL=https://my-openclaw.fly.dev`, `OPENCLAW_AUTH_TOKEN` = same token as above. Redeploy.

### Option B (alternatives): Other free hosts for a public OpenClaw URL

If Fly.io is not an option (e.g. account verification or region), you can host OpenClaw on one of these **free** platforms to get a public URL. Then set that URL in Render as `OPENCLAW_GATEWAY_URL` and use the same token for `OPENCLAW_AUTH_TOKEN`.

| Platform | Free tier | Notes |
|----------|-----------|--------|
| **Render (2nd service)** | Free web service (750 hrs/month) | Deploy OpenClaw from [openclaw/openclaw](https://github.com/openclaw/openclaw) as a **Docker** Web Service on the same Render account. No persistent disk on free tier — use a start command that writes `openclaw.json` from env vars into the state dir before starting the gateway (see below). |
| **Koyeb** | 2 free services | [koyeb.com](https://www.koyeb.com) — Deploy from GitHub or Docker image. Free tier does not attach persistent volumes; same “config from env at startup” approach as Render. |
| **Oracle Cloud Free Tier** | Always-free VM(s) | [cloud.oracle.com](https://www.oracle.com/cloud/free/) — Create an always-free VM (e.g. Ubuntu), SSH in, install Docker, clone OpenClaw, run with a volume for `/data`. Full control; no charge if you stay within free limits. |
| **Railway** | Limited free credit | [railway.app](https://railway.app) — Can run Docker; free trial credit, then pay-as-you-go. |
| **Google Cloud Run** | Free request quota | [cloud.google.com/run](https://cloud.google.com/run) — Free tier by requests; good if you can run OpenClaw in a request-scoped way. |

**Render as the second service (OpenClaw on Render):**

1. In the same Render dashboard, click **New → Web Service**.
2. Connect the **openclaw/openclaw** GitHub repo (or your fork). Choose **Docker** as the environment.
3. **Build:** Docker (use repo’s Dockerfile). **Start command:** the gateway must listen on `$PORT`; the OpenClaw Dockerfile may expect port 3000, so set **Start Command** to something like:  
   `node dist/index.js gateway --allow-unconfigured --port ${PORT} --bind 0.0.0.0`  
   (Render sets `PORT`; use it and bind to `0.0.0.0`.)
4. **Environment variables:**  
   `OPENCLAW_STATE_DIR=/data`  
   `OPENCLAW_GATEWAY_TOKEN` = your token (same one you’ll use in Render’s API service).  
   Add your model key (e.g. `ANTHROPIC_API_KEY`).  
   Because the free instance has **ephemeral disk**, you need the config to be recreated on each start. Either:
   - Use a **custom start script** that writes `/data/openclaw.json` (with `gateway.http.endpoints.chatCompletions.enabled: true` and `gateway.auth.token`) from env vars, then runs the gateway; or  
   - Rely on OpenClaw’s `--allow-unconfigured` and any env-based config it supports, then add the minimal JSON via a build step or script.
5. After deploy, your OpenClaw URL will be like `https://your-openclaw-service.onrender.com`. In your **Incident Knowledge API** service on Render, set `BOT_PROVIDER=openclaw`, `OPENCLAW_GATEWAY_URL=https://your-openclaw-service.onrender.com`, `OPENCLAW_AUTH_TOKEN` = same token. Redeploy the API.

**Oracle Cloud (always-free VM):**

1. Create an Oracle Cloud account and create an **always-free** VM (e.g. Ubuntu 22.04).
2. SSH into the VM. Install Docker: `curl -fsSL https://get.docker.com | sh`.
3. Clone OpenClaw: `git clone https://github.com/openclaw/openclaw.git && cd openclaw`.
4. Create a volume dir and `openclaw.json` with chatCompletions enabled and your gateway token.
5. Run the gateway in Docker (map the config dir and expose port 3000). Use a reverse proxy (e.g. Caddy or Nginx) with HTTPS (e.g. Let’s Encrypt) and open the firewall so the VM is reachable on 80/443. Your public URL will be `https://your-domain-or-public-ip`.

---

## Option 1: Streamlit Community Cloud (UI)

**Cost:** Free  
**Result:** Public URL like `https://your-app-name.streamlit.app`

### Steps

1. **Push your repo to GitHub** (if not already).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → choose your repo, branch, and set **Main file path** to `app.py`.
4. **Secrets (required for chat):** In the app’s **Settings → Secrets**, add a TOML block. For a **free LLM backend** use one of:

   **A) Groq (free tier)**  
   Get a free API key at [console.groq.com](https://console.groq.com). Then in Secrets:

   ```toml
   BOT_PROVIDER = "openai_compatible"
   OPENAI_COMPATIBLE_URL = "https://api.groq.com/openai/v1"
   OPENAI_COMPATIBLE_API_KEY = "gsk_your_groq_api_key_here"
   ```

   **B) OpenRouter (free models)**  
   Get a key at [openrouter.ai](https://openrouter.ai). Then:

   ```toml
   BOT_PROVIDER = "openai_compatible"
   OPENAI_COMPATIBLE_URL = "https://openrouter.ai/api/v1"
   OPENAI_COMPATIBLE_API_KEY = "your_openrouter_key"
   ```

   **C) Mock / no backend (demo only)**  
   If you leave no bot configured, the UI still loads and shows instructions for setting up a free backend.

5. Click **Deploy**. Your app will be built and get a public URL.

### Notes

- Only the **Streamlit UI** runs on Streamlit Cloud (no FastAPI server there).
- To expose the **POST /chat API** publicly, use the **Deploy the POST API publicly** section above (Render or Railway).
- Free tier has resource limits; for heavy traffic consider Hugging Face Spaces or self-hosting.

---

## Option 2: Hugging Face Spaces

**Cost:** Free  
**Result:** Public URL like `https://huggingface.co/spaces/your-username/incident-knowledge-assistant`

### Steps

1. Create an account at [huggingface.co](https://huggingface.co).
2. Go to **Spaces** → **Create new Space**.
3. Choose **Streamlit** as SDK, set visibility to **Public**, create the Space.
4. Clone the Space repo, copy your app files (`app.py`, `config.py`, `bots/`, `requirements.txt`, etc.), push.
5. **Secrets:** In the Space → **Settings → Repository secrets**, add:
   - `BOT_PROVIDER` = `openai_compatible`
   - `OPENAI_COMPATIBLE_URL` = e.g. `https://api.groq.com/openai/v1`
   - `OPENAI_COMPATIBLE_API_KEY` = your key

   HF Spaces injects these as environment variables; the app reads them via `config.py`.

6. The Space will build and serve your app with a public URL.

### Notes

- Add a `README.md` in the Space so the UI shows a short description and link to this repo.
- For OpenAI-compatible backends, use the same Groq/OpenRouter setup as in Option 1.

---

## Summary

| Goal                         | Free option                    | What to do                                                                 |
|-----------------------------|--------------------------------|----------------------------------------------------------------------------|
| **Public POST /chat API**   | **Render / Railway**           | See **Deploy the POST API publicly** above; use `render.yaml` or set start command + env vars. |
| Public chat UI              | Streamlit Community Cloud / HF | Deploy `app.py`, set Secrets for Groq or OpenRouter (or leave unset).     |
| Fully local (no public URL) | Your machine                   | Run `streamlit run app.py` and `uvicorn api_server:app --host 0.0.0.0 --port 8000`.    |

No cloud infrastructure or paid services are required for the free, open-source public deployment path.
