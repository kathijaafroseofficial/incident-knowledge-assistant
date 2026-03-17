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
