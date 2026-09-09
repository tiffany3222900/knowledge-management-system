@echo off
REM Build static site only (output to site/ directory)
cd /d "%~dp0"
echo Building static site...
.venv\Scripts\python.exe -m mkdocs build
echo.
echo Site built to site\ directory
pause
