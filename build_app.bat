@echo off
echo Building JXR to JPEG Converter...
pyinstaller --noconfirm --onefile --windowed --add-data "hdr_p3.icc;." converter_app.py
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo Build complete. The exe is located in the dist folder.
pause
