@echo off
REM Start local MkDocs preview server at http://127.0.0.1:8000
cd /d "%~dp0"
echo Starting MkDocs preview server...
echo Open http://127.0.0.1:8000 in your browser
echo Press Ctrl+C to stop
.venv\Scripts\python.exe -m mkdocs serve
pause
