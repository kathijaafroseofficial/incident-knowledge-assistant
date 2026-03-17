# Incident Knowledge Assistant — Folder Organization

```
incident-knowledge-assistant/
│
├── app.py                  # Streamlit UI (dual input, chat, voice, HTML/CSS)
├── api_server.py           # FastAPI POST /chat with Bearer token
├── config.py               # Environment & bot provider config
├── voice_utils.py          # Voice STT (SpeechRecognition) + TTS (gTTS)
├── requirements.txt        # Python dependencies
├── .env.example            # Template: copy to .env
├── .gitignore
├── README.md               # Usage, architecture, assumptions
├── FOLDER_STRUCTURE.md     # This file
├── sample_error.log        # Sample log for testing
├── run_ui.bat              # Run Streamlit (Windows)
├── run_api.bat             # Run FastAPI (Windows)
│
└── bots/                   # Bot providers (MoltBot, ClawDBot, Nanobot, fallbacks)
    ├── __init__.py
    ├── base.py             # BotProvider ABC + get_bot()
    ├── moltbot.py
    ├── clawdbot.py
    ├── nanobot.py
    ├── ollama_bot.py       # Ollama fallback
    └── openai_compatible.py
```

## Run commands

- **UI:** `streamlit run app.py`  (or `run_ui.bat`)
- **API:** `uvicorn api_server:app --host 0.0.0.0 --port 8000`  (or `run_api.bat`)
