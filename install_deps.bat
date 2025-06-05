@echo off
echo Installing Python dependencies...
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo Failed to install Python packages.
    pause
    exit /b 1
)

echo Dependencies installed.

pause
