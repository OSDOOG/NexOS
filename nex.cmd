@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%tools\nex\nex.py" (
    python "%SCRIPT_DIR%tools\nex\nex.py" %*
    exit /b %errorlevel%
)
if exist "%SCRIPT_DIR%..\tools\nex\nex.py" (
    python "%SCRIPT_DIR%..\tools\nex\nex.py" %*
    exit /b %errorlevel%
)
if exist "%SCRIPT_DIR%nex.py" (
    python "%SCRIPT_DIR%nex.py" %*
    exit /b %errorlevel%
)
echo Error: Cannot find NexOS Core CLI script nex.py
exit /b 1
