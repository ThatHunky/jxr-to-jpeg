@echo off
echo Installing Python dependencies...
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo Failed to install Python packages.
    pause
    exit /b 1
)

if exist jxr2jpg.exe (
    echo Found jxr2jpg.exe
) else (
    echo jxr2jpg.exe not found!
    echo Please download it from https://github.com/jxr-tools/jxr2jpg
    echo and place it in this folder or add it to PATH.
)

pause
