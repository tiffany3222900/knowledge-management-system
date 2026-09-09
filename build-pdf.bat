@echo off
REM Build static site and export PDF
cd /d "%~dp0"
echo Step 1: Building static site...
.venv\Scripts\python.exe -m mkdocs build
if %errorlevel% neq 0 (
    echo Build failed.
    pause
    exit /b 1
)
echo.
echo Step 2: Exporting PDF...
.venv\Scripts\python.exe export_pdf.py
if %errorlevel% equ 0 (
    echo.
    echo PDF generated: Printer_Maintenance_Manual.pdf
) else (
    echo.
    echo PDF export failed.
)
pause
