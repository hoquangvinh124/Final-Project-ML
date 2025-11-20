@echo off
REM ====================================================================
REM LOGISTICS KPI PREDICTION - SHUTDOWN SCRIPT
REM ====================================================================
REM Author: Data Science Team
REM Date: November 18, 2025
REM Description: Gracefully stops API server and Dashboard
REM ====================================================================

SETLOCAL EnableDelayedExpansion

REM Change to project root directory
cd /d "%~dp0.."

color 0C

echo.
echo ========================================================================
echo                    SHUTTING DOWN SERVICES
echo ========================================================================
echo.

set SERVICES_FOUND=0

REM Method 1: Kill by window title (works if started with startup.bat)
echo [1/4] Stopping API Server by window title...
taskkill /FI "WINDOWTITLE eq Logistics KPI - API Server*" /F >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] API Server stopped ^(by window title^)
    set SERVICES_FOUND=1
) else (
    echo [INFO] API Server window not found
)

echo [2/4] Stopping Dashboard by window title...
taskkill /FI "WINDOWTITLE eq Logistics KPI - Dashboard*" /F >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Dashboard stopped ^(by window title^)
    set SERVICES_FOUND=1
) else (
    echo [INFO] Dashboard window not found
)
echo.

REM Method 2: Kill by PID files
echo [3/4] Checking PID files...
if exist ".temp\.pid_api" (
    set /p API_PID=<.temp\.pid_api
    echo [INFO] Found API PID: !API_PID!
    taskkill /PID !API_PID! /F >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] API Server stopped ^(by PID^)
        set SERVICES_FOUND=1
    )
    del .temp\.pid_api >nul 2>&1
)

if exist ".temp\.pid_dashboard" (
    set /p DASH_PID=<.temp\.pid_dashboard
    echo [INFO] Found Dashboard PID: !DASH_PID!
    taskkill /PID !DASH_PID! /F >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Dashboard stopped ^(by PID^)
        set SERVICES_FOUND=1
    )
    del .temp\.pid_dashboard >nul 2>&1
)
echo.

REM Method 3: Kill by port (fallback)
echo [4/4] Checking for processes on ports 8000 and 8501...

REM Kill process on port 8000 (API)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Found process on port 8000 ^(PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Process on port 8000 stopped
        set SERVICES_FOUND=1
    )
)

REM Kill process on port 8501 (Dashboard)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
    echo [INFO] Found process on port 8501 ^(PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Process on port 8501 stopped
        set SERVICES_FOUND=1
    )
)
echo.

REM Clean up temporary files
if exist ".pid_api" del .pid_api >nul 2>&1
if exist ".pid_dashboard" del .pid_dashboard >nul 2>&1

REM Summary
echo ========================================================================
if !SERVICES_FOUND! equ 1 (
    echo                    [32mSHUTDOWN COMPLETED[0m
    echo.
    echo   All services have been stopped successfully.
) else (
    echo                    [33mNO SERVICES FOUND[0m
    echo.
    echo   No running services were detected.
    echo   Services may not have been started or already stopped.
)
echo ========================================================================
echo.

REM Verify ports are free
timeout /t 2 /nobreak >nul
echo Verifying ports are now free...
netstat -ano | findstr ":8000.*LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo [OK] Port 8000 is free
) else (
    echo [WARNING] Port 8000 is still in use
)

netstat -ano | findstr ":8501.*LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo [OK] Port 8501 is free
) else (
    echo [WARNING] Port 8501 is still in use
)

echo.
echo Press any key to exit...
pause >nul

ENDLOCAL
