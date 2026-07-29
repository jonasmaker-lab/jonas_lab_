@echo off
rem doppelklick-flasher fuer windows
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py flash.py
) else (
    python flash.py
)
echo.
pause
