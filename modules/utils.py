import os
import subprocess
from pathlib import Path

def launch_module_in_terminal(module_cmd: list, logfile: str, donefile: str, title: str = None):
    """Launch module_cmd (list) in GUI terminal, log output, create donefile"""
    # Ensure dirs
    os.makedirs(os.path.dirname(logfile) or ".", exist_ok=True)
    
    # Wrapper to run command, log, create donefile
    wrapper_cmd = ' '.join([shlex.quote(arg) for arg in module_cmd]) + f" 2>&1 | tee -a {shlex.quote(logfile)}; echo DONE > {shlex.quote(donefile)}; read -n1 -s -r -p 'Press any key to close...'"
    
    candidates = [
        ["xfce4-terminal", "--hold", "-e", "bash", "-lc", wrapper_cmd],
        ["xterm", "-hold", "-e", "bash", "-lc", wrapper_cmd],
        ["gnome-terminal", "--", "bash", "-lc", wrapper_cmd],
        ["konsole", "-e", "bash", "-lc", wrapper_cmd],
    ]
    
    for cmd in candidates:
        try:
            p = subprocess.Popen(cmd)
            return p
        except FileNotFoundError:
            continue
    
    # Fallback: background run
    try:
        bg_cmd = f"bash -lc '{wrapper_cmd}' &"
        return subprocess.Popen(bg_cmd, shell=True)
    except Exception as e:
        print(f"[!] Failed to launch: {str(e)}", file=sys.stderr)
        return None

def wait_for_done(donefile: str, poll_interval: float = 1.0, timeout: int = None):
    """Wait for donefile"""
    import time
    start = time.time()
    while True:
        if os.path.exists(donefile):
            return True
        if timeout is not None and (time.time() - start) > timeout:
            return False
        time.sleep(poll_interval)
