#!/usr/bin/env python3
"""
Utility functions for T-SLYTHERINS
Handles terminal launching and process management
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
    # Ensure directories exist
    os.makedirs(os.path.dirname(logfile) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(donefile) or ".", exist_ok=True)
    
    # Clean up old donefile
    if os.path.exists(donefile):
        os.remove(donefile)
    
    # Create wrapper command that runs the module, logs output, and creates done file
    wrapper_cmd = ' '.join([shlex.quote(arg) for arg in module_cmd]) + \
                  f" 2>&1 | tee -a {shlex.quote(logfile)}; " \
                  f"echo 'Module completed at $(date)' > {shlex.quote(donefile)}; " \
                  f"echo 'Press any key to close...'; read -n1 -s"
    
    # Different terminal emulators require different argument formats
    terminal_candidates = [
        # xfce4-terminal - Kali Linux default
        ["xfce4-terminal", "--hold", "--title", title or "T-SLYTHERINS", "-x", "bash", "-c", wrapper_cmd],
        # xterm - Universal, always available
        ["xterm", "-hold", "-title", title or "T-SLYTHERINS", "-e", "bash", "-c", wrapper_cmd],
        # gnome-terminal - Ubuntu/Gnome
        ["gnome-terminal", "--", "bash", "-c", wrapper_cmd],
        # konsole - KDE
        ["konsole", "-e", "bash", "-c", wrapper_cmd],
        # mate-terminal - MATE desktop
        ["mate-terminal", "--command", f"bash -c '{wrapper_cmd}'"],
        # terminator
        ["terminator", "-x", f"bash -c '{wrapper_cmd}'"],
    ]
    
    # Try each terminal emulator until one works
    for cmd in terminal_candidates:
        try:
            # Check if this terminal exists on the system
            if not which(cmd[0]):
                continue
            
            # Try to launch the terminal
            p = subprocess.Popen(cmd, start_new_session=True)
            print(f"[*] Launched module in {cmd[0]}")
            return p
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"[!] Error with {cmd[0]}: {e}")
            continue
    
    # Fallback: run in background without terminal window
    print(f"[!] No terminal emulator found, running module in background")
    return run_in_background(module_cmd, logfile, donefile)

def run_in_background(module_cmd: list, logfile: str, donefile: str):
    """Run a module in the background without a terminal window"""
    try:
        # Create a shell script to run the module
        script_content = f'''#!/bin/bash
echo "Starting module at $(date)" >> {logfile}
{' '.join([shlex.quote(arg) for arg in module_cmd])} >> {logfile} 2>&1
EXIT_CODE=$?
echo "Module completed with exit code: $EXIT_CODE at $(date)" >> {logfile}
echo "Background module completed at $(date)" > {donefile}
'''
        
        # Write the script to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        # Make it executable
        os.chmod(script_path, 0o755)
        
        # Run the script in the background
        p = subprocess.Popen(['bash', script_path], start_new_session=True)
        
        # Schedule cleanup of the temp file
        def cleanup_temp_file():
            try:
                os.unlink(script_path)
            except:
                pass
        
        import atexit
        atexit.register(cleanup_temp_file)
        
        print(f"[*] Module running in background (PID: {p.pid})")
        return p
        
    except Exception as e:
        print(f"[!] Failed to run in background: {str(e)}")
        return None

def wait_for_done(donefile: str, poll_interval: float = 2.0, timeout: int = None):
    """Wait for donefile to appear with timeout"""
    import time
    
    if timeout is None:
        timeout = 7200  # Default 2 hour timeout
    
    start = time.time()
    
    while True:
        if os.path.exists(donefile):
            # Check if module actually completed (not just background start)
            with open(donefile, 'r') as f:
                content = f.read()
                if "completed" in content.lower():
                    return True
        
        if (time.time() - start) > timeout:
            print(f"[!] Timeout waiting for module after {timeout} seconds")
            return False
        
        time.sleep(poll_interval)

def check_required_tools(tools_list):
    """Check if required tools are installed"""
    missing = []
    for tool in tools_list:
        if not which(tool):
            missing.append(tool)
    return missing

def get_available_terminal():
    """Detect and return the best available terminal emulator"""
    terminals = [
        "xfce4-terminal",  # Kali Linux default
        "gnome-terminal",  # Ubuntu/Gnome
        "xterm",          # Universal fallback
        "konsole",        # KDE
        "mate-terminal",  # MATE
        "terminator",     # Advanced terminal
        "urxvt",          # rxvt-unicode
        "rxvt",           # Standard rxvt
        "lxterminal",     # LXDE
        "terminology",    # Enlightenment
    ]
    
    for term in terminals:
        if which(term):
            return term
    
    return None  # No terminal found

def check_environment():
    """Check if we're in a suitable environment"""
    issues = []
    
    # Check for DISPLAY variable (GUI environment)
    if not os.environ.get('DISPLAY'):
        issues.append("No DISPLAY variable found (not in GUI environment)")
    
    # Check for terminal emulator
    terminal = get_available_terminal()
    if not terminal:
        issues.append("No terminal emulator found")
    else:
        print(f"[✓] Terminal emulator: {terminal}")
    
    return issues

# Test function for debugging
if __name__ == "__main__":
    print("[*] Testing utils module...")
    
    terminal = get_available_terminal()
    if terminal:
        print(f"[✓] Found terminal: {terminal}")
    else:
        print("[!] No terminal found")
    
    env_issues = check_environment()
    if env_issues:
        print("[!] Environment issues:")
        for issue in env_issues:
            print(f"    - {issue}")
    else:
        print("[✓] Environment OK")
