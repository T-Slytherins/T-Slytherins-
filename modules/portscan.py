from pathlib import Path
from .utils import launch_module_in_terminal, wait_for_done

OUTDIR = Path("T-SLYTHERINS-OUTPUT")

def run(all_subs_file: str):
    OUTDIR.mkdir(exist_ok=True)
    nmap_prefix = OUTDIR / "nmap"
    nmap_log = str(OUTDIR / "nmap.log")
    nmap_done = str(OUTDIR / "nmap.done")
    # -oA writes nmap.nmap/.gnmap/.xml
    cmd = f"nmap -iL {all_subs_file} -Pn -sV -T4 -oA {nmap_prefix}"
    launch_module_in_terminal(cmd, nmap_log, nmap_done, title="nmap")
    print(f"[+] Waiting for nmap to finish...")
    wait_for_done(nmap_done)
    print(f"[+] nmap finished. Outputs: {nmap_prefix}.nmap {nmap_prefix}.xml")
    return str(nmap_prefix)
