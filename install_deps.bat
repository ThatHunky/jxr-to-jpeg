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
    echo Download the jxr_to_png release from https://github.com/ledoge/jxr_to_png
    echo Rename the executable to jxr2jpg.exe and place it in this folder or add it to PATH.
)

pause
