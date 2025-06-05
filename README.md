# JXR to JPEG Converter

A simple Windows tool that watches a folder for new `.jxr` images and converts them to `.jpg`. The conversion uses the [`imagecodecs`](https://pypi.org/project/imagecodecs/) library, so no external executables are required. The GUI now supports starting and stopping the watcher, tray minimization, optional recursive watching, and embedding an HDR P3 profile.

> **Note**
> The previous version relied on `jxr2jpg.exe`. Conversion is now handled natively via `imagecodecs`.

## Requirements
- Python 3.12 when running from source (not needed for the built exe).
- Python packages: `watchdog`, `Pillow`, `imagecodecs`, `numpy`, `pystray` (installed automatically via `install_deps.bat`).

## Setup
1. Double-click `install_deps.bat` to install Python packages.
2. (Optional) Run `run_app.bat` to launch the app directly from source.
3. To build a standalone executable, run `build_app.bat`. The final `converter_app.exe` will be in the `dist` folder.
4. (Optional) Use `--hdr-p3` with `jxr_to_jpeg.py` to embed the HDR P3 profile.

## Usage
1. Open the app and select the input and output folders.
2. Click **Start Service**. The app converts existing `.jxr` files in the input folder and then watches for new ones. Press **Stop Service** to halt.
3. Settings (folders, options) are saved in `settings.json` so the next launch remembers them. Logs appear in the window and are also written to `conversion.log` inside the output folder.
4. Enabling **Launch on boot** creates a shortcut in the user Startup folder.

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

## Installer
An example `installer.nsi` script is provided for [NSIS](https://nsis.sourceforge.io/) to create a Windows installer. It installs the standalone exe without touching system Python and supports a `/PORTABLE` switch for portable mode.

## Publishing
1. Commit your code and push to GitHub.
2. Build `converter_app.exe` and run the NSIS script to produce `installer.exe`.
3. Tag a release, e.g. `git tag v1.0.0 && git push --tags`, and upload `installer.exe` on the GitHub release page.
