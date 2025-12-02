#!/usr/bin/env python3
"""
Vulnerability Scanning Module
Fixed httpx -l flag issue
"""

import sys
import subprocess
import os
import json
import shlex
from pathlib import Path
from shutil import which

class VulnerabilityScanner:
    def __init__(self, domain, out_dir):
        self.domain = domain
        self.out_dir = out_dir
        self.nuc_dir = f"{out_dir}/nuclei"
        Path(self.nuc_dir).mkdir(parents=True, exist_ok=True)
    
    def check_httpx_results(self):
        """Check for existing httpx results"""
        httpx_f = f"{self.out_dir}/httpx_results.txt"
        if os.path.exists(httpx_f):
            print(f"[✓] Using existing httpx results: {httpx_f}")
            return httpx_f
        
        sub_f = f"{self.out_dir}/all_subdomains.txt"
        if os.path.exists(sub_f):
            print("[*] Running httpx on subdomains...")
            return self.run_httpx(sub_f)
        
        print("[!] No targets found for vulnerability scan", file=sys.stderr)
        return None
    
    def run_httpx(self, in_f):
        """Run httpx to find live hosts"""
        prep_f = self.prepare_urls(in_f)
        if not prep_f:
            return None
        
        httpx_out = f"{self.out_dir}/httpx_results.txt"
        
        # Test httpx version for compatibility
        httpx_version = self.get_httpx_version()
        
        if httpx_version and "v2" in httpx_version:
            # httpx v2.x uses -list flag
            cmd = ['httpx', '-list', prep_f, '-silent', '-o', httpx_out, 
                   '-timeout', '10', '-retries', '2', '-rate-limit', '50']
        else:
            # httpx v1.x or fallback: use stdin
            cmd = ['httpx', '-silent', '-o', httpx_out, 
                   '-timeout', '10', '-retries', '2', '-rate-limit', '50']
        
        try:
            if "list" in cmd:
                # Use -list flag
                subprocess.run(cmd, timeout=600, check=True)
            else:
                # Use stdin
                with open(prep_f, 'r') as f:
                    subprocess.run(cmd, stdin=f, timeout=600, check=True)
            
            if os.path.exists(httpx_out):
                with open(httpx_out, 'r') as f:
                    lines = [line.strip() for line in f if line.strip()]
                    count = len(lines)
                print(f"[✓] Found {count} live hosts")
                return httpx_out
            return None
        except subprocess.TimeoutExpired:
            print("[!] httpx timeout", file=sys.stderr)
            return None
        except subprocess.CalledProcessError as e:
            print(f"[!] httpx error (exit {e.returncode})", file=sys.stderr)
            # Try alternative method
            return self.run_httpx_alternative(prep_f, httpx_out)
        except Exception as e:
            print(f"[!] httpx error: {str(e)}", file=sys.stderr)
            return None
    
    def get_httpx_version(self):
        """Get httpx version"""
        try:
            result = subprocess.run(['httpx', '-version'], 
                                   capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except:
            return None
    
    def run_httpx_alternative(self, input_file, output_file):
        """Alternative method to run httpx (using cat pipe)"""
        try:
            cmd = f"cat {shlex.quote(input_file)} | httpx -silent -o {shlex.quote(output_file)} -timeout 10 -retries 2"
            subprocess.run(cmd, shell=True, timeout=600, check=True)
            
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    count = sum(1 for line in f if line.strip())
                print(f"[✓] Found {count} live hosts (alternative method)")
                return output_file
            return None
        except Exception as e:
            print(f"[!] Alternative httpx also failed: {str(e)}", file=sys.stderr)
            return None
    
    def prepare_urls(self, in_f):
        """Prepare URLs for httpx"""
        out_f = f"{self.out_dir}/prepared_for_vuln.txt"
        try:
            with open(in_f, 'r') as inf, open(out_f, 'w') as outf:
                for line in inf:
                    url = line.strip()
                    if url and not url.startswith('#') and '.' in url:
                        # Ensure URL has protocol
                        if not url.startswith(('http://', 'https://')):
                            outf.write(f"http://{url}\n")
                            outf.write(f"https://{url}\n")
                        else:
                            outf.write(f"{url}\n")
            print(f"[✓] Prepared {out_f} for httpx")
            return out_f
        except Exception as e:
            print(f"[!] Error preparing URLs: {str(e)}", file=sys.stderr)
            return None
    
    def update_templates(self):
        """Update nuclei templates"""
        print("[*] Updating nuclei templates...")
        try:
            result = subprocess.run(['nuclei', '-update-templates'], 
                                   capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("[✓] Templates updated")
            else:
                print(f"[!] Template update warning: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("[!] Template update timed out")
        except Exception as e:
            print(f"[!] Template update error: {str(e)}")
    
    def run_nuclei(self, tgt_f):
        """Run nuclei vulnerability scanner"""
        print("[*] Running nuclei vulnerability scan...")
        print("[*] This may take a while...")
        
        nuc_out = f"{self.nuc_dir}/nuclei.log"
        nuc_json = f"{self.nuc_dir}/nuclei.json"
        
        cmd = [
            'nuclei', '-l', tgt_f,
            '-o', nuc_out,
            '-json', nuc_json,
            '-severity', 'critical,high,medium',
            '-rate-limit', '50',
            '-concurrency', '10',
            '-timeout', '10',
            '-retries', '2',
            '-silent'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
            
            if result.returncode == 0:
                print("[✓] Nuclei scan completed")
                return True
            elif result.returncode == 1:
                print("[*] Nuclei completed with findings")
                return True
            else:
                print(f"[!] Nuclei error: {result.stderr[:200]}", file=sys.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("[!] Nuclei scan timed out (2 hours)", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[!] Nuclei error: {str(e)}", file=sys.stderr)
            return False
    
    def parse_results(self):
        """Parse and summarize nuclei results"""
        json_f = f"{self.nuc_dir}/nuclei.json"
        sum_f = f"{self.nuc_dir}/summary.txt"
        
        if not os.path.exists(json_f):
            print("[!] No nuclei JSON output found", file=sys.stderr)
            return
        
        print("[*] Parsing vulnerability results...")
        
        try:
            vulns = []
            counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
            
            with open(json_f, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.strip():
                        try:
                            v = json.loads(line)
                            vulns.append(v)
                            severity = v.get('info', {}).get('severity', 'info').lower()
                            if severity in counts:
                                counts[severity] += 1
                        except json.JSONDecodeError:
                            continue
            
            with open(sum_f, 'w', encoding='utf-8') as f:
                f.write(f"VULNERABILITY SUMMARY FOR: {self.domain}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Total Findings: {len(vulns)}\n\n")
                
                f.write("Severity Breakdown:\n")
                f.write("-" * 40 + "\n")
                for severity in ['critical', 'high', 'medium', 'low', 'info']:
                    if counts[severity] > 0:
                        f.write(f"  {severity.upper():<9}: {counts[severity]}\n")
                f.write("\n" + "=" * 60 + "\n\n")
                
                if vulns:
                    f.write("DETAILED FINDINGS:\n\n")
                    
                    # Sort by severity
                    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
                    vulns.sort(key=lambda x: severity_order.get(
                        x.get('info', {}).get('severity', 'info').lower(), 5
                    ))
                    
                    for v in vulns:
                        info = v.get('info', {})
                        severity = info.get('severity', 'UNKNOWN').upper()
                        name = info.get('name', 'Unknown')
                        template = v.get('template-id', 'unknown')
                        host = v.get('host', 'unknown')
                        
                        f.write(f"[{severity}] {name}\n")
                        f.write(f"  Template: {template}\n")
                        f.write(f"  Host: {host}\n")
                        
                        if 'matched-at' in v:
                            f.write(f"  Location: {v['matched-at']}\n")
                        
                        if 'description' in info:
                            desc = info['description'].replace('\n', ' ')
                            if len(desc) > 200:
                                desc = desc[:197] + "..."
                            f.write(f"  Description: {desc}\n")
                        
                        f.write("\n")
                else:
                    f.write("No vulnerabilities found.\n")
            
            print(f"[✓] Summary saved to: {sum_f}")
            print(f"[✓] Total findings: {len(vulns)}")
            
            # Print quick summary
            if counts['critical'] > 0 or counts['high'] > 0:
                print(f"[!] Found {counts['critical']} critical, {counts['high']} high severity issues")
            
        except Exception as e:
            print(f"[!] Error parsing results: {str(e)}", file=sys.stderr)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <out_dir>", file=sys.stderr)
        sys.exit(1)
    
    domain = sys.argv[1]
    out_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"VULNERABILITY SCAN - {domain}")
    print("=" * 60)
    
    if not which('nuclei'):
        print("[!] nuclei is not installed", file=sys.stderr)
        print("[!] Install with: go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest", file=sys.stderr)
        sys.exit(1)
    
    scanner = VulnerabilityScanner(domain, out_dir)
    
    # Update templates
    scanner.update_templates()
    print()
    
    # Get targets
    tgt_f = scanner.check_httpx_results()
    if not tgt_f:
        print("[!] Cannot proceed without targets", file=sys.stderr)
        sys.exit(1)
    
    print()
    
    # Run nuclei
    success = scanner.run_nuclei(tgt_f)
    
    if success:
        print()
        scanner.parse_results()
    
    print("\n[✓] Vulnerability scan complete!")
    print(f"[*] Results saved to: {scanner.nuc_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
