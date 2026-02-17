import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
import urllib.request
import json
import tempfile

APP_VERSION = "v1.1"
GITHUB_USER = "nachocett03"
GITHUB_REPO = "gymTracker"
EXE_NAME    = "GymTracker.exe"

RELEASES_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"


def get_latest_release():
    try:
        req = urllib.request.Request(
            RELEASES_URL,
            headers={"User-Agent": "GymTracker-Updater"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())

        tag = data.get("tag_name", "")
        url = None
        for asset in data.get("assets", []):
            if asset["name"].lower() == EXE_NAME.lower():
                url = asset["browser_download_url"]
                break

        return tag, url
    except Exception:
        return None, None


def download_update(url, progress_callback):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".exe")
    tmp.close()

    def reporthook(count, block_size, total_size):
        if total_size > 0:
            pct = min(100, int(count * block_size * 100 / total_size))
            progress_callback(pct)

    urllib.request.urlretrieve(url, tmp.name, reporthook)
    return tmp.name


def apply_update_and_restart(new_exe_path):
    current_exe = sys.executable if getattr(sys, "frozen", False) else None

    if current_exe is None:
        subprocess.Popen([new_exe_path])
        sys.exit(0)

    bat_content = f"""@echo off
ping 127.0.0.1 -n 3 >nul
move /Y "{new_exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
    bat_path = os.path.join(tempfile.gettempdir(), "gym_update.bat")
    with open(bat_path, "w") as f:
        f.write(bat_content)

    subprocess.Popen(["cmd", "/c", bat_path], creationflags=subprocess.CREATE_NO_WINDOW)
    sys.exit(0)


class UpdaterWindow:

    BG           = "lightgray"
    FG_TITLE     = "#000000"
    FG_STATUS    = "#444444"
    FG_VERSION   = "#777777"
    PROGRESS_BG  = "#4a90d9"
    PROGRESS_TRO = "#cccccc"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pesos Picados")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)
        self._center()
        self._build_ui()
        self.should_continue = False

    def _center(self):
        self.root.update_idletasks()
        w, h = 400, 200
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Update.Horizontal.TProgressbar",
            troughcolor=self.PROGRESS_TRO,
            background=self.PROGRESS_BG,
            thickness=12
        )

        header = tk.Frame(self.root, bg=self.BG, bd=2, relief=tk.SOLID)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="Pesos Picados",
            font=("Arial", 20, "bold"),
            bg=self.BG,
            fg=self.FG_TITLE
        ).pack(side=tk.LEFT, padx=15, pady=10)

        tk.Label(
            header,
            text=APP_VERSION,
            font=("Arial", 9),
            bg=self.BG,
            fg=self.FG_VERSION
        ).pack(side=tk.RIGHT, padx=15, pady=10)

        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill=tk.BOTH, expand=True, padx=30, pady=16)

        self.status_var = tk.StringVar(value="Buscando actualizaciones...")
        tk.Label(
            body,
            textvariable=self.status_var,
            font=("Arial", 10),
            bg=self.BG,
            fg=self.FG_STATUS
        ).pack(anchor="w", pady=(0, 8))

        self.progress = ttk.Progressbar(
            body,
            style="Update.Horizontal.TProgressbar",
            orient="horizontal",
            length=340,
            mode="indeterminate"
        )
        self.progress.pack(fill=tk.X)
        self.progress.start(10)

    def set_status(self, text):
        self.root.after(0, lambda: self.status_var.set(text))

    def set_progress_determinate(self, pct):
        def _update():
            self.progress.stop()
            self.progress.config(mode="determinate", value=pct, maximum=100)
        self.root.after(0, _update)

    def close_and_continue(self):
        self.should_continue = True
        self.root.after(0, self.root.destroy)

    def run_check(self):
        thread = threading.Thread(target=self._check_logic, daemon=True)
        thread.start()
        self.root.mainloop()
        return self.should_continue

    def _check_logic(self):
        self.set_status("Conectando con GitHub...")
        latest_tag, download_url = get_latest_release()

        if latest_tag is None:
            self.set_status("Sin conexión. Iniciando...")
            self.root.after(1200, self.close_and_continue)
            return

        if latest_tag == APP_VERSION:
            self.set_status(f"✓ Estás al día ({APP_VERSION})")
            self.root.after(1000, self.close_and_continue)
            return

        if download_url is None:
            self.set_status("Actualización disponible (descargala manualmente)")
            self.root.after(2000, self.close_and_continue)
            return

        self.set_status(f"Descargando {latest_tag}...")

        try:
            def on_progress(pct):
                self.set_progress_determinate(pct)
                self.set_status(f"Descargando {latest_tag}... {pct}%")

            new_exe = download_update(download_url, on_progress)
            self.set_status("Instalando actualización...")
            self.root.after(800, lambda: apply_update_and_restart(new_exe))

        except Exception:
            self.set_status("Error al descargar. Iniciando igual...")
            self.root.after(1500, self.close_and_continue)


def check_for_updates():
    window = UpdaterWindow()
    return window.run_check()
