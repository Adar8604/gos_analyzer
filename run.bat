@echo off

echo Starting GOS Analyzer

call .venv\Scripts\activate.bat

start "GOS Analyzer" cmd /k "streamlit run frontend\app.py --server.port 8502"
start "MkDocs" cmd /k "mkdocs serve --open"

pause