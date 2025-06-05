import logging
import os
import queue
import threading
import time
from pathlib import Path
from typing import Optional

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from jxr_to_jpeg import convert_jxr_to_jpeg


class ConverterHandler(PatternMatchingEventHandler):
    """Handle new JXR files and convert them to JPEG."""

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        q: queue.Queue,
        logger: logging.Logger,
        icc_profile: Optional[str] = None,
        popup_errors: bool = False,
    ) -> None:
        super().__init__(patterns=["*.jxr", "*.JXR"], ignore_directories=True)
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.queue = q
        self.logger = logger
        self.icc_profile = icc_profile
        self.popup_errors = popup_errors

    def on_created(self, event) -> None:
        self._convert(event.src_path)

    def on_moved(self, event) -> None:
        self._convert(event.dest_path)

    def _convert(self, src: str) -> None:
        name = os.path.basename(src)
        out_name = os.path.splitext(name)[0] + ".jpg"
        out_path = os.path.join(self.output_dir, out_name)
        try:
            convert_jxr_to_jpeg(src, out_path, icc_profile=self.icc_profile)
            msg = f"Converted {name} -> {out_name}"
        except Exception as exc:  # pragma: no cover - error path
            msg = f"Failed to convert {name}: {exc}"
            self.logger.error(msg)
            if self.popup_errors:
                from tkinter import messagebox

                messagebox.showerror("Conversion failed", msg)
            self.queue.put(msg)
            return
        self.logger.info(msg)
        self.queue.put(msg)


def setup_logger(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("converter")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(log_file, encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


class Watcher:
    """Manage background observer thread."""

    def __init__(
        self, input_dir: str, handler: ConverterHandler, recursive: bool
    ) -> None:
        self.input_dir = input_dir
        self.handler = handler
        self.recursive = recursive
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()
            self._stop_event.clear()

    def _run(self) -> None:
        observer = Observer()
        observer.schedule(self.handler, self.input_dir, recursive=self.recursive)
        observer.start()
        try:
            while not self._stop_event.is_set():
                time.sleep(0.5)
        finally:
            observer.stop()
            observer.join()
