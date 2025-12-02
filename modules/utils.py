#!/usr/bin/env python3
"""
Utility functions for T-SLYTHERINS
"""

import os
import subprocess
import shlex
import sys
import tempfile
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
                  f"echo 'Module completed at $(date)' > {shlex.quote(donefile)}; " \
                  f"echo 'Press any key to close...'; read -n1 -s"
    
    # Different terminals have different argument formats
    candidates = [
        # xfce4-terminal - uses -x for command (not -c)
        ["xfce4-terminal", "--hold", "--title", title or "T-SLYTHERINS", "-x", "bash", "-c", wrapper_cmd],
        # xterm - uses -e for command
        ["xterm", "-hold", "-title", title or "T-SLYTHERINS", "-e", "bash", "-c", wrapper_cmd],
        # gnome-terminal - uses -- to separate options from command
        ["gnome-terminal", "--", "bash", "-c", wrapper_cmd],
        # konsole - uses -e
        ["konsole", "-e", "bash", "-c", wrapper_cmd],
        # mate-terminal
        ["mate-terminal", "--command", f"bash -c '{wrapper_cmd}'"],
        # terminator
        ["terminator", "-x", f"bash -c '{wrapper_cmd}'"],
    ]
    
    for cmd in candidates:
        try:
            # Check if terminal exists
            if not which(cmd[0]):
                continue
            
            print(f"[*] Trying terminal: {cmd[0]}")
            p = subprocess.Popen(cmd, start_new_session=True)
            return p
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"[!] Error with {cmd[0]}: {e}")
            continue
    
    # Fallback: run in background without terminal
    print(f"[!] No supported terminal found, running {module_cmd[0]} in background")
    try:
        with open(logfile, 'a') as log_f:
            p = subprocess.Popen(
                module_cmd,
                stdout=log_f,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
            
            # Create done file immediately for background processes
            with open(donefile, 'w') as df:
                df.write(f"Module running in background at $(date)\n")
            
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
            # Read the donefile to check if it's actually complete
            with open(donefile, 'r') as f:
                content = f.read()
                if "Module completed" in content or "Press any key" in content:
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

def get_terminal_emulator():
    """Get the best available terminal emulator"""
    terminals = [
        "xfce4-terminal",
        "gnome-terminal",
        "xterm", 
        "konsole",
        "mate-terminal",
        "terminator",
        "urxvt",
        "rxvt",
        "lxterminal",
        "terminology"
    ]
    
    for term in terminals:
        if which(term):
            return term
    return None

# Simple test function
def test_terminals():
    """Test available terminals"""
    print("[*] Testing available terminals...")
    term = get_terminal_emulator()
    if term:
        print(f"[✓] Found terminal: {term}")
        return term
    else:
        print("[!] No terminal emulator found")
        return None
