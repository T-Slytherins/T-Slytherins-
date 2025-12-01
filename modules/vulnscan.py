from pathlib import Path
from .utils import launch_module_in_terminal, wait_for_done

OUTDIR = Path("T-SLYTHERINS-OUTPUT")

def run(all_subs_file: str):
    OUTDIR.mkdir(exist_ok=True)
    nuclei_log = str(OUTDIR / "nuclei.log")
    nuclei_done = str(OUTDIR / "nuclei.done")
    cmd = f"nuclei -l {all_subs_file} -o {nuclei_log} -retries 1"
    launch_module_in_terminal(cmd, nuclei_log, nuclei_done, title="nuclei")
    print(f"[+] Waiting for nuclei to finish...")
    wait_for_done(nuclei_done)
    print("[+] nuclei finished.")
    return nuclei_log
