@echo off
REM ====================================================================
REM LOGISTICS KPI PREDICTION - STATUS CHECK
REM ====================================================================
REM Author: Data Science Team
REM Date: November 18, 2025
REM Description: Check if services are running
REM ====================================================================

cd /d "%~dp0.."

color 0B

echo.
echo ========================================================================
echo                    SYSTEM STATUS CHECK
echo ========================================================================
echo.

REM Check API Server (port 8000)
echo [1/2] Checking API Server (port 8000)...
echo -----------------------------------------------------------------------
netstat -ano | findstr ":8000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo Status:    [32m✓ RUNNING[0m
    echo URL:       http://localhost:8000
    echo API Docs:  http://localhost:8000/docs
    
    REM Get PID
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        echo Process:   PID %%a
        
        REM Get process details
        for /f "tokens=*" %%b in ('tasklist /FI "PID eq %%a" /FO LIST ^| findstr "Image Name:"') do echo %%b
        for /f "tokens=*" %%c in ('tasklist /FI "PID eq %%a" /FO LIST ^| findstr "Mem Usage:"') do echo %%c
    )
    
    REM Test API health
    echo.
    echo Testing API health endpoint...
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 3; Write-Host 'Health Check: ' -NoNewline; Write-Host 'HEALTHY' -ForegroundColor Green; $json = $response.Content | ConvertFrom-Json; Write-Host 'Model Version:' $json.model_version } catch { Write-Host 'Health Check: ' -NoNewline; Write-Host 'FAILED' -ForegroundColor Red }"
) else (
    echo Status:    [31m✗ NOT RUNNING[0m
    echo.
    echo API Server is not running on port 8000
    echo To start: scripts\startup.bat
)
echo.

REM Check Dashboard (port 8501)
echo [2/2] Checking Streamlit Dashboard (port 8501)...
echo -----------------------------------------------------------------------
netstat -ano | findstr ":8501.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo Status:    [32m✓ RUNNING[0m
    echo URL:       http://localhost:8501
    
    REM Get PID
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
        echo Process:   PID %%a
        
        REM Get process details
        for /f "tokens=*" %%b in ('tasklist /FI "PID eq %%a" /FO LIST ^| findstr "Image Name:"') do echo %%b
        for /f "tokens=*" %%c in ('tasklist /FI "PID eq %%a" /FO LIST ^| findstr "Mem Usage:"') do echo %%c
    )
) else (
    echo Status:    [31m✗ NOT RUNNING[0m
    echo.
    echo Dashboard is not running on port 8501
    echo To start: scripts\startup.bat
)
echo.

REM Additional system info
echo ========================================================================
echo                    ADDITIONAL INFORMATION
echo ========================================================================
echo.

REM Check model files
echo Model Files:
if exist "models\Ridge_Regression_*.pkl" (
    echo [32m✓[0m Ridge Regression model found
) else (
    echo [31m✗[0m Ridge Regression model NOT found
)

if exist "models\scaler_*.pkl" (
    echo [32m✓[0m Scaler found
) else (
    echo [31m✗[0m Scaler NOT found
)

if exist "models\encoders_*.pkl" (
    echo [32m✓[0m Encoders found
) else (
    echo [31m✗[0m Encoders NOT found
)
echo.

REM Check log files
echo Log Files:
if exist "logs\api.log" (
    for %%A in ("logs\api.log") do echo   • API log: %%~zA bytes ^(logs\api.log^)
) else (
    echo   • API log: Not found
)

if exist "logs\dashboard.log" (
    for %%A in ("logs\dashboard.log") do echo   • Dashboard log: %%~zA bytes ^(logs\dashboard.log^)
) else (
    echo   • Dashboard log: Not found
)

if exist "monitoring_logs.log" (
    for %%A in ("monitoring_logs.log") do echo   • Monitoring log: %%~zA bytes ^(monitoring_logs.log^)
) else (
    echo   • Monitoring log: Not found
)

if exist "predictions_history.csv" (
    for %%A in ("predictions_history.csv") do echo   • Predictions history: %%~zA bytes ^(predictions_history.csv^)
) else (
    echo   • Predictions history: Not found
)
echo.

REM Check virtual environment
echo Virtual Environment:
if exist "venv\Scripts\python.exe" (
    echo [32m✓[0m Virtual environment found at: venv\
    venv\Scripts\python.exe --version 2>nul
) else (
    echo [31m✗[0m Virtual environment NOT found
    echo Run: python -m venv venv
)
echo.

echo ========================================================================
echo.
echo Quick Actions:
echo   • Start services:   scripts\startup.bat
echo   • Stop services:    scripts\shutdown.bat
echo   • Restart services: scripts\restart.bat
echo   • View API docs:    http://localhost:8000/docs
echo   • View dashboard:   http://localhost:8501
echo.
echo ========================================================================
echo.
pause
