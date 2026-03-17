# Deploy OpenClaw on Fly.io and use it with Render (Option B)

Follow these steps in order. You will: (1) install Fly CLI, (2) deploy OpenClaw to Fly.io and get a public URL, (3) set Render to use that URL.

---

## Prerequisites

- A [Fly.io](https://fly.io) account (sign up at fly.io; free tier may require a card on file).
- Git installed.
- Your model API key (e.g. Anthropic, OpenAI, or another provider OpenClaw supports).

---

## Step 1: Install Fly CLI on Windows

In **PowerShell** (Run as Administrator if the script asks for elevation):

```powershell
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

Close and reopen PowerShell, then check:

```powershell
fly version
```

Log in:

```powershell
fly auth login
```

(Browser will open to sign in to Fly.io.)

---

## Step 2: Generate a gateway token (use this everywhere)

Generate **one** token and use it in Fly secrets, OpenClaw config, and Render.

**Option A — PowerShell (hex token):**

```powershell
-join ((48..57) + (97..102) | Get-Random -Count 64 | ForEach-Object { [char]$_ })
```

This gives a 64-character hex string. Copy it and use it as your token everywhere.

**Option B — Git Bash or WSL (if you have it):**

```bash
openssl rand -hex 32
```

**Save this token** (e.g. in a temporary file or password manager). You will use it in Step 5 (Fly secrets), Step 7 (openclaw.json), and Step 9 (Render).

---

## Step 3: Clone OpenClaw and create the Fly app

In a folder of your choice (e.g. your home or `C:\dev`):

```powershell
git clone https://github.com/openclaw/openclaw.git
cd openclaw
```

Create the Fly app (use a **unique** name; only letters, numbers, hyphens):

```powershell
fly apps create my-openclaw
```

(Replace `my-openclaw` with your chosen name, e.g. `incident-openclaw-kathija`.)

Create a 1GB volume for config and data:

```powershell
fly volumes create openclaw_data --size 1 --region iad
```

(`iad` = Virginia; you can use `lhr` for London or another [region](https://fly.io/docs/reference/regions/).)

---

## Step 4: Configure `fly.toml`

In the `openclaw` folder, create or replace `fly.toml` with the content below.  
**Replace `my-openclaw`** with the same app name you used in Step 3.

```toml
app = "my-openclaw"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  NODE_ENV = "production"
  OPENCLAW_PREFER_PNPM = "1"
  OPENCLAW_STATE_DIR = "/data"
  NODE_OPTIONS = "--max-old-space-size=1536"

[processes]
  app = "node dist/index.js gateway --allow-unconfigured --port 3000 --bind lan"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[vm]]
  size = "shared-cpu-2x"
  memory = "2048mb"

[mounts]
  source = "openclaw_data"
  destination = "/data"
```

Save the file.

---

## Step 5: Set Fly secrets

Still in the `openclaw` folder.

Set the gateway token (use the **same** token you generated in Step 2):

```powershell
fly secrets set OPENCLAW_GATEWAY_TOKEN=YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with your actual token (no quotes needed).

Add your model API key so OpenClaw can call the LLM. Example for Anthropic:

```powershell
fly secrets set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

(Use the key for your chosen provider; see [OpenClaw docs](https://open-claw.bot/docs) for supported env vars.)

---

## Step 6: Deploy

From the `openclaw` folder:

```powershell
fly deploy
```

Wait for the build and deploy to finish. If it fails, check the Fly dashboard logs.

---

## Step 7: Create OpenClaw config with chat completions enabled

After deploy, open a shell on the Fly machine:

```powershell
fly ssh console
```

In the **remote** console you get a Linux shell. Run the commands below.

**Important:** Before pasting, replace `YOUR_SAME_TOKEN` in the JSON with your **exact** token from Step 2 (no quotes around the token in the JSON if it has no spaces; if it has spaces, keep the whole value in double quotes).

```bash
mkdir -p /data
```

Then create the config. **First** replace `YOUR_SAME_TOKEN` in the snippet below with your real token, then paste the whole block into the SSH console:

```bash
cat > /data/openclaw.json << 'ENDOFFILE'
{
  "gateway": {
    "http": { "endpoints": { "chatCompletions": { "enabled": true } } },
    "auth": { "mode": "token", "token": "YOUR_SAME_TOKEN" }
  },
  "agents": {
    "defaults": { "model": { "primary": "anthropic/claude-3-5-sonnet-latest" } },
    "list": [{ "id": "main", "default": true }]
  }
}
ENDOFFILE
exit
```

If your model is not Anthropic, change `"primary": "anthropic/claude-3-5-sonnet-latest"` to the model ID your provider uses (see OpenClaw docs).

Then restart the app so it loads the new config:

```powershell
fly machine restart --all
```

---

## Step 8: Get your public URL

Your OpenClaw gateway will be at:

**`https://my-openclaw.fly.dev`**

Replace `my-openclaw` with your actual app name. You can also run:

```powershell
fly status
```

and check the hostname in the output.

Test in a browser or with curl (use your token):

```powershell
curl -H "Authorization: Bearer YOUR_SAME_TOKEN" https://my-openclaw.fly.dev/
```

You should get a response (e.g. 200 or a short message), not connection refused.

---

## Step 9: Point Render at OpenClaw

1. Open **Render** → your **incident-knowledge-api** (or whatever you named it) service.
2. Go to **Environment**.
3. Set or update:
   - **BOT_PROVIDER** = `openclaw`
   - **OPENCLAW_GATEWAY_URL** = `https://my-openclaw.fly.dev` (your real Fly URL from Step 8; no trailing slash, no port)
   - **OPENCLAW_AUTH_TOKEN** = the **same** token you used in Step 2 / 5 / 7
   - **OPENCLAW_AGENT_ID** = `main` (optional; this is the default)
4. Remove or leave unchanged any `OPENAI_COMPATIBLE_*` vars if you were using Option A before.
5. Click **Save Changes**.
6. Trigger a **Manual Deploy** (or wait for auto-deploy) so the API restarts with the new env.

---

## Step 10: Test the API on Render

After the Render deploy finishes:

```powershell
curl -X POST https://YOUR_RENDER_URL/chat `
  -H "Authorization: Bearer YOUR_RENDER_API_BEARER_TOKEN" `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"What is 2+2?\", \"context\": \"\"}'
```

Replace `YOUR_RENDER_URL` with your Render service URL (e.g. `https://incident-knowledge-api.onrender.com`) and `YOUR_RENDER_API_BEARER_TOKEN` with the token you set for the **API** (the one you use for `POST /chat`). You should get a JSON reply with `"bot": "OpenClaw"` and an answer in `"reply"`.

---

## Troubleshooting

- **Connection refused from Render:** Ensure `OPENCLAW_GATEWAY_URL` is the **public** Fly URL (e.g. `https://my-openclaw.fly.dev`) and that you ran `fly machine restart --all` after creating `/data/openclaw.json`.
- **401 Unauthorized:** Make sure `OPENCLAW_AUTH_TOKEN` on Render matches `gateway.auth.token` in `/data/openclaw.json` and `OPENCLAW_GATEWAY_TOKEN` in Fly secrets.
- **404 on /v1/chat/completions:** Ensure `/data/openclaw.json` has `"chatCompletions": { "enabled": true }` under `gateway.http.endpoints` and you restarted the machine.
- **Fly app crashes or OOM:** The `fly.toml` above uses 2GB RAM; if you reduced it, set it back to 2048mb.

---

## Quick reference

| Where        | What to set |
|-------------|-------------|
| Fly secrets | `OPENCLAW_GATEWAY_TOKEN` = your token |
| Fly `/data/openclaw.json` | `gateway.auth.token` = same token, `chatCompletions.enabled: true` |
| Render Environment | `BOT_PROVIDER=openclaw`, `OPENCLAW_GATEWAY_URL=https://my-openclaw.fly.dev`, `OPENCLAW_AUTH_TOKEN` = same token |

Use the **same token** in all three places.
