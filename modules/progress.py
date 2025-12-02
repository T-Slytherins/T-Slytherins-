#!/usr/bin/env python3
"""
Progress Spinner for T-SLYTHERINS
Simple and effective progress tracking
"""

import threading
import time
import sys
import atexit

class Spinner:
    def __init__(self):
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.idx = 0
        self.running = False
        self.lock = threading.Lock()
        self.modules = {}
        self.thread = None
        
        # Register cleanup
        atexit.register(self.cleanup)
    
    def start(self):
        """Start the spinner animation"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the spinner animation"""
        if not self.running:
            return
        
        self.running = False
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        
        # Clear the line
        self._clear_line()
    
    def _clear_line(self):
        """Clear the current terminal line"""
        sys.stdout.write("\r" + " " * 100 + "\r")
        sys.stdout.flush()
    
    def set_module_running(self, name, val: bool):
        """Set a module's running status"""
        with self.lock:
            self.modules[name] = val
    
    def _progress_pct(self):
        """Calculate progress percentage"""
        with self.lock:
            total = len(self.modules)
            if total == 0:
                return 0
            completed = sum(1 for v in self.modules.values() if not v)
            return int((completed / total) * 100)
    
    def _spin(self):
        """Main spinner animation loop"""
        while self.running:
            with self.lock:
                active = [n for n, r in self.modules.items() if r]
            
            frame = self.frames[self.idx % len(self.frames)]
            self.idx += 1
            pct = self._progress_pct()
            
            if active:
                status = ", ".join(active)
                # Limit status length to avoid terminal wrapping
                if len(status) > 50:
                    status = status[:47] + "..."
                sys.stdout.write(f"\r{frame} [{pct:3d}%] Running: {status}    ")
            else:
                sys.stdout.write(f"\r{frame} [{pct:3d}%] Idle.                     ")
            
            sys.stdout.flush()
            time.sleep(0.12)
        
        # Clear when done
        self._clear_line()
    
    def cleanup(self):
        """Clean up resources"""
        self.stop()
