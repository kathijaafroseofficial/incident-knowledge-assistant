@echo off
REM Start mock ClawDBot server (port 9090) so UI/API work without OpenClaw gateway
cd /d "%~dp0"
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
echo Starting mock bot server at http://localhost:9090 ...
echo Keep this window open. In another terminal run run_ui.bat or run_api.bat
python scripts/mock_bot_server.py
