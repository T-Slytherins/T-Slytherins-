#!/usr/bin/env python3

"""
HTTP Probing Module 
"""

import sys
import subprocess
import os
from pathlib import Path
from shutil import which

class HTTPProber:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
    
    def get_input_file(self):
        """Get the subdomain list and prepare with protocols"""
        subdomain_file = f"{self.output_dir}/all_subdomains.txt"
        
        if os.path.exists(subdomain_file):
            print(f"[✓] Found subdomain list: {subdomain_file}")
            return self.prepare_urls(subdomain_file)
        
        print(f"[!] No subdomain list found, using domain only")
        temp_file = f"{self.output_dir}/temp_domain.txt"
        with open(temp_file, 'w') as f:
            f.write(f"https://{self.domain}\n")
            f.write(f"http://{self.domain}\n")
        return temp_file
    
    def prepare_urls(self, input_file):
        """Add protocols and filter invalid subdomains"""
        output_file = f"{self.output_dir}/prepared_subdomains.txt"
        
        try:
            with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
                for line in infile:
                    subdomain = line.strip()
                    if subdomain and not subdomain.startswith('#') and '.' in subdomain:  # Filter invalid
                        outfile.write(f"https://{subdomain}\n")
                        outfile.write(f"http://{subdomain}\n")
            print(f"[✓] Prepared {output_file} with protocols")
            return output_file
        except Exception as e:
            print(f"[!] Error preparing URLs: {str(e)}", file=sys.stderr)
            return None
    
    def run_httpx(self, input_file):
        """Run httpx to find live hosts"""
        print("[*] Probing for live HTTP/HTTPS hosts...")
        print("[*] This may take several minutes...")
        
        output_file = f"{self.output_dir}/httpx_results.txt"
        
        httpx_cmd = [
            'httpx',
            '-l', input_file,
            '-o', output_file,
            '-silent',
            '-status-code',
            '-title',
            '-tech-detect',
            '-follow-redirects',
            '-timeout', '10',
            '-retries', '2',
            '-threads', '50'
        ]
        
        try:
            result = subprocess.run(
                httpx_cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    count = sum(1 for line in f if line.strip())
                print(f"[✓] HTTP probing completed")
                print(f"[✓] Found {count} live hosts")
                return True
            else:
                print("[!] No live hosts found", file=sys.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("[!] HTTP probing timed out", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[!] Error during HTTP probing: {str(e)}", file=sys.stderr)
            return False
    
    def parse_results(self):
        """Parse and display httpx results"""
        results_file = f"{self.output_dir}/httpx_results.txt"
        summary_file = f"{self.output_dir}/httpx_summary.txt"
        
        if not os.path.exists(results_file):
            print("[!] No results file found", file=sys.stderr)
            return
        
        print("[*] Parsing results...")
        
        try:
            with open(results_file, 'r') as f:
                results = [line.strip() for line in f if line.strip()]
            
            status_codes = {}
            live_hosts = []
            
            for line in results:
                parts = line.split()
                if parts:
                    url = parts[0]
                    live_hosts.append(url)
                    if '[' in line and ']' in line:
                        status = line[line.find('[')+1:line.find(']')]
                        status_codes[status] = status_codes.get(status, 0) + 1
            
            with open(summary_file, 'w') as f:
                f.write(f"HTTP PROBING SUMMARY FOR: {self.domain}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Total Live Hosts: {len(live_hosts)}\n\n")
                
                if status_codes:
                    f.write("Status Code Distribution:\n")
                    f.write("-" * 40 + "\n")
                    for status, count in sorted(status_codes.items()):
                        f.write(f"  {status}: {count}\n")
                    f.write("\n")
                
                f.write("Live Hosts:\n")
                f.write("-" * 40 + "\n")
                for host in live_hosts:
                    f.write(f"  {host}\n")
            
            print(f"[✓] Summary saved to: {summary_file}")
            print(f"[✓] Total live hosts: {len(live_hosts)}")
            
        except Exception as e:
            print(f"[!] Error parsing results: {str(e)}", file=sys.stderr)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>", file=sys.stderr)
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"HTTP PROBING - {domain}")
    print("=" * 60)
    
    if not which('httpx'):
        print("[!] httpx is not installed", file=sys.stderr)
        print("[!] Install with: go install github.com/projectdiscovery/httpx/cmd/httpx@latest", file=sys.stderr)
        sys.exit(1)
    
    prober = HTTPProber(domain, output_dir)
    
    input_file = prober.get_input_file()
    if not input_file:
        sys.exit(1)
    
    success = prober.run_httpx(input_file)
    
    if success:
        prober.parse_results()
    
    print("\n[✓] HTTP probing complete!")
    print(f"[*] Results saved to: {output_dir}/httpx_results.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()
