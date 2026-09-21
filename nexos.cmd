@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%tools\nexos\nexos_cli.py" (
    python "%SCRIPT_DIR%tools\nexos\nexos_cli.py" %*
    exit /b %errorlevel%
)
if exist "%SCRIPT_DIR%..\tools\nexos\nexos_cli.py" (
    python "%SCRIPT_DIR%..\tools\nexos\nexos_cli.py" %*
    exit /b %errorlevel%
)
if exist "%SCRIPT_DIR%nexos_cli.py" (
    python "%SCRIPT_DIR%nexos_cli.py" %*
    exit /b %errorlevel%
)
echo Error: Cannot find NexOS CLI script nexos_cli.py
exit /b 1
