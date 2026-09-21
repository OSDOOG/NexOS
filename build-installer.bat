@echo off
echo ========================================================
echo   Building NexOS Developer Setup Installer (.exe)
echo ========================================================
python "%~dp0installer\build_installer.py"
echo.
echo Installer generated at:
echo   %~dp0dist_installer\NexOS-Developer-Setup.exe
echo ========================================================
pause
