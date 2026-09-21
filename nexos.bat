@echo off
if exist "%~dp0tools\nexos\nexos_cli.py" (
    python "%~dp0tools\nexos\nexos_cli.py" %*
) else if exist "%~dp0..\tools\nexos\nexos_cli.py" (
    python "%~dp0..\tools\nexos\nexos_cli.py" %*
) else if exist "%~dp0nexos_cli.py" (
    python "%~dp0nexos_cli.py" %*
) else (
    echo Error: Cannot find NexOS CLI script.
    exit /b 1
)
