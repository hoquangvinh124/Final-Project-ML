@echo off
REM Help - Show available commands
echo.
echo ====================================================================
echo                   LOGISTICS KPI PREDICTION SYSTEM
echo                           Quick Commands
echo ====================================================================
echo.
echo   BASIC COMMANDS (1-liner):
echo   -------------------------
echo   start.bat              - Start all services (3 seconds)
echo   stop.bat               - Stop all services
echo.
echo   FULL COMMANDS:
echo   -------------------------
echo   scripts\startup.bat    - Full startup with details
echo   scripts\shutdown.bat   - Stop all services
echo   scripts\status.bat     - Check system status
echo   scripts\restart.bat    - Restart services
echo.
echo   POWERSHELL (flexible):
echo   -------------------------
echo   .\quick.ps1 start      - Start services
echo   .\quick.ps1 stop       - Stop services
echo   .\quick.ps1 status     - Check status
echo   .\quick.ps1 restart    - Restart
echo.
echo   SERVICES:
echo   -------------------------
echo   API Server:            http://localhost:8000
echo   API Docs (Swagger):    http://localhost:8000/docs
echo   Dashboard:             http://localhost:8501
echo.
echo   DOCUMENTATION:
echo   -------------------------
echo   README.md              - Main documentation
echo   QUICK_START.md         - Quick start guide
echo   docs\                  - Detailed guides
echo.
echo ====================================================================
echo.
echo   TIP: Just run "start.bat" to begin!
echo.
pause
