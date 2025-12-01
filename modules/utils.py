import os
import subprocess
from pathlib import Path

def _choose_terminal_commands(bash_cmd, title=None):
    """
    Return a list of candidate terminal invocations (each is a list)
    that run bash -lc "<bash_cmd>" and keep the window open.
    """
    t = title or "T-SLYTHERINS"
    # the command will run: clear; echo title; then the command; tee logfile; create done file; prompt to close
    return [
        ["xfce4-terminal", "--hold", "-e", f"bash -lc \"{bash_cmd}\""],
        ["xterm", "-hold", "-e", "bash", "-lc", bash_cmd],
        ["gnome-terminal", "--", "bash", "-lc", bash_cmd],
        ["konsole", "-e", "bash", "-lc", bash_cmd],
    ]

def launch_module_in_terminal(module_cmd: str, logfile: str, donefile: str, title: str = None):
    """
    Launch module_cmd (a bash string) in a GUI terminal, pipe stdout/stderr to logfile,
    and create donefile when finished. This returns the Popen object or None.
    """
    # ensure directories
    os.makedirs(os.path.dirname(logfile) or ".", exist_ok=True)
    # Compose the wrapper bash command so the terminal displays output and writes donefile at the end.
    # It will also pause at the end waiting for a keypress so you can inspect it.
    safe_cmd = (
        f"clear; echo '--- {title or 'T-SLYTHERINS'} ---'; "
        f"{module_cmd} 2>&1 | tee -a {logfile}; "
        f"echo; echo '--- DONE: {title or ''} ---' ; echo DONE > {donefile}; "
        f"read -n1 -s -r -p 'Press any key to close this window...'"
    )
    candidates = _choose_terminal_commands(safe_cmd, title)
    for cmd in candidates:
        try:
            p = subprocess.Popen(cmd)
            return p
        except FileNotFoundError:
            continue
    # if no GUI terminal exists, fallback: run in background without terminal and still create donefile when done
    # create a background shell that runs the command
    try:
        bg_cmd = f"bash -lc \"{module_cmd} 2>&1 | tee -a {logfile}; echo DONE > {donefile}\""
        return subprocess.Popen(["bash", "-lc", bg_cmd])
    except Exception:
        return None

def wait_for_done(donefile: str, poll_interval: float = 1.0, timeout: int = None):
    """
    Wait for donefile to appear. Returns True if seen, False if timed out.
    """
    import time
    start = time.time()
    while True:
        if os.path.exists(donefile):
            return True
        if timeout is not None and (time.time() - start) > timeout:
            return False
        time.sleep(poll_interval)
