@echo off
REM Build static site and export bilingual PDFs (EN + ZH)
cd /d "%~dp0"
echo Step 1: Building static site...
.venv\Scripts\python.exe -m mkdocs build
if %errorlevel% neq 0 (
    echo Build failed.
    pause
    exit /b 1
)
echo.
echo Step 2: Exporting English PDF...
.venv\Scripts\python.exe export_pdf.py en
if %errorlevel% neq 0 (
    echo English PDF export failed.
    pause
    exit /b 1
)
echo.
echo Step 3: Exporting Chinese PDF...
.venv\Scripts\python.exe export_pdf.py zh
if %errorlevel% equ 0 (
    echo.
    echo PDFs generated: Printer_Maintenance_Manual_EN.pdf + Printer_Maintenance_Manual_ZH.pdf
) else (
    echo.
    echo Chinese PDF export failed.
)
pause
