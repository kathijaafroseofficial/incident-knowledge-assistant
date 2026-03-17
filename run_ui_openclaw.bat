@echo off
REM Run Streamlit UI with OpenClaw gateway (127.0.0.1:18789)
cd /d "%~dp0"
set OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789
set BOT_PROVIDER=openclaw
set OPENCLAW_AUTH_TOKEN=49f0d0b6f8695eaf226769b0ac015a1246f54f17b0836b2e
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
streamlit run app.py
