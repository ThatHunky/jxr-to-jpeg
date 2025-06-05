# JXR to JPEG Converter

A simple Windows tool that watches a folder for new `.jxr` images and converts them to `.jpg`. The conversion uses the [`imagecodecs`](https://pypi.org/project/imagecodecs/) library, so no external executables are required.

> **Note**
> The previous version relied on `jxr2jpg.exe`. Conversion is now handled natively via `imagecodecs`.

## Requirements
- Python 3.12 when running from source (not needed for the built exe).
- Python packages: `watchdog`, `Pillow`, `imagecodecs`, `numpy` (installed automatically via `install_deps.bat`).

## Setup
1. Double-click `install_deps.bat` to install Python packages.
2. (Optional) Run `run_app.bat` to launch the app directly from source.
3. To build a standalone executable, run `build_app.bat`. The final `converter_app.exe` will be in the `dist` folder.

## Usage
1. Open the app and select the input and output folders.
2. Click **Start Service**. The app converts existing `.jxr` files in the input folder and then watches for new ones.
3. Logs appear in the window and are also written to `conversion.log` inside the output folder.

### Example `conversion.log`
```text
2025-06-04 12:00:00,000 - INFO - Converted sample.jxr -> sample.jpg
```

## Troubleshooting
- **Multiple watchers** – The app prevents starting a second watcher while one is already running.

## PyInstaller Command
The build script runs:
```bash
pyinstaller --noconfirm --onefile --windowed converter_app.py
```
This packages the Python GUI into a single Windows executable with no additional dependencies required at runtime.
