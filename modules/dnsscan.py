import os
from pathlib import Path
from .utils import launch_module_in_terminal, wait_for_done

OUTDIR = Path("T-SLYTHERINS-OUTPUT")

def run(domain):
    OUTDIR.mkdir(exist_ok=True)
    logs = {}
    # amass
    amass_log = str(OUTDIR / "amass.log")
    amass_done = str(OUTDIR / "amass.done")
    amass_cmd = f"amass enum -passive -d {domain}"
    launch_module_in_terminal(amass_cmd, amass_log, amass_done, title="amass")
    logs["amass"] = (amass_log, amass_done)

    # subfinder
    subfinder_log = str(OUTDIR / "subfinder.log")
    subfinder_done = str(OUTDIR / "subfinder.done")
    subfinder_cmd = f"subfinder -silent -d {domain} -o {OUTDIR / 'subfinder.txt'}"
    launch_module_in_terminal(subfinder_cmd, subfinder_log, subfinder_done, title="subfinder")
    logs["subfinder"] = (subfinder_log, subfinder_done)

    # assetfinder
    asset_log = str(OUTDIR / "assetfinder.log")
    asset_done = str(OUTDIR / "assetfinder.done")
    asset_cmd = f"assetfinder {domain}"
    launch_module_in_terminal(asset_cmd, asset_log, asset_done, title="assetfinder")
    logs["assetfinder"] = (asset_log, asset_done)

    # Wait for completion
    for name, (log, done) in logs.items():
        print(f"\n[+] Waiting for {name} to finish (log: {log})")
        wait_for_done(done)
        print(f"[+] {name} done.")
    # Merge outputs into all_subdomains.txt
    all_subs = OUTDIR / "all_subdomains.txt"
    with open(all_subs, "w", encoding="utf-8") as out:
        # accumulate from specific outputs
        candidates = [OUTDIR / "subfinder.txt", OUTDIR / "amass.log", OUTDIR / "assetfinder.log"]
        seen = set()
        for p in candidates:
            if not p.exists():
                continue
            for line in open(p, "r", encoding="utf-8", errors="ignore"):
                s = line.strip()
                if not s:
                    continue
                # some logs contain extra text; keep heuristics: lines with dots
                if "." in s and s not in seen:
                    seen.add(s)
                    out.write(s + "\n")
    print(f"[+] Subdomain collection complete: {all_subs}")
    return str(all_subs)
