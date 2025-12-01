import threading
import time

class Spinner:
    def __init__(self):
        self.frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        self.idx = 0
        self.running = False
        self.lock = threading.Lock()
        self.modules = {}
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def set_module_running(self, name, val: bool):
        with self.lock:
            self.modules[name] = val

    def _progress_pct(self):
        with self.lock:
            total = len(self.modules)
            if total == 0:
                return 0
            completed = sum(1 for v in self.modules.values() if not v)
            return int((completed / total) * 100)

    def _spin(self):
        while self.running:
            with self.lock:
                active = [n for n, r in self.modules.items() if r]
            frame = self.frames[self.idx % len(self.frames)]
            self.idx += 1
            pct = self._progress_pct()
            if active:
                status = ", ".join(active)
                print(f"\r{frame} [{pct:3d}%] Running: {status}    ", end="", flush=True)
            else:
                print(f"\r{frame} [{pct:3d}%] Idle.                     ", end="", flush=True)
            time.sleep(0.12)
        print("\r" + " " * 80 + "\r", end="", flush=True)
