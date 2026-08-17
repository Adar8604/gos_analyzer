@echo off

echo Starting GOS Analyser

cd /d "%~dp0"

call .venv\Scripts\activate.bat

start "GOS Analyzer" cmd /k "streamlit run frontend\app.py --server.port 8502"
start "MkDocs" cmd /k "mkdocs serve --open"

pause