@echo off
REM ============================================================
REM  ClosingBell bell-dashboard launcher (quiet / background)
REM  - Same as run_dashboard.bat but suppresses Streamlit's startup
REM    banner and runs minimized.  Useful when adding to startup.
REM ============================================================

chcp 65001 >nul
set "VENV_PY=C:\Coding\projects\_venvs\closingbell-py312\Scripts\python.exe"
set "APP=C:\Coding\projects\bell-dashboard\app.py"
set "PORT=8501"

if not exist "%VENV_PY%" exit /b 1
if not exist "%APP%"     exit /b 1

start "ClosingBell Dashboard" /min "%VENV_PY%" -m streamlit run "%APP%" ^
    --server.port=%PORT% ^
    --server.address=localhost ^
    --browser.gatherUsageStats=false ^
    --server.headless=true

REM Give the server a moment, then open the browser.
timeout /t 3 /nobreak >nul
start "" "http://localhost:%PORT%"
