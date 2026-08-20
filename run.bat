@echo off
title GOS Analyzer

echo ==========================================
echo        Starting GOS Analyzer
echo ==========================================
echo.

call .venv\Scripts\activate.bat

REM --------------------------------------------------
REM Force Hugging Face / Transformers to work offline
REM --------------------------------------------------
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1

echo Hugging Face offline mode enabled
echo.

REM --------------------------------------------------
REM Start Streamlit
REM --------------------------------------------------
echo Starting Streamlit on port 8502...

start "" /B cmd /c "call .venv\Scripts\activate.bat && set HF_HUB_OFFLINE=1 && set TRANSFORMERS_OFFLINE=1 && streamlit run frontend\app.py --server.address 0.0.0.0 --server.port 8502"

REM --------------------------------------------------
REM Start MkDocs
REM --------------------------------------------------
echo Starting MkDocs on port 8503...

start "" /B cmd /c "call .venv\Scripts\activate.bat && mkdocs serve --dev-addr 0.0.0.0:8503"

REM --------------------------------------------------
REM Wait for Streamlit
REM --------------------------------------------------
echo.
echo Waiting for Streamlit...

:WAIT_STREAMLIT
powershell -NoProfile -Command "$t=Test-NetConnection -ComputerName 127.0.0.1 -Port 8502 -WarningAction SilentlyContinue; if ($t.TcpTestSucceeded) { exit 0 } else { exit 1 }"

if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto WAIT_STREAMLIT
)

echo Streamlit is ready.

REM --------------------------------------------------
REM Wait for MkDocs
REM --------------------------------------------------
echo Waiting for MkDocs...

:WAIT_MKDOCS
powershell -NoProfile -Command "$t=Test-NetConnection -ComputerName 127.0.0.1 -Port 8503 -WarningAction SilentlyContinue; if ($t.TcpTestSucceeded) { exit 0 } else { exit 1 }"

if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto WAIT_MKDOCS
)

echo MkDocs is ready.

REM --------------------------------------------------
REM Open browsers ONLY after both services are ready
REM --------------------------------------------------
echo.
echo ==========================================
echo All services are running!
echo ==========================================
echo.
echo GOS Analyzer: http://localhost:8502
echo MkDocs:       http://localhost:8503
echo.

start "" http://localhost:8503

echo Both applications opened in the browser.
echo.
echo Press any key to close this launcher...
pause >nul