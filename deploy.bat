@echo off
REM Build static site and deploy to GitHub Pages
cd /d "%~dp0"
echo Building and deploying to GitHub Pages...
.venv\Scripts\python.exe -m mkdocs gh-deploy --force
if %errorlevel% equ 0 (
    echo.
    echo Deployment successful!
    echo Site will be live at https://tiffany3222900.github.io/knowledge-management-system/ in 1-2 minutes.
) else (
    echo.
    echo Deployment failed. Check the error messages above.
)
pause
