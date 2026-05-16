@echo off
REM ============================================================
REM  ClosingBell bell-dashboard launcher
REM  - Activates the shared closingbell-py312 venv
REM  - Starts Streamlit and opens http://localhost:8501
REM ============================================================

chcp 65001 >nul
setlocal

set "VENV_PY=C:\Coding\projects\_venvs\closingbell-py312\Scripts\python.exe"
set "APP=C:\Coding\projects\bell-dashboard\app.py"
set "PORT=8501"

if not exist "%VENV_PY%" (
    echo [ERROR] venv not found: %VENV_PY%
    echo Please verify the closingbell-py312 venv path.
    pause
    exit /b 1
)

if not exist "%APP%" (
    echo [ERROR] app.py not found: %APP%
    pause
    exit /b 1
)

title ClosingBell Dashboard ^| port %PORT%
echo.
echo  ClosingBell bell-dashboard
echo  -----------------------------------------
echo  Python : %VENV_PY%
echo  App    : %APP%
echo  URL    : http://localhost:%PORT%
echo  -----------------------------------------
echo  Press Ctrl+C in this window to stop the server.
echo.

REM Streamlit auto-opens the browser by default (server.headless=false).
"%VENV_PY%" -m streamlit run "%APP%" ^
    --server.port=%PORT% ^
    --server.address=localhost ^
    --browser.gatherUsageStats=false

endlocal
pause
