import json
import os
import queue
import sys
from pathlib import Path
from tkinter import (
    BooleanVar,
    END,
    Button,
    Checkbutton,
    Entry,
    Label,
    Scrollbar,
    Text,
    Tk,
    filedialog,
    messagebox,
)

import pystray
from PIL import Image as PILImage

from watcher import ConverterHandler, Watcher, setup_logger
from jxr_to_jpeg import HDR_P3_PROFILE


SETTINGS_FILE = Path("settings.json")


class App:
    def __init__(self, root: Tk) -> None:
        self.root = root
        root.title("JXR to JPEG Converter")
        root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

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

        self.recursive_var = BooleanVar(value=False)
        self.icc_var = BooleanVar(value=False)
        self.launch_var = BooleanVar(value=False)

        Checkbutton(root, text="Watch subfolders", variable=self.recursive_var).grid(
            row=2, column=0, sticky="w"
        )
        Checkbutton(root, text="Embed HDR P3", variable=self.icc_var).grid(
            row=2, column=1, sticky="w"
        )

        Button(root, text="Start Service", command=self.start_service).grid(
            row=3, column=0
        )
        Button(root, text="Stop Service", command=self.stop_service).grid(
            row=3, column=1
        )

        self.status = Label(root, text="Stopped", fg="red")
        self.status.grid(row=4, column=0, sticky="w")

        Button(root, text="Open Log", command=self.open_log).grid(row=4, column=1)

        self.log_box.grid(row=5, column=0, columnspan=2, padx=5)
        self.scroll.grid(row=5, column=2, sticky="ns")

        self.queue: queue.Queue[str] | None = None
        self.watcher: Watcher | None = None
        self.logger = None
        self.log_file: Path | None = None
        self.tray_icon: pystray.Icon | None = None
        self.root.after(200, self.process_queue)
        self.load_settings()

    def load_settings(self) -> None:
        if SETTINGS_FILE.exists():
            data = json.loads(SETTINGS_FILE.read_text())
            self.input_var.insert(0, data.get("input_dir", ""))
            self.output_var.insert(0, data.get("output_dir", ""))
            self.recursive_var.set(data.get("recursive", False))
            self.icc_var.set(data.get("icc", False))

    def save_settings(self) -> None:
        data = {
            "input_dir": self.input_var.get(),
            "output_dir": self.output_var.get(),
            "recursive": self.recursive_var.get(),
            "icc": self.icc_var.get(),
        }
        SETTINGS_FILE.write_text(json.dumps(data))

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
        if self.watcher:
            messagebox.showinfo("Service running", "Watcher already running.")
            return

        input_dir = self.input_var.get()
        output_dir = self.output_var.get()
        if not input_dir or not output_dir:
            messagebox.showerror(
                "Missing folders", "Please select input and output folders."
            )
            return

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.log_file = Path(output_dir) / "conversion.log"
        self.logger = setup_logger(self.log_file)
        self.queue = queue.Queue()

        profile = HDR_P3_PROFILE if self.icc_var.get() else None
        handler = ConverterHandler(
            input_dir,
            output_dir,
            self.queue,
            self.logger,
            icc_profile=profile,
            popup_errors=True,
        )
        for file in Path(input_dir).glob("*.jxr"):
            handler._convert(str(file))
        for file in Path(input_dir).glob("*.JXR"):
            handler._convert(str(file))

        self.watcher = Watcher(input_dir, handler, self.recursive_var.get())
        self.watcher.start()
        self.status.config(text="Watching", fg="green")
        self.log("Watching for .jxr files in " + input_dir)
        self.save_settings()
        self.update_startup()

    def stop_service(self) -> None:
        if self.watcher:
            self.watcher.stop()
            self.watcher = None
            self.status.config(text="Stopped", fg="red")
            self.save_settings()
            self.update_startup()

    def open_log(self) -> None:
        if self.log_file and self.log_file.exists():
            os.startfile(self.log_file)

    def minimize_to_tray(self) -> None:
        if self.tray_icon:
            return
        self.root.withdraw()
        image = PILImage.new("RGB", (64, 64), color="white")
        self.tray_icon = pystray.Icon(
            "jxr",
            image,
            "JXR Converter",
            menu=pystray.Menu(
                pystray.MenuItem("Show", self.show_window),
                pystray.MenuItem("Quit", self.quit_app),
            ),
        )
        self.tray_icon.run_detached()

    def show_window(self) -> None:
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.root.deiconify()

    def quit_app(self) -> None:
        self.stop_service()
        self.save_settings()
        self.root.destroy()

    def update_startup(self) -> None:
        startup_dir = (
            Path(os.getenv("APPDATA", ""))
            / "Microsoft"
            / "Windows"
            / "Start Menu"
            / "Programs"
            / "Startup"
        )
        link = startup_dir / "JXRConverter.cmd"
        if self.launch_var.get():
            startup_dir.mkdir(parents=True, exist_ok=True)
            link.write_text(f'"{Path(sys.argv[0]).resolve()}"\n')
        elif link.exists():
            link.unlink()

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
