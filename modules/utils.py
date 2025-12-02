#!/usr/bin/env python3
"""
Utility functions for T-SLYTHERINS
"""

import os
import subprocess
import shlex
from pathlib import Path
from shutil import which

def launch_module_in_terminal(module_cmd: list, logfile: str, donefile: str, title: str = None):
    """Launch module_cmd in GUI terminal, log output, create donefile"""
    # Ensure dirs
    os.makedirs(os.path.dirname(logfile) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(donefile) or ".", exist_ok=True)
    
    # Clean up old donefile
    if os.path.exists(donefile):
        os.remove(donefile)
    
    # Wrapper to run command, log, create donefile
    wrapper_cmd = ' '.join([shlex.quote(arg) for arg in module_cmd]) + \
                  f" 2>&1 | tee -a {shlex.quote(logfile)}; " \
                  f"echo 'Module completed at $(date)' > {shlex.quote(donefile)}"
    
    candidates = [
        ["xfce4-terminal", "--hold", "-T", title or "T-SLYTHERINS", "-e", "bash", "-c", wrapper_cmd],
        ["xterm", "-hold", "-title", title or "T-SLYTHERINS", "-e", "bash", "-c", wrapper_cmd],
        ["gnome-terminal", "--", "bash", "-c", wrapper_cmd],
        ["konsole", "-e", "bash", "-c", wrapper_cmd],
    ]
    
    for cmd in candidates:
        try:
            p = subprocess.Popen(cmd, start_new_session=True)
            return p
        except FileNotFoundError:
            continue
    
    # Fallback: run in background without terminal
    print(f"[!] No terminal found, running {module_cmd[0]} in background")
    try:
        with open(logfile, 'a') as log_f:
            p = subprocess.Popen(
                module_cmd,
                stdout=log_f,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
            return p
    except Exception as e:
        print(f"[!] Failed to launch: {str(e)}")
        return None

def wait_for_done(donefile: str, poll_interval: float = 2.0, timeout: int = None):
    """Wait for donefile to appear"""
    import time
    start = time.time()
    while True:
        if os.path.exists(donefile):
            return True
        if timeout is not None and (time.time() - start) > timeout:
            return False
        time.sleep(poll_interval)

def check_required_tools(tools_list):
    """Check if required tools are installed"""
    missing = []
    for tool in tools_list:
        if not which(tool):
            missing.append(tool)
    return missing
