import os
import subprocess

def start_snake_terminal():
    snake_script = "/tmp/t_slytherins_snake.sh"
    with open(snake_script, "w") as f:
        f.write("""#!/bin/bash
frames=( "🐍      " "  🐍    " "    🐍  " "      🐍" "    🐍  " "  🐍    " )
while true; do
  for frame in "${frames[@]}"; do
    echo -ne "\\r$frame SLITHERING..."
    sleep 0.12
  done
done
""")
    os.chmod(snake_script, 0o755)
    # Try common GUI terminals:
    candidates = [
        ["xfce4-terminal", "--hold", "-e", snake_script],
        ["xterm", "-hold", "-e", snake_script],
        ["gnome-terminal", "--", snake_script],
        ["konsole", "-e", snake_script],
    ]
    for cmd in candidates:
        try:
            p = subprocess.Popen(cmd)
            return p
        except FileNotFoundError:
            continue
    return None
