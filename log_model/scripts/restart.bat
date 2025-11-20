@echo off
REM ====================================================================
REM LOGISTICS KPI PREDICTION - RESTART SCRIPT
REM ====================================================================
REM Author: Data Science Team
REM Date: November 18, 2025
REM Description: Restart both API server and Dashboard
REM ====================================================================

cd /d "%~dp0.."

color 0E

echo.
echo ========================================================================
echo                    RESTARTING SERVICES
echo ========================================================================
echo.

echo [1/3] Stopping current services...
call "%~dp0shutdown.bat"

echo.
echo [2/3] Waiting for clean shutdown...
timeout /t 3 /nobreak >nul
echo.

echo [3/3] Starting services...
call "%~dp0startup.bat"

echo.
echo ========================================================================
echo                    RESTART COMPLETED
echo ========================================================================
echo.
