# Quick Commands for Logistics KPI Prediction System
# Usage: 
#   .\quick.ps1 start  - Start all services
#   .\quick.ps1 stop   - Stop all services
#   .\quick.ps1 status - Check status
#   .\quick.ps1 restart - Restart services

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('start', 'stop', 'status', 'restart')]
    [string]$Action
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

switch ($Action) {
    'start' {
        Write-Host "🚀 Starting Logistics KPI System..." -ForegroundColor Cyan
        & "$ProjectRoot\scripts\startup.bat"
    }
    'stop' {
        Write-Host "🛑 Stopping services..." -ForegroundColor Yellow
        & "$ProjectRoot\scripts\shutdown.bat"
    }
    'status' {
        Write-Host "📊 Checking system status..." -ForegroundColor Magenta
        & "$ProjectRoot\scripts\status.bat"
    }
    'restart' {
        Write-Host "🔄 Restarting services..." -ForegroundColor Blue
        & "$ProjectRoot\scripts\restart.bat"
    }
}
