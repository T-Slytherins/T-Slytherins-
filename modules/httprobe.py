#!/usr/bin/env python3

"""
HTTP Probing Module 
Fixed httpx -l flag issue
"""

import sys
import subprocess
import os
import shlex
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
            f.write(f"http://{self.domain}\n")
            f.write(f"https://{self.domain}\n")
        return temp_file
    
    def prepare_urls(self, input_file):
        """Add protocols and filter invalid subdomains"""
        output_file = f"{self.output_dir}/prepared_subdomains.txt"
        
        try:
            with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
                for line in infile:
                    subdomain = line.strip()
                    if subdomain and not subdomain.startswith('#') and '.' in subdomain:
                        outfile.write(f"http://{subdomain}\n")
                        outfile.write(f"https://{subdomain}\n")
            print(f"[✓] Prepared {output_file} with protocols")
            return output_file
        except Exception as e:
            print(f"[!] Error preparing URLs: {str(e)}", file=sys.stderr)
            return None
    
    def run_httpx(self, input_file):
        """Run httpx to find live hosts - fixed -l flag issue"""
        print("[*] Probing for live HTTP/HTTPS hosts...")
        print("[*] This may take several minutes...")
        
        output_file = f"{self.output_dir}/httpx_results.txt"
        
        # Test httpx version
        httpx_version = self.get_httpx_version()
        
        if httpx_version and "v2" in httpx_version:
            # httpx v2.x uses -list flag
            httpx_cmd = [
                'httpx', '-list', input_file,
                '-o', output_file,
                '-silent',
                '-status-code',
                '-title',
                '-tech-detect',
                '-follow-redirects',
                '-timeout', '10',
                '-retries', '2',
                '-rate-limit', '100'
            ]
        else:
            # httpx v1.x or fallback: use stdin
            httpx_cmd = [
                'httpx',
                '-o', output_file,
                '-silent',
                '-status-code',
                '-title',
                '-tech-detect',
                '-follow-redirects',
                '-timeout', '10',
                '-retries', '2',
                '-rate-limit', '100'
            ]
        
        try:
            if "-list" in httpx_cmd:
                # Use -list flag
                result = subprocess.run(
                    httpx_cmd,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
            else:
                # Use stdin
                with open(input_file, 'r') as f:
                    result = subprocess.run(
                        httpx_cmd,
                        stdin=f,
                        capture_output=True,
                        text=True,
                        timeout=600
                    )
            
            if result.returncode == 0:
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        count = sum(1 for line in f if line.strip())
                    print(f"[✓] HTTP probing completed - {count} live hosts")
                    return True
                else:
                    print("[!] No live hosts found")
                    return False
            else:
                # Try alternative method
                print(f"[*] Trying alternative method...")
                return self.run_httpx_alternative(input_file, output_file)
                
        except subprocess.TimeoutExpired:
            print("[!] HTTP probing timed out", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[!] Error during HTTP probing: {str(e)}", file=sys.stderr)
            return False
    
    def get_httpx_version(self):
        """Get httpx version"""
        try:
            result = subprocess.run(['httpx', '-version'], 
                                   capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except:
            return None
    
    def run_httpx_alternative(self, input_file, output_file):
        """Alternative method using cat pipe"""
        try:
            cmd = f"cat {shlex.quote(input_file)} | httpx -silent -o {shlex.quote(output_file)} -status-code -title -tech-detect -follow-redirects -timeout 10 -retries 2 -rate-limit 100"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0 and os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    count = sum(1 for line in f if line.strip())
                print(f"[✓] HTTP probing completed (alt method) - {count} live hosts")
                return True
            return False
        except Exception as e:
            print(f"[!] Alternative method failed: {str(e)}")
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
            technologies = set()
            
            for line in results:
                if line:
                    # Extract URL (first part before space)
                    url = line.split()[0] if ' ' in line else line
                    live_hosts.append(url)
                    
                    # Extract status code if present
                    if '[' in line and ']' in line:
                        import re
                        matches = re.findall(r'\[(\d+)\]', line)
                        if matches:
                            status = matches[0]
                            status_codes[status] = status_codes.get(status, 0) + 1
                    
                    # Extract technologies if present
                    if '[' in line and ']' in line:
                        parts = line.split('[')
                        for part in parts[1:]:
                            if ']' in part:
                                tech = part.split(']')[0]
                                if tech.isdigit():
                                    continue  # Skip status codes
                                technologies.add(tech)
            
            with open(summary_file, 'w') as f:
                f.write(f"HTTP PROBING SUMMARY FOR: {self.domain}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Total Live Hosts: {len(live_hosts)}\n\n")
                
                if status_codes:
                    f.write("Status Code Distribution:\n")
                    f.write("-" * 40 + "\n")
                    for status, count in sorted(status_codes.items(), key=lambda x: int(x[0])):
                        f.write(f"  {status}: {count}\n")
                    f.write("\n")
                
                if technologies:
                    f.write("Technologies Detected:\n")
                    f.write("-" * 40 + "\n")
                    for tech in sorted(technologies):
                        f.write(f"  {tech}\n")
                    f.write("\n")
                
                f.write("Live Hosts:\n")
                f.write("-" * 40 + "\n")
                for host in sorted(live_hosts):
                    f.write(f"  {host}\n")
            
            print(f"[✓] Summary saved to: {summary_file}")
            print(f"[✓] Total live hosts: {len(live_hosts)}")
            
            if status_codes:
                print(f"[✓] Status codes: {', '.join(f'{k}({v})' for k, v in sorted(status_codes.items()))}")
            
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
