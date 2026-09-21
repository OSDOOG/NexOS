@echo off
echo Installing NexOS Developer Tools to %LOCALAPPDATA%\NexOS...
powershell -Command "Expand-Archive -Force 'NexOS-Developer-Setup.zip' -DestinationPath '%LOCALAPPDATA%\NexOS'"
setx PATH "%PATH%;%LOCALAPPDATA%\NexOS\bin"
echo NexOS Developer Tools installed successfully! Run 'nexos doctor' to verify.
pause
