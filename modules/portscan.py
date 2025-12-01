#!/usr/bin/env python3

"""
Port Scanning Module 
Fixes: Better nmap integration, parsing, error handling
"""

import sys
import subprocess
import os
import xml.etree.ElementTree as ET
from pathlib import Path

class PortScanner:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
        self.ports_dir = f"{output_dir}/ports"
        Path(self.ports_dir).mkdir(parents=True, exist_ok=True)
    
    def resolve_domain(self):
        """Resolve domain to IP address"""
        import socket
        try:
            ip = socket.gethostbyname(self.domain)
            print(f"[✓] Resolved {self.domain} to {ip}")
            return ip
        except socket.gaierror:
            print(f"[!] Could not resolve domain: {self.domain}")
            return None
    
    def scan_ports(self, target):
        """Run nmap port scan"""
        print(f"[*] Scanning ports on {target}...")
        print("[*] This may take several minutes...")
        
        nmap_output = f"{self.ports_dir}/nmap.txt"
        nmap_xml = f"{self.ports_dir}/nmap.xml"
        
        # Nmap command with safe defaults
        # -sV: Version detection
        # -T4: Faster timing
        # --top-ports 1000: Scan top 1000 ports
        # -oA: Output in all formats
        nmap_cmd = [
            'nmap',
            '-sV',
            '-T4',
            '--top-ports', '1000',
            '-oA', f"{self.ports_dir}/nmap",
            target
        ]
        
        try:
            # Run nmap
            result = subprocess.run(
                nmap_cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            # Save output
            with open(nmap_output, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n\nErrors:\n")
                    f.write(result.stderr)
            
            if result.returncode == 0:
                print(f"[✓] Port scan completed")
                return True
            else:
                print(f"[!] Port scan completed with errors")
                return False
                
        except subprocess.TimeoutExpired:
            print("[!] Port scan timed out")
            return False
        except Exception as e:
            print(f"[!] Error during port scan: {str(e)}")
            return False
    
    def parse_nmap_xml(self):
        """Parse nmap XML output for better formatting"""
        xml_file = f"{self.ports_dir}/nmap.xml"
        summary_file = f"{self.ports_dir}/port_summary.txt"
        
        if not os.path.exists(xml_file):
            print("[!] XML output not found, skipping parsing")
            return
        
        print("[*] Parsing scan results...")
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            with open(summary_file, 'w') as f:
                f.write(f"PORT SCAN SUMMARY FOR: {self.domain}\n")
                f.write("=" * 60 + "\n\n")
                
                # Find all hosts
                for host in root.findall('host'):
                    # Get host address
                    address = host.find('address').get('addr')
                    f.write(f"Host: {address}\n")
                    f.write("-" * 60 + "\n\n")
                    
                    # Get ports
                    ports_elem = host.find('ports')
                    if ports_elem is not None:
                        open_ports = []
                        
                        for port in ports_elem.findall('port'):
                            state = port.find('state')
                            if state is not None and state.get('state') == 'open':
                                portid = port.get('portid')
                                protocol = port.get('protocol')
                                
                                service = port.find('service')
                                service_name = service.get('name', 'unknown') if service is not None else 'unknown'
                                service_product = service.get('product', '') if service is not None else ''
                                service_version = service.get('version', '') if service is not None else ''
                                
                                port_info = {
                                    'port': portid,
                                    'protocol': protocol,
                                    'service': service_name,
                                    'product': service_product,
                                    'version': service_version
                                }
                                open_ports.append(port_info)
                        
                        # Write open ports
                        if open_ports:
                            f.write(f"Open Ports: {len(open_ports)}\n\n")
                            f.write(f"{'PORT':<8} {'PROTOCOL':<10} {'SERVICE':<15} {'VERSION'}\n")
                            f.write("-" * 60 + "\n")
                            
                            for p in open_ports:
                                version_str = f"{p['product']} {p['version']}".strip()
                                f.write(f"{p['port']:<8} {p['protocol']:<10} {p['service']:<15} {version_str}\n")
                            
                            f.write("\n")
                            print(f"[✓] Found {len(open_ports)} open ports")
                        else:
                            f.write("No open ports found\n\n")
                            print("[*] No open ports found")
            
            print(f"[✓] Summary saved to: {summary_file}")
            
        except ET.ParseError:
            print("[!] Error parsing XML output")
        except Exception as e:
            print(f"[!] Error creating summary: {str(e)}")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>")
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"PORT SCANNING - {domain}")
    print("=" * 60)
    
    # Check if nmap is installed
    if subprocess.run(['which', 'nmap'], capture_output=True).returncode != 0:
        print("[!] nmap is not installed")
        print("[!] Install with: sudo apt install nmap")
        sys.exit(1)
    
    scanner = PortScanner(domain, output_dir)
    
    # Resolve domain
    target = scanner.resolve_domain()
    if not target:
        print("[!] Cannot proceed without valid target")
        sys.exit(1)
    
    # Scan ports
    success = scanner.scan_ports(target)
    
    if success:
        # Parse results
        scanner.parse_nmap_xml()
    
    print("\n[✓] Port scanning complete!")
    print(f"[*] Results saved to: {scanner.ports_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
