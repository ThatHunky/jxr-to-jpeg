# JXR to HEIC Converter

A simple Windows tool that watches a folder for new `.jxr` images and converts them to `.heic`. It relies on the open-source **jxr2jpg** utility to decode JPEG XR files and the `pillow-heif` library to encode HEIC. Color profiles and HDR data are preserved automatically.


> **Note**
> The previously linked `jxr2jpg` project is no longer available on GitHub. A convenient alternative is the [jxr_to_png](https://github.com/ledoge/jxr_to_png) tool which can decode JPEG XR files. You can convert `.jxr` to `.png` with it and then to `.heic` using the app.

## Requirements

- `jxr2jpg.exe` – if you still have a copy of the original tool place it next to the app or somewhere in your `PATH`. Otherwise download the [jxr_to_png](https://github.com/ledoge/jxr_to_png) release and rename the executable to `jxr2jpg.exe`.
- Python 3.12 when running from source (not needed for the built exe).
- Python packages: `watchdog`, `Pillow`, `pillow-heif` (installed automatically via `install_deps.bat`).

## Setup

1. Double-click `install_deps.bat` to install Python packages and verify that `jxr2jpg.exe` is available.
2. (Optional) Run `run_app.bat` to launch the app directly from source.
3. To build a standalone executable, run `build_app.bat`. The final `converter_app.exe` will be in the `dist` folder.

## Usage

1. Open the app and select the input and output folders.
2. Click **Start Service**. The app converts any existing `.jxr` files in the input folder and then watches for new ones.
3. Logs appear in the window and are also written to `conversion.log` inside the output folder.

HDR information is preserved in the generated `.heic` images.

### Example `conversion.log`

```
2025-06-04 12:00:00,000 - INFO - Converted sample.jxr -> sample.heic
2025-06-04 12:00:05,000 - INFO - Converted hdr_image.jxr -> hdr_image.heic
```

## Troubleshooting

- **Missing `jxr2jpg.exe`** – The app will show a popup if the converter is not found. Download `jxr_to_png` from GitHub and rename the binary to `jxr2jpg.exe` before placing it next to the `.exe`.

- **Multiple watchers** – The app prevents starting a second watcher while one is already running.

## PyInstaller Command

The build script runs:

```
pyinstaller --noconfirm --onefile --windowed converter_app.py
```

This packages the Python GUI into a single Windows executable with no additional dependencies required at runtime.

