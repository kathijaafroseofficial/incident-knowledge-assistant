# How to run the API and UI

## Option A: Run with mock bot (no OpenClaw gateway)

Use this when the OpenClaw gateway is not running or you see "Health check failed / 1006".

### 1. Start the mock bot server (one terminal)

```bat
run_mock_bot.bat
```

Leave this window open. The mock server listens on **http://localhost:9090**.

### 2. Start the UI (second terminal)

```bat
run_ui.bat
```

Open **http://localhost:8501** in your browser.

### 3. Start the API (optional; third terminal)

```bat
run_api.bat
```

API base: **http://localhost:8000** (e.g. `POST /chat` with Bearer token).

---

## Option B: Run with OpenClaw (when gateway is running)

The **"Gateway: not detected (1006 abnormal closure)"** message means the OpenClaw gateway process is not running or closed. Fix it first:

1. **Start the OpenClaw gateway**  
   From a terminal run:
   ```bat
   openclaw
   ```
   Or start it from the OpenClaw dashboard / app so that **ws://127.0.0.1:18789** is active.

2. **Use your token in `.env`**  
   Set:
   ```env
   BOT_PROVIDER=openclaw
   OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789
   OPENCLAW_AUTH_TOKEN=49f0d0b6f8695eaf226769b0ac015a1246f54f17b0836b2e
   ```
   (Replace with your actual token from the onboarding Control UI link.)

3. **Enable HTTP chat in OpenClaw**  
   In `C:\Users\ahame\.openclaw\openclaw.json` (or the config path OpenClaw uses), ensure the gateway allows HTTP chat completions. See [OpenClaw gateway docs](https://docs.openclaw.ai/gateway/health).

4. **Run UI and API** (no mock server needed):
   ```bat
   run_ui.bat
   run_api.bat
   ```

---

## Summary

| Goal              | Step 1              | Step 2       | Step 3 (optional) |
|-------------------|---------------------|--------------|-------------------|
| **UI + mock bot** | `run_mock_bot.bat`  | `run_ui.bat` | —                 |
| **API + mock bot**| `run_mock_bot.bat`  | `run_api.bat`| —                 |
| **UI + OpenClaw** | Start OpenClaw gateway (port 18789), set `.env` | `run_ui.bat` | — |
| **API + OpenClaw**| Start OpenClaw gateway, set `.env` | `run_api.bat` | — |

The `.env` file in this project is set for the **mock bot** by default so the UI and API work without OpenClaw. Switch to OpenClaw by changing `BOT_PROVIDER` and setting `OPENCLAW_AUTH_TOKEN` once the gateway is running.
