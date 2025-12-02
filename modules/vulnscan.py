#!/usr/bin/env python3
import sys, subprocess, os, json
from pathlib import Path
from shutil import which

class VulnerabilityScanner:
    def __init__(self, domain, out_dir):
        self.domain = domain
        self.out_dir = out_dir
        self.nuc_dir = f"{out_dir}/nuclei"
        Path(self.nuc_dir).mkdir(parents=True, exist_ok=True)
    
    def check_httpx_results(self):
        httpx_f = f"{self.out_dir}/httpx_results.txt"
        if os.path.exists(httpx_f):
            print(f"[✓] httpx: {httpx_f}")
            return httpx_f
        sub_f = f"{self.out_dir}/all_subdomains.txt"
        if os.path.exists(sub_f):
            print("[*] httpx on subs...")
            return self.run_httpx(sub_f)
        print("[!] No target", file=sys.stderr)
        return None
    
    def run_httpx(self, in_f):
        prep_f = self.prepare_urls(in_f)
        if not prep_f:
            return None
        httpx_out = f"{self.out_dir}/httpx_results.txt"
        cmd = ['httpx', '-l', prep_f, '-silent', '-o', httpx_out, '-timeout', '10', '-retries', '2']
        try:
            subprocess.run(cmd, timeout=600, check=True)
            if os.path.exists(httpx_out):
                with open(httpx_out, 'r') as f:
                    count = sum(1 for l in f if l.strip())
                print(f"[✓] {count} live")
                return httpx_out
            return None
        except Exception as e:
            print(f"[!] httpx err: {str(e)}", file=sys.stderr)
            return None
    
    def prepare_urls(self, in_f):
        out_f = f"{self.out_dir}/prepared_for_vuln.txt"
        try:
            with open(in_f, 'r') as inf, open(out_f, 'w') as outf:
                for line in inf:
                    url = line.strip()
                    if url and not url.startswith('#'):
                        if not url.startswith(('http://', 'https://')):
                            outf.write(f"https://{url}\n")
                        else:
                            outf.write(f"{url}\n")
            return out_f
        except Exception as e:
            print(f"[!] Prep err: {str(e)}", file=sys.stderr)
            return None
    
    def update_templates(self):
        print("[*] Updating templates...")
        try:
            subprocess.run(['nuclei', '-update-templates'], capture_output=True, timeout=300, check=True)
            print("[✓] Updated")
        except Exception as e:
            print(f"[!] Update err: {str(e)}", file=sys.stderr)
    
    def run_nuclei(self, tgt_f):
        print("[*] Scanning...")
        nuc_out = f"{self.nuc_dir}/nuclei.log"
        nuc_json = f"{self.nuc_dir}/nuclei.json"
        cmd = ['nuclei', '-l', tgt_f, '-o', nuc_out, '-jsonl', nuc_json, '-severity', 'critical,high,medium', '-rate-limit', '50', '-concurrency', '10', '-bulk-size', '25', '-timeout', '10', '-retries', '2', '-silent', '-t', 'templates/']
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            if res.returncode == 0:
                print("[✓] Completed")
                return True
            print(f"[!] Fail: {res.stderr}", file=sys.stderr)
            return False
        except subprocess.TimeoutExpired:
            print("[!] Timeout", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[!] Err: {str(e)}", file=sys.stderr)
            return False
    
    def parse_results(self):
        json_f = f"{self.nuc_dir}/nuclei.json"
        sum_f = f"{self.nuc_dir}/summary.txt"
        if not os.path.exists(json_f):
            print("[!] No JSON", file=sys.stderr)
            return
        print("[*] Parsing...")
        try:
            vulns = []
            counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
            with open(json_f, 'r') as f:
                for line in f:
                    if line.strip():
                        v = json.loads(line)
                        vulns.append(v)
                        sev = v.get('info', {}).get('severity', 'info').lower()
                        counts[sev] = counts.get(sev, 0) + 1
            with open(sum_f, 'w') as f:
                f.write(f"VULN SUMMARY FOR: {self.domain}\n{'='*60}\n\nTotal: {len(vulns)}\n")
                for k, v in counts.items():
                    f.write(f"  {k.capitalize()}: {v}\n")
                f.write("\n{'='*60}\n\nDETAILS:\n\n")
                order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
                vulns.sort(key=lambda x: order.get(x.get('info', {}).get('severity', 'info').lower(), 5))
                for v in vulns:
                    info = v.get('info', {})
                    f.write(f"[{info.get('severity', 'UNKNOWN').upper()}] {info.get('name', 'Unknown')}\n")
                    f.write(f"  Template: {v.get('template-id', 'unknown')}\n")
                    f.write(f"  Target: {v.get('host', 'unknown')}\n")
                    if 'matched-at' in v:
                        f.write(f"  Matched: {v['matched-at']}\n")
                    if 'description' in info:
                        f.write(f"  Desc: {info['description']}\n")
                    f.write("\n")
            print(f"[✓] Saved: {sum_f}")
            print(f"[✓] {len(vulns)} issues")
        except json.JSONDecodeError as e:
            print(f"[!] JSON err: {str(e)}", file=sys.stderr)
        except Exception as e:
            print(f"[!] Parse err: {str(e)}", file=sys.stderr)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <out_dir>", file=sys.stderr)
        sys.exit(1)
    domain, out_dir = sys.argv[1], sys.argv[2]
    print("="*60 + f"\nVULN SCAN - {domain}\n"+"="*60)
    if not which('nuclei'):
        print("[!] No nuclei", file=sys.stderr)
        sys.exit(1)
    scanner = VulnerabilityScanner(domain, out_dir)
    scanner.update_templates()
    print()
    tgt_f = scanner.check_httpx_results()
    if not tgt_f:
        sys.exit(1)
    print()
    success = scanner.run_nuclei(tgt_f)
    if success:
        print()
        scanner.parse_results()
    print("\n[✓] Complete!")
    print(f"[*] Saved: {scanner.nuc_dir}\n"+"="*60)

if __name__ == "__main__":
    main()
