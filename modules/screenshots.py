import os
from pathlib import Path
from .utils import launch_module_in_terminal, wait_for_done
from PIL import Image

OUTDIR = Path("T-SLYTHERINS-OUTPUT")
AQUA_OUT = OUTDIR / "aquatone"
THUMBS = AQUA_OUT / "thumbs"
THUMBS.mkdir(parents=True, exist_ok=True)

def run(all_subs_file: str):
    OUTDIR.mkdir(exist_ok=True)
    urls_file = OUTDIR / "urls.txt"
    httpx_log = str(OUTDIR / "httpx.log")
    httpx_done = str(OUTDIR / "httpx.done")
    # httpx produce URLs suitable for aquatone (format: scheme://host[:port]/path)
    httpx_cmd = f"httpx -l {all_subs_file} -silent -status-code -o {urls_file}"
    launch_module_in_terminal(httpx_cmd, httpx_log, httpx_done, title="httpx")
    print("[+] Waiting for httpx to finish...")
    wait_for_done(httpx_done)

    # run aquatone (Mode A uses Firefox GUI if aquatone is configured to use it)
    aquatone_log = str(OUTDIR / "aquatone.log")
    aquatone_done = str(OUTDIR / "aquatone.done")
    # aquatone reads URLs from stdin
    aqua_cmd = f"if [ -s {urls_file} ]; then cat {urls_file} | aquatone -out {AQUA_OUT}; else echo 'No URLs to screenshot'; fi"
    launch_module_in_terminal(aqua_cmd, aquatone_log, aquatone_done, title="aquatone")
    print("[+] Waiting for aquatone to finish (this will open browser windows in GUI mode)...")
    wait_for_done(aquatone_done)
    print("[+] aquatone finished.")

    # Generate thumbnails from aquatone png outputs (if present)
    thumbs = []
    try:
        pngs = list(AQUA_OUT.rglob("*.png"))
        for p in pngs:
            try:
                im = Image.open(p)
                im.thumbnail((320, 200))
                outp = THUMBS / p.name
                im.save(outp)
                thumbs.append(str(outp))
            except Exception:
                continue
    except Exception:
        pass

    print(f"[+] Thumbnails generated in {THUMBS} (count: {len(thumbs)})")
    return str(AQUA_OUT), thumbs
