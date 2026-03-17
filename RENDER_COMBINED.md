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

3. **Environment variables** (required):

   | Key | Value |
   |-----|--------|
   | `API_BEARER_TOKEN` | Your secret token for `POST /chat` (e.g. random string). |
   | `BOT_PROVIDER` | `openclaw` |
   | `OPENCLAW_GATEWAY_URL` | `http://127.0.0.1:3000` (must be this so the API talks to in-container OpenClaw) |
   | `OPENCLAW_AUTH_TOKEN` | Same value as `OPENCLAW_GATEWAY_TOKEN` (see below). |
   | `OPENCLAW_GATEWAY_TOKEN` | A secret token (e.g. 32+ random chars). **Use the same value** in the API as `OPENCLAW_AUTH_TOKEN`. |
   | `ANTHROPIC_API_KEY` | Your Anthropic key (or other model key OpenClaw supports). |

   Generate one token and set it as both `OPENCLAW_GATEWAY_TOKEN` and `OPENCLAW_AUTH_TOKEN`.

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
