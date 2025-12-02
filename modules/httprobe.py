#!/usr/bin/env python3

"""
HTTP Probing Module 
Finds live HTTP/HTTPS hosts using httpx
"""

import sys
import subprocess
import os
from pathlib import Path

class HTTPProber:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
    
    def get_input_file(self):
        """Get the subdomain list file"""
        subdomain_file = f"{self.output_dir}/all_subdomains.txt"
        
        if os.path.exists(subdomain_file):
            print(f"[✓] Found subdomain list: {subdomain_file}")
            return subdomain_file
        
        # Fallback to just the domain
        print(f"[!] No subdomain list found, using domain only")
        temp_file = f"{self.output_dir}/temp_domain.txt"
        with open(temp_file, 'w') as f:
            f.write(f"{self.domain}\n")
        return temp_file
    
    def run_httpx(self, input_file):
        """Run httpx to find live hosts"""
        print("[*] Probing for live HTTP/HTTPS hosts...")
        print("[*] This may take several minutes...")
        
        output_file = f"{self.output_dir}/httpx_results.txt"
        
        # httpx command
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
            # Run httpx
            result = subprocess.run(
                httpx_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0 or os.path.exists(output_file):
                # Count results
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        count = sum(1 for line in f if line.strip())
                    
                    print(f"[✓] HTTP probing completed")
                    print(f"[✓] Found {count} live hosts")
                    return True
                else:
                    print("[!] No live hosts found")
                    return False
            else:
                print(f"[!] HTTP probing failed")
                if result.stderr:
                    print(f"[!] Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[!] HTTP probing timed out")
            return False
        except FileNotFoundError:
            print("[!] httpx not found. Install with: go install github.com/projectdiscovery/httpx/cmd/httpx@latest")
            return False
        except Exception as e:
            print(f"[!] Error during HTTP probing: {str(e)}")
            return False
    
    def parse_results(self):
        """Parse and display httpx results"""
        results_file = f"{self.output_dir}/httpx_results.txt"
        summary_file = f"{self.output_dir}/httpx_summary.txt"
        
        if not os.path.exists(results_file):
            print("[!] No results file found")
            return
        
        print("[*] Parsing results...")
        
        try:
            with open(results_file, 'r') as f:
                results = [line.strip() for line in f if line.strip()]
            
            # Categorize by status code
            live_hosts = []
            status_codes = {}
            
            for line in results:
                parts = line.split()
                if parts:
                    url = parts[0]
                    live_hosts.append(url)
                    
                    # Try to extract status code if present
                    if '[' in line and ']' in line:
                        status = line[line.find('[')+1:line.find(']')]
                        status_codes[status] = status_codes.get(status, 0) + 1
            
            # Create summary
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
            print(f"[!] Error parsing results: {str(e)}")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>")
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"HTTP PROBING - {domain}")
    print("=" * 60)
    
    # Check if httpx is installed
    if subprocess.run(['which', 'httpx'], capture_output=True).returncode != 0:
        print("[!] httpx is not installed")
        print("[!] Install with: go install github.com/projectdiscovery/httpx/cmd/httpx@latest")
        sys.exit(1)
    
    prober = HTTPProber(domain, output_dir)
    
    # Get input file
    input_file = prober.get_input_file()
    
    # Run httpx
    success = prober.run_httpx(input_file)
    
    if success:
        # Parse results
        prober.parse_results()
    
    print("\n[✓] HTTP probing complete!")
    print(f"[*] Results saved to: {output_dir}/httpx_results.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()
