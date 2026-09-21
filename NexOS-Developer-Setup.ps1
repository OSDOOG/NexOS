# NexOS Developer Setup Script for Windows PowerShell
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                  NEXOS DEVELOPER SETUP & CONFIGURATION                         " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

$CurrentPath = $PSScriptRoot
Write-Host "NexOS Root Directory: $CurrentPath"

# Verify Python
try {
    $pyVer = python --version
    Write-Host "[+] Python Detected: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[-] Python is not installed. Please install Python 3.10+ from python.org" -ForegroundColor Red
    exit 1
}

# Run Installer Backend
python "$CurrentPath\installer\setup.py" esp32-c6 rp2040 pico-w esp8266 arduino-avr stm32 host

Write-Host "`nTo start NexOS Developer Studio GUI, run:" -ForegroundColor Yellow
Write-Host "  python nexos-developer\server.py" -ForegroundColor White
Write-Host "`nTo use the NexOS CLI, run:" -ForegroundColor Yellow
Write-Host "  .\nex.cmd doctor" -ForegroundColor White
Write-Host "  .\nex.cmd targets" -ForegroundColor White
