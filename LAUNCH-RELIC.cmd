@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch-relic.ps1" -PauseOnExit %*
exit /b %ERRORLEVEL%
