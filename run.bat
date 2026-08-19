@echo off

echo Starting GOS Analyzer

call .venv\Scripts\activate.bat

REM --------------------------------------------------
REM Force Hugging Face / Transformers to work offline
REM Models must already be downloaded locally.
REM --------------------------------------------------
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1

echo Hugging Face offline mode enabled

REM Start Streamlit
start "GOS Analyzer" cmd /k "set HF_HUB_OFFLINE=1 && set TRANSFORMERS_OFFLINE=1 && call .venv\Scripts\activate.bat && streamlit run frontend\app.py --server.address 0.0.0.0 --server.port 8502"

REM Start MkDocs
start "MkDocs" cmd /k "call .venv\Scripts\activate.bat && mkdocs serve --dev-addr 0.0.0.0:8503 --open"

echo.
echo GOS Analyzer: http://localhost:8502
echo MkDocs:       http://localhost:8503
echo.
echo Press any key to exit...
pause >nul