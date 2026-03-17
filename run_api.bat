@echo off
REM Run FastAPI server (public POST endpoint, Bearer token)
cd /d "%~dp0"
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
uvicorn api_server:app --host 0.0.0.0 --port 8000
