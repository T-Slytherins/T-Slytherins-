#!/usr/bin/env python3

import os
import subprocess
import shutil
import sys
import time
import signal
from pathlib import Path
from threading import Thread
from tqdm import tqdm
from PIL import Image

# ----------------------------
# Configuration
# ----------------------------
BASE_DIR = Path(__file__).parent.resolve()
VENV_DIR = BASE_DIR / "venv"
PYTHON_EXEC = VENV_DIR / "bin" / "python"
OUTPUT_DIR = BASE_DIR / "T-SLYTHERINS-OUTPUT"
OUTPUT_DIR.mkdir(exist_ok=True)

# Modules and commands
MODULES = {
    "amass": ["amass", "enum", "-passive", "-d"],
    "subfinder": ["subfinder", "-silent", "-d"],
    "assetfinder": ["assetfinder"],
    "httpx": ["httpx", "-l"],
    "katana": ["katana", "-list"],
    "dnsscan": ["dnsscan"],
    "aquatone": ["aquatone", "-scan"],
    "snake": [str(PYTHON_EXEC), "snake_animation.py"]
}

LOG_FILES = {name: OUTPUT_DIR / f"{name}.log" for name in MODULES}

GREEN = "\033[92m"
RESET = "\033[0m"

processes = []
module_status = {name: "Pending" for name in MODULES}

# ----------------------------
# Virtual environment
# ----------------------------
if not VENV_DIR.exists():
    print("[!] Virtual environment not found, creating venv...")
    subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)

# Upgrade pip inside venv
subprocess.run([str(PYTHON_EXEC), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel", "tqdm", "pillow"], stdout=subprocess.DEVNULL)

# ----------------------------
# Banner
# ----------------------------
def banner():
    print(GREEN + r"""
 _______      _______        __   __ _______ _     _ _______  ______ _____ __   _ _______
    |         |______ |        \_/      |    |_____| |______ |_____/   |   | \  | |______
    |         ______| |_____    |       |    |     | |______ |    \_ __|__ |  \_| ______|

      T  S L Y T H E R I N S   R E C O N   S U I T E
        Owned by T-Slytherins ~ Crafted by Pr0fessor_SnApe
    """ + RESET)

# ----------------------------
# Open terminal
# ----------------------------
def open_terminal(module_name, cmd):
    logfile = LOG_FILES[module_name]
    logfile.parent.mkdir(parents=True, exist_ok=True)
    terminal_cmd = [
        "xfce4-terminal",
        "--title", module_name,
        "--hold",
        "--disable-server",
        "--command",
        f"bash -c ' {' '.join(cmd)} &> {logfile}; exec bash'"
    ]
    proc = subprocess.Popen(terminal_cmd)
    processes.append((module_name, proc))
    module_status[module_name] = "Running"
    proc.wait()
    module_status[module_name] = "Completed"

# ----------------------------
# Progress bar monitor
# ----------------------------
def show_progress():
    with tqdm(total=len(MODULES), desc="Modules", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} Modules") as pbar:
        completed = 0
        while completed < len(MODULES):
            new_completed = sum(1 for status in module_status.values() if status == "Completed")
            pbar.update(new_completed - completed)
            completed = new_completed
            time.sleep(1)

# ----------------------------
# Screenshot + thumbnail
# ----------------------------
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"
THUMB_DIR = OUTPUT_DIR / "thumbnails"
SCREENSHOT_DIR.mkdir(exist_ok=True)
THUMB_DIR.mkdir(exist_ok=True)

def take_screenshots():
    for file in LOG_FILES.values():
        # Example: generate empty placeholder screenshot
        img_path = SCREENSHOT_DIR / f"{file.stem}.png"
        img = Image.new("RGB", (800, 600), color=(73, 109, 137))
        img.save(img_path)
        # generate thumbnail
        thumb_path = THUMB_DIR / f"{file.stem}_thumb.png"
        img.thumbnail((160, 120))
        img.save(thumb_path)

# ----------------------------
# HTML Report Generator
# ----------------------------
REPORT_FILE = OUTPUT_DIR / "report.html"
def generate_html_report():
    html_content = "<html><head><title>T-SLYTHERINS Recon Report</title></head><body>"
    html_content += "<h1>T-SLYTHERINS Recon Report</h1><ul>"
    for module, logfile in LOG_FILES.items():
        html_content += f"<li><h2>{module}</h2>"
        html_content += f"<pre>{logfile.read_text()[:500]}...</pre>"  # snippet
        thumb = THUMB_DIR / f"{module}_thumb.png"
        if thumb.exists():
            html_content += f'<img src="thumbnails/{thumb.name}" alt="{module} thumbnail"/><br>'
        html_content += "</li>"
    html_content += "</ul></body></html>"
    REPORT_FILE.write_text(html_content)

# ----------------------------
# Graceful shutdown
# ----------------------------
def signal_handler(sig, frame):
    print("\n[!] Terminating all modules...")
    for _, proc in processes:
        try:
            proc.terminate()
        except Exception:
            pass
    print("[✔] All modules terminated.")
    exit(0)

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    banner()
    target = input(GREEN + "Enter target domain: " + RESET).strip()

    # Start progress bar in background
    progress_thread = Thread(target=show_progress, daemon=True)
    progress_thread.start()

    # Launch all modules
    threads = []
    for module_name, base_cmd in MODULES.items():
        if module_name in ["amass", "subfinder", "assetfinder", "httpx", "katana"]:
            cmd = base_cmd + [target]
        else:
            cmd = base_cmd
        t = Thread(target=open_terminal, args=(module_name, cmd))
        t.start()
        threads.append(t)
        time.sleep(0.5)

    # Wait all to finish
    for t in threads:
        t.join()

    # Generate screenshots & thumbnails
    take_screenshots()
    # Generate HTML report
    generate_html_report()

    print(GREEN + "[✔] Recon complete. HTML report generated!" + RESET)
    print(GREEN + f"[✔] Output directory: {OUTPUT_DIR}" + RESET)
