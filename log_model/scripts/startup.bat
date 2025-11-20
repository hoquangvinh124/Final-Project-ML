@echo off
REM ====================================================================
REM LOGISTICS KPI PREDICTION - STARTUP SCRIPT
REM ====================================================================
REM Author: Data Science Team
REM Date: November 18, 2025
REM Description: Automatically starts API server and Dashboard
REM ====================================================================

SETLOCAL EnableDelayedExpansion

REM Change to project root directory
cd /d "%~dp0.."

REM Colors (optional, for better visibility)
color 0A

echo.
echo ========================================================================
echo    ___   ____   ____      __  ____   ____   ____   _____  ____  ______
echo   / __\ / ___) (___ \    / / / ___) / ___) / ___)^|_   _^|/   _\(   __ \
echo  ( (__  \___ \   / _ \  / / ( (__  ( (__  ( (___   ^| ^|  ^|  ^|_/^\^|  (__^)
echo   \___) (____/  (_____^)(_/   \___^)  \___^)  \___^)  ^|_^|  ^|_____/ (____/
echo.
echo                    LOGISTICS KPI PREDICTION SYSTEM
echo                         Starting Services...
echo ========================================================================
echo.

REM Step 1: Check Python installation
echo [1/6] Checking Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.8+ first.
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

REM Step 2: Check virtual environment
echo [2/6] Checking virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo [WARNING] Virtual environment not found!
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [INFO] Installing dependencies...
    call .venv\Scripts\activate.bat
    pip install -r deployment\requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)
call .venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Step 3: Check model files
echo [3/6] Checking model files...
set MODEL_FOUND=0
for %%f in (models\Ridge_Regression_*.pkl) do set MODEL_FOUND=1

if !MODEL_FOUND! equ 0 (
    echo [ERROR] Model files not found in models\ directory!
    echo [INFO] Please train the model first:
    echo        python train_model.py
    echo.
    pause
    exit /b 1
)
echo [OK] Model files found
echo.

REM Step 4: Create logs directory if not exists
if not exist "logs" mkdir logs
echo [4/6] Logs directory ready (logs\)
echo.

REM Step 5: Start API Server
echo [5/6] Starting API Server...
echo [INFO] API will be available at: http://localhost:8000
echo [INFO] API Docs (Swagger): http://localhost:8000/docs
echo [INFO] Logs: logs\api.log
start "Logistics KPI - API Server" /MIN cmd /k "title Logistics KPI - API Server && cd /d "%~dp0.." && call .venv\Scripts\activate.bat && set PYTHONIOENCODING=utf-8 && python src\api\app.py > logs\api.log 2>&1"

REM Quick health check (2 seconds only)
echo [INFO] Starting API server...
timeout /t 2 /nobreak >nul
echo [OK] API Server initiated
echo.

REM Step 6: Start Dashboard
echo [6/6] Starting Streamlit Dashboard...
echo [INFO] Dashboard will be available at: http://localhost:8501
echo [INFO] Logs: logs\dashboard.log
start "Logistics KPI - Dashboard" /MIN cmd /k "title Logistics KPI - Dashboard && cd /d "%~dp0.." && call .venv\Scripts\activate.bat && set PYTHONIOENCODING=utf-8 && streamlit run src\dashboard\dashboard.py > logs\dashboard.log 2>&1"

echo [INFO] Starting Dashboard...
timeout /t 1 /nobreak >nul
echo [OK] Dashboard initiated
echo.

REM Create temp directory if not exists
if not exist ".temp" mkdir .temp

REM Save PIDs for later shutdown (PowerShell method)
echo [INFO] Saving process information...
powershell -Command "Get-WmiObject Win32_Process | Where-Object {$_.CommandLine -like '*app.py*'} | Select-Object -First 1 | ForEach-Object {$_.ProcessId} | Out-File -FilePath .temp\.pid_api -Encoding ASCII" >nul 2>&1
powershell -Command "Get-WmiObject Win32_Process | Where-Object {$_.CommandLine -like '*streamlit*'} | Select-Object -First 1 | ForEach-Object {$_.ProcessId} | Out-File -FilePath .temp\.pid_dashboard -Encoding ASCII" >nul 2>&1

REM Final summary
echo.
echo ========================================================================
echo                    [32mSTARTUP COMPLETED SUCCESSFULLY![0m
echo ========================================================================
echo.
echo   [36m[SERVICES RUNNING][0m
echo   ✓ API Server:         http://localhost:8000
echo   ✓ API Documentation:  http://localhost:8000/docs
echo   ✓ Dashboard:          http://localhost:8501
echo.
echo   [33m[LOGS][0m
echo   • API logs:           logs\api.log
echo   • Dashboard logs:     logs\dashboard.log
echo   • Monitoring logs:    monitoring_logs.log
echo   • Predictions:        predictions_history.csv
echo.
echo   [35m[MANAGEMENT][0m
echo   • To stop services:   scripts\shutdown.bat
echo   • To view status:     scripts\status.bat
echo   • To restart:         scripts\restart.bat
echo.
echo   [90m[TIPS][0m
echo   • The windows are minimized - check taskbar
echo   • Press Ctrl+C in service window to stop that service
echo   • View logs for troubleshooting
echo.
echo ========================================================================
echo.
echo [90m[TIP] Opening browsers in background...[0m
start /min cmd /c "timeout /t 5 /nobreak >nul && start http://localhost:8000/docs && timeout /t 1 /nobreak >nul && start http://localhost:8501" 2>nul

echo.
echo [32mAll services are now running[0m
echo [90mBrowsers will open automatically in 5 seconds...[0m
echo.
echo Press any key to close this window (services will keep running)...
pause >nul

ENDLOCAL
