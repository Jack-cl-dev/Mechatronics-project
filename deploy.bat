@echo off
REM ===================================================================
REM  DOUBLE-CLICK THIS FILE to put the code on the micro:bit (Windows).
REM
REM  It just launches deploy.ps1. This wrapper exists because:
REM    * double-clicking a .ps1 file opens it in Notepad instead of running it
REM    * Windows blocks unsigned .ps1 scripts by default, and -ExecutionPolicy
REM      Bypass here avoids making the user change a system-wide setting
REM
REM  Choose which program gets deployed in the settings block at the top of
REM  deploy.ps1, or leave it at 0 and it will ask you.
REM ===================================================================

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy.ps1"

REM If PowerShell itself couldn't start, the window would close instantly
REM without deploy.ps1's own "Press Enter" prompt, so catch that here.
if errorlevel 1 (
    echo.
    echo If nothing appeared above, Windows PowerShell could not be started.
    pause
)
