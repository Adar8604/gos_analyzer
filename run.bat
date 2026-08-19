@echo off

echo Starting GOS Analyzer

call .venv\Scripts\activate.bat

start "GOS Analyzer" cmd /k "streamlit run frontend\app.py --server.address 0.0.0.0 --server.port 8502"
start "MkDocs" cmd /k "mkdocs serve --dev-addr 0.0.0.0:8503 --open"

pause