import os
from pathlib import Path
from datetime import datetime

OUTDIR = Path("T-SLYTHERINS-OUTPUT")

def generate(all_subs_file: str, nmap_prefix: str, nuclei_log: str, aquatone_dir: str, thumbnails: list):
    report = OUTDIR / "report.html"
    now = datetime.utcnow().isoformat() + "Z"
    subs = []
    if Path(all_subs_file).exists():
        subs = [l.strip() for l in open(all_subs_file, "r", encoding="utf-8") if l.strip()]

    # nmap preview
    nmap_text = ""
    try:
        nmap_nmap = Path(nmap_prefix + ".nmap")
        if nmap_nmap.exists():
            nmap_text = "\n".join(open(nmap_nmap, "r", encoding="utf-8").read().splitlines()[:400])
    except Exception:
        nmap_text = ""

    nuclei_text = ""
    if Path(nuclei_log).exists():
        nuclei_text = "\n".join(open(nuclei_log, "r", encoding="utf-8").read().splitlines()[:400])

    # Build thumbnails gallery markup (relative paths)
    gallery_html = ""
    for t in thumbnails:
        rel = os.path.relpath(t, OUTDIR)
        gallery_html += f'<div style="display:inline-block;margin:8px"><a href="{rel}"><img src="{rel}" style="width:320px;height:auto;border:1px solid #333"></a></div>\n'

    html = f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>T-SLYTHERINS Report</title></head>
<body style="background:#0b0f14;color:#e6eef6;font-family:Arial;padding:18px">
<h1 style="color:#6ee7b7">T-SLYTHERINS Recon Report</h1>
<p>Generated: {now}</p>

<section style="background:#071022;padding:12px;border-radius:8px;margin-bottom:12px">
<h2>Subdomains ({len(subs)})</h2>
<ul>{"".join(f"<li>{s}</li>" for s in subs[:1000])}</ul>
</section>

<section style="background:#071022;padding:12px;border-radius:8px;margin-bottom:12px">
<h2>Nmap (preview)</h2>
<pre style="white-space:pre-wrap;max-height:300px;overflow:auto;background:#00111a;padding:8px;color:#bfe6ff">{nmap_text or 'Nmap output not available.'}</pre>
</section>

<section style="background:#071022;padding:12px;border-radius:8px;margin-bottom:12px">
<h2>Nuclei (preview)</h2>
<pre style="white-space:pre-wrap;max-height:300px;overflow:auto;background:#00111a;padding:8px;color:#bfe6ff">{nuclei_text or 'No nuclei output.'}</pre>
</section>

<section style="background:#071022;padding:12px;border-radius:8px;margin-bottom:12px">
<h2>Screenshots (thumbnails)</h2>
{gallery_html or '<p>No thumbnails found.</p>'}
</section>

</body>
</html>
"""
    with open(report, "w", encoding="utf-8") as fh:
        fh.write(html)
    return str(report)
