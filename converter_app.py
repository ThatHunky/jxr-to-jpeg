import os
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path
from tkinter import (
    END,
    Button,
    Entry,
    Label,
    Scrollbar,
    Text,
    Tk,
    filedialog,
    messagebox,
)

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class ConverterHandler(PatternMatchingEventHandler):
    """Handle new JXR files and convert them to JPEG."""

    def __init__(
        self, input_dir: str, output_dir: str, exe: str, q: queue.Queue, logger
    ):
        super().__init__(patterns=["*.jxr", "*.JXR"], ignore_directories=True)
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.exe = exe
        self.queue = q
        self.logger = logger

    def on_created(self, event):
        self._convert(event.src_path)

    def on_moved(self, event):
        self._convert(event.dest_path)

    def _convert(self, src: str) -> None:
        name = os.path.basename(src)
        out_name = os.path.splitext(name)[0] + ".jpg"
        out_path = os.path.join(self.output_dir, out_name)
        cmd = [self.exe, src, out_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            msg = f"Converted {name} -> {out_name}"
            if "HDR" in result.stdout:
                warn = f"HDR info detected in {name}; JPEG output will be SDR"
                self.logger.warning(warn)
                msg += f"\nWARNING: {warn}"
            self.logger.info(msg)
        else:
            msg = f"Failed to convert {name}: {result.stderr.strip()}"
            self.logger.error(msg)
        self.queue.put(msg)


def setup_logger(log_file: Path):
    import logging

    logger = logging.getLogger("converter")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger


class App:
    def __init__(self, root: Tk) -> None:
        self.root = root
        root.title("JXR to JPEG Converter")

        self.input_var = Entry(root, width=50)
        self.output_var = Entry(root, width=50)
        self.log_box = Text(root, height=15, width=60, state="normal")
        self.scroll = Scrollbar(root, command=self.log_box.yview)
        self.log_box.config(yscrollcommand=self.scroll.set)

        Label(root, text="Input folder:").grid(row=0, column=0, sticky="w")
        self.input_var.grid(row=0, column=1, padx=5)
        Button(root, text="Browse", command=self.pick_input).grid(row=0, column=2)

        Label(root, text="Output folder:").grid(row=1, column=0, sticky="w")
        self.output_var.grid(row=1, column=1, padx=5)
        Button(root, text="Browse", command=self.pick_output).grid(row=1, column=2)

        Button(root, text="Start Service", command=self.start_service).grid(
            row=2, column=0, pady=10
        )

        self.log_box.grid(row=3, column=0, columnspan=2, padx=5)
        self.scroll.grid(row=3, column=2, sticky="ns")

        self.queue: queue.Queue[str] | None = None
        self.watch_thread: threading.Thread | None = None
        self.logger = None
        self.root.after(200, self.process_queue)

    def pick_input(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.input_var.delete(0, END)
            self.input_var.insert(0, folder)

    def pick_output(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.output_var.delete(0, END)
            self.output_var.insert(0, folder)

    def start_service(self) -> None:
        if self.watch_thread and self.watch_thread.is_alive():
            messagebox.showinfo("Service running", "Watcher already running.")
            return

        input_dir = self.input_var.get()
        output_dir = self.output_var.get()
        if not input_dir or not output_dir:
            messagebox.showerror(
                "Missing folders", "Please select input and output folders."
            )
            return

        exe = shutil.which("jxr2jpg.exe") or os.path.join(os.getcwd(), "jxr2jpg.exe")
        if not os.path.exists(exe):
            messagebox.showerror(
                "jxr2jpg.exe not found",
                (

                    "jxr2jpg.exe is missing. Download the jxr_to_png release from "
                    "https://github.com/ledoge/jxr_to_png, rename the executable to "
                    "jxr2jpg.exe and place it in the app folder or in your PATH."

                ),
            )
            return

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        log_file = Path(output_dir) / "conversion.log"
        self.logger = setup_logger(log_file)
        self.queue = queue.Queue()

        self.watch_thread = threading.Thread(
            target=self.watch, args=(input_dir, output_dir, exe), daemon=True
        )
        self.watch_thread.start()
        self.log("Watching for .jxr files in " + input_dir)

    def watch(self, input_dir: str, output_dir: str, exe: str) -> None:
        handler = ConverterHandler(input_dir, output_dir, exe, self.queue, self.logger)
        observer = Observer()
        observer.schedule(handler, input_dir, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()

    def process_queue(self) -> None:
        if self.queue:
            while not self.queue.empty():
                msg = self.queue.get()
                self.log(msg)
        self.root.after(200, self.process_queue)

    def log(self, message: str) -> None:
        self.log_box.insert(END, message + "\n")
        self.log_box.see(END)


def main() -> None:
    root = Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
