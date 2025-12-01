#!/usr/bin/env python3

"""
Vulnerability Scanning Module 
Fixes: Better nuclei integration, rate limiting, output parsing
"""

import sys
import subprocess
import os
import json
from pathlib import Path

class VulnerabilityScanner:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
        self.nuclei_dir = f"{output_dir}/nuclei"
        Path(self.nuclei_dir).mkdir(parents=True, exist_ok=True)
    
    def check_httpx_results(self):
        """Check if httpx results exist"""
        httpx_file = f"{self.output_dir}/httpx_results.txt"
        
        if os.path.exists(httpx_file):
            print(f"[✓] Found httpx results: {httpx_file}")
            return httpx_file
        
        # Check subdomain file
        subdomain_file = f"{self.output_dir}/all_subdomains.txt"
        if os.path.exists(subdomain_file):
            print(f"[*] Using subdomain file: {subdomain_file}")
            return subdomain_file
        
        print(f"[!] No target file found")
        return None
    
    def run_httpx(self, input_file):
        """Run httpx to find live hosts"""
        print("[*] Running httpx to find live hosts...")
        
        httpx_output = f"{self.output_dir}/httpx_results.txt"
        
        httpx_cmd = [
            'httpx',
            '-l', input_file,
            '-silent',
            '-o', httpx_output,
            '-timeout', '10',
            '-retries', '2'
        ]
        
        try:
            subprocess.run(
                httpx_cmd,
                timeout=600,
                check=False
            )
            
            if os.path.exists(httpx_output):
                # Count results
                with open(httpx_output, 'r') as f:
                    count = sum(1 for line in f if line.strip())
                
                print(f"[✓] Found {count} live hosts")
                return httpx_output
            else:
                print("[!] No live hosts found")
                return None
                
        except subprocess.TimeoutExpired:
            print("[!] httpx timed out")
            return None
        except Exception as e:
            print(f"[!] Error running httpx: {str(e)}")
            return None
    
    def update_templates(self):
        """Update nuclei templates"""
        print("[*] Updating nuclei templates...")
        
        try:
            subprocess.run(
                ['nuclei', '-update-templates'],
                capture_output=True,
                timeout=300,
                check=False
            )
            print("[✓] Templates updated")
        except:
            print("[!] Could not update templates, continuing with existing ones")
    
    def run_nuclei(self, target_file):
        """Run nuclei vulnerability scan"""
        print("[*] Starting vulnerability scan with nuclei...")
        print("[*] This may take a while depending on number of targets...")
        
        nuclei_output = f"{self.nuclei_dir}/nuclei.log"
        nuclei_json = f"{self.nuclei_dir}/nuclei.json"
        
        # Nuclei command with safe defaults
        nuclei_cmd = [
            'nuclei',
            '-l', target_file,
            '-severity', 'low,medium,high,critical',
            '-o', nuclei_output,
            '-json-export', nuclei_json,
            '-rate-limit', '150',  # Rate limiting
            '-timeout', '10',
            '-retries', '2',
            '-verbose'
        ]
        
        try:
            # Run nuclei
            process = subprocess.Popen(
                nuclei_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Stream output
            for line in process.stdout:
                print(f"  {line.strip()}")
            
            process.wait(timeout=3600)  # 1 hour timeout
            
            if process.returncode == 0:
                print(f"[✓] Nuclei scan completed")
                return True
            else:
                print(f"[!] Nuclei scan completed with warnings")
                return True  # Still consider it successful
                
        except subprocess.TimeoutExpired:
            print("[!] Nuclei scan timed out")
            process.kill()
            return False
        except KeyboardInterrupt:
            print("\n[!] Scan interrupted by user")
            process.kill()
            return False
        except Exception as e:
            print(f"[!] Error during nuclei scan: {str(e)}")
            return False
    
    def parse_results(self):
        """Parse and summarize nuclei results"""
        json_file = f"{self.nuclei_dir}/nuclei.json"
        summary_file = f"{self.nuclei_dir}/summary.txt"
        
        if not os.path.exists(json_file):
            print("[!] No JSON results found")
            return
        
        print("[*] Parsing results...")
        
        try:
            vulnerabilities = []
            
            # Read JSON lines
            with open(json_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            vuln = json.loads(line)
                            vulnerabilities.append(vuln)
                        except json.JSONDecodeError:
                            continue
            
            # Create summary
            with open(summary_file, 'w') as f:
                f.write(f"VULNERABILITY SCAN SUMMARY\n")
                f.write("=" * 60 + "\n\n")
                
                if not vulnerabilities:
                    f.write("No vulnerabilities found!\n")
                    print("[✓] No vulnerabilities found")
                    return
                
                # Count by severity
                severity_counts = {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'info': 0
                }
                
                for vuln in vulnerabilities:
                    severity = vuln.get('info', {}).get('severity', 'info').lower()
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Write summary
                f.write(f"Total Findings: {len(vulnerabilities)}\n\n")
                f.write("By Severity:\n")
                f.write(f"  Critical: {severity_counts['critical']}\n")
                f.write(f"  High:     {severity_counts['high']}\n")
                f.write(f"  Medium:   {severity_counts['medium']}\n")
                f.write(f"  Low:      {severity_counts['low']}\n")
                f.write(f"  Info:     {severity_counts['info']}\n")
                f.write("\n" + "=" * 60 + "\n\n")
                
                # Write detailed findings
                f.write("DETAILED FINDINGS:\n\n")
                
                # Sort by severity
                severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
                vulnerabilities.sort(
                    key=lambda x: severity_order.get(
                        x.get('info', {}).get('severity', 'info').lower(), 
                        5
                    )
                )
                
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
            print(f"    Critical: {severity_counts['critical']}, High: {severity_counts['high']}")
            
        except Exception as e:
            print(f"[!] Error parsing results: {str(e)}")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>")
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"VULNERABILITY SCANNING - {domain}")
    print("=" * 60)
    
    # Check if nuclei is installed
    if subprocess.run(['which', 'nuclei'], capture_output=True).returncode != 0:
        print("[!] nuclei is not installed")
        print("[!] Please run installer.sh")
        sys.exit(1)
    
    scanner = VulnerabilityScanner(domain, output_dir)
    
    # Update templates
    scanner.update_templates()
    print()
    
    # Check for existing results or generate with httpx
    target_file = scanner.check_httpx_results()
    
    if not target_file:
        # Try to run httpx on subdomains
        subdomain_file = f"{output_dir}/all_subdomains.txt"
        if os.path.exists(subdomain_file):
            target_file = scanner.run_httpx(subdomain_file)
        
        if not target_file:
            print("[!] No targets available for scanning")
            sys.exit(1)
    
    print()
    
    # Run nuclei scan
    success = scanner.run_nuclei(target_file)
    
    if success:
        print()
        scanner.parse_results()
    
    print("\n[✓] Vulnerability scanning complete!")
    print(f"[*] Results saved to: {scanner.nuclei_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
