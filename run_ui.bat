@echo off
REM Run Streamlit UI (Incident Knowledge Assistant)
cd /d "%~dp0"
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
streamlit run app.py
