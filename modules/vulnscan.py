#!/usr/bin/env python3

"""
Vulnerability Scanning Module 
"""

import sys
import subprocess
import os
import json
from pathlib import Path
from shutil import which

class VulnerabilityScanner:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
        self.nuclei_dir = f"{output_dir}/nuclei"
        Path(self.nuclei_dir).mkdir(parents=True, exist_ok=True)
    
    def check_httpx_results(self):
        """Check if httpx results exist, prepare if needed"""
        httpx_file = f"{self.output_dir}/httpx_results.txt"
        
        if os.path.exists(httpx_file):
            print(f"[✓] Found httpx results: {httpx_file}")
            return httpx_file
        
        subdomain_file = f"{self.output_dir}/all_subdomains.txt"
        if os.path.exists(subdomain_file):
            print(f"[*] Running httpx on subdomains...")
            return self.run_httpx(subdomain_file)
        
        print(f"[!] No target file found", file=sys.stderr)
        return None
    
    def run_httpx(self, input_file):
        """Run httpx to find live hosts"""
        prepared_file = self.prepare_urls(input_file)
        if not prepared_file:
            return None
        
        print("[*] Running httpx to find live hosts...")
        
        httpx_output = f"{self.output_dir}/httpx_results.txt"
        
        httpx_cmd = [
            'httpx',
            '-l', prepared_file,
            '-silent',
            '-o', httpx_output,
            '-timeout', '10',
            '-retries', '2'
        ]
        
        try:
            subprocess.run(httpx_cmd, timeout=600, check=True)
            if os.path.exists(httpx_output):
                with open(httpx_output, 'r') as f:
                    count = sum(1 for line in f if line.strip())
                print(f"[✓] Found {count} live hosts")
                return httpx_output
            return None
        except Exception as e:
            print(f"[!] Error running httpx: {str(e)}", file=sys.stderr)
            return None
    
    def prepare_urls(self, input_file):
        """Prepare URLs with protocols"""
        output_file = f"{self.output_dir}/prepared_for_vuln.txt"
        
        try:
            with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
                for line in infile:
                    url = line.strip()
                    if url and not url.startswith('#'):
                        if not url.startswith(('http://', 'https://')):
                            outfile.write(f"https://{url}\n")
                        else:
                            outfile.write(f"{url}\n")
            return output_file
        except Exception as e:
            print(f"[!] Error preparing URLs: {str(e)}", file=sys.stderr)
            return None
    
    def update_templates(self):
        """Update nuclei templates"""
        print("[*] Updating nuclei templates...")
        
        try:
            subprocess.run(['nuclei', '-update-templates'], capture_output=True, timeout=300, check=True)
            print("[✓] Templates updated")
        except Exception as e:
            print(f"[!] Could not update templates: {str(e)}. Continuing...", file=sys.stderr)
    
    def run_nuclei(self, target_file):
        """Run nuclei vulnerability scan"""
        print("[*] Starting vulnerability scan with nuclei...")
        print("[*] This may take a while...")
        
        nuclei_output = f"{self.nuclei_dir}/nuclei.log"
        nuclei_json = f"{self.nuclei_dir}/nuclei.json"
        
        nuclei_cmd = [
            'nuclei',
            '-l', target_file,
            '-o', nuclei_output,
            '-jsonl', nuclei_json,
            '-severity', 'critical,high,medium',
            '-rate-limit', '50',
            '-concurrency', '10',
            '-bulk-size', '25',
            '-timeout', '10',
            '-retries', '2',
            '-silent'
        ]
        
        try:
            result = subprocess.run(
                nuclei_cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode == 0:
                print(f"[✓] Nuclei scan completed")
                return True
            else:
                print(f"[!] Nuclei scan failed: {result.stderr}", file=sys.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("[!] Nuclei scan timed out", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[!] Error running nuclei: {str(e)}", file=sys.stderr)
            return False
    
    def parse_results(self):
        """Parse nuclei JSONL results"""
        json_file = f"{self.nuclei_dir}/nuclei.json"
        summary_file = f"{self.nuclei_dir}/summary.txt"
        
        if not os.path.exists(json_file):
            print("[!] No JSON results found", file=sys.stderr)
            return
        
        print("[*] Parsing vulnerability results...")
        
        try:
            vulnerabilities = []
            severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
            
            with open(json_file, 'r') as f:
                for line in f:
                    if line.strip():
                        vuln = json.loads(line)
                        vulnerabilities.append(vuln)
                        severity = vuln.get('info', {}).get('severity', 'info').lower()
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            with open(summary_file, 'w') as f:
                f.write(f"VULNERABILITY SCAN SUMMARY FOR: {self.domain}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Total Issues Found: {len(vulnerabilities)}\n")
                f.write(f"  Critical: {severity_counts['critical']}\n")
                f.write(f"  High:     {severity_counts['high']}\n")
                f.write(f"  Medium:   {severity_counts['medium']}\n")
                f.write(f"  Low:      {severity_counts['low']}\n")
                f.write(f"  Info:     {severity_counts['info']}\n")
                f.write("\n" + "=" * 60 + "\n\n")
                
                severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
                vulnerabilities.sort(key=lambda x: severity_order.get(x.get('info', {}).get('severity', 'info').lower(), 5))
                
                f.write("DETAILED FINDINGS:\n\n")
                
                for vuln in vulnerabilities:
                    info = vuln.get('info', {})
                    f.write(f"[{info.get('severity', 'UNKNOWN').upper()}] {info.get('name', 'Unknown')}\n")
                    f.write(f"  Template: {vuln.get('template-id', 'unknown')}\n")
                    f.write(f"  Target: {vuln.get('host', 'unknown')}\n")
                    
                    if 'matched-at' in vuln:
                        f.write(f"  Matched: {vuln['matched-at']}\n")
                    
                    if 'description' in info:
                        f.write(f"  Description: {info['description']}\n")
                    
                    f.write("\n")
            
            print(f"[✓] Summary saved to: {summary_file}")
            print(f"[✓] Found {len(vulnerabilities)} issues")
            
        except json.JSONDecodeError as e:
            print(f"[!] Error parsing JSON: {str(e)}", file=sys.stderr)
        except Exception as e:
            print(f"[!] Error parsing results: {str(e)}", file=sys.stderr)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>", file=sys.stderr)
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"VULNERABILITY SCANNING - {domain}")
    print("=" * 60)
    
    if not which('nuclei'):
        print("[!] nuclei is not installed", file=sys.stderr)
        print("[!] Please run installer.sh", file=sys.stderr)
        sys.exit(1)
    
    scanner = VulnerabilityScanner(domain, output_dir)
    
    scanner.update_templates()
    print()
    
    target_file = scanner.check_httpx_results()
    if not target_file:
        print("[!] No targets available for scanning", file=sys.stderr)
        sys.exit(1)
    
    print()
    
    success = scanner.run_nuclei(target_file)
    
    if success:
        print()
        scanner.parse_results()
    
    print("\n[✓] Vulnerability scanning complete!")
    print(f"[*] Results saved to: {scanner.nuclei_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
