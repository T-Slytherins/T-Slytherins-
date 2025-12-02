#!/usr/bin/env python3

"""
Port Scanning Module 
"""

import sys
import subprocess
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import socket
from shutil import which

class PortScanner:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
        self.ports_dir = f"{output_dir}/ports"
        Path(self.ports_dir).mkdir(parents=True, exist_ok=True)
    
    def resolve_domain(self):
        """Resolve domain to IP address"""
        try:
            ip = socket.gethostbyname(self.domain)
            print(f"[✓] Resolved {self.domain} to {ip}")
            return ip
        except socket.gaierror as e:
            print(f"[!] Could not resolve domain: {str(e)}", file=sys.stderr)
            return None
    
    def scan_ports(self, target):
        """Run nmap port scan"""
        print(f"[*] Scanning ports on {target}...")
        print("[*] This may take several minutes...")
        
        nmap_output = f"{self.ports_dir}/nmap.txt"
        nmap_xml = f"{self.ports_dir}/nmap.xml"
        
        nmap_cmd = [
            'nmap',
            '-sV',
            '-T4',
            '--top-ports', '1000',
            '-oA', f"{self.ports_dir}/nmap",
            target
        ]
        
        try:
            result = subprocess.run(
                nmap_cmd,
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            with open(nmap_output, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n\nErrors:\n")
                    f.write(result.stderr)
            
            if result.returncode == 0:
                print(f"[✓] Port scan completed")
                return True
            else:
                print(f"[!] Port scan completed with errors: {result.stderr}", file=sys.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("[!] Port scan timed out", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[!] Error during port scan: {str(e)}", file=sys.stderr)
            return False
    
    def parse_nmap_xml(self):
        """Parse nmap XML output for better formatting"""
        xml_file = f"{self.ports_dir}/nmap.xml"
        summary_file = f"{self.ports_dir}/port_summary.txt"
        
        if not os.path.exists(xml_file):
            print("[!] XML output not found, skipping parsing", file=sys.stderr)
            return
        
        print("[*] Parsing scan results...")
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            with open(summary_file, 'w') as f:
                f.write(f"PORT SCAN SUMMARY FOR: {self.domain}\n")
                f.write("=" * 60 + "\n\n")
                
                for host in root.findall('host'):
                    address = host.find('address')
                    addr = address.get('addr') if address is not None else 'unknown'
                    
                    f.write(f"Host: {addr}\n")
                    f.write("-" * 60 + "\n")
                    
                    open_ports = []
                    ports = host.find('ports')
                    if ports is not None:
                        for port in ports.findall('port'):
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
            
        except ET.ParseError as e:
            print(f"[!] Error parsing XML: {str(e)}", file=sys.stderr)
        except Exception as e:
            print(f"[!] Error creating summary: {str(e)}", file=sys.stderr)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>", file=sys.stderr)
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"PORT SCANNING - {domain}")
    print("=" * 60)
    
    if not which('nmap'):
        print("[!] nmap is not installed", file=sys.stderr)
        print("[!] Install with: sudo apt install nmap", file=sys.stderr)
        sys.exit(1)
    
    scanner = PortScanner(domain, output_dir)
    
    target = scanner.resolve_domain()
    if not target:
        print("[!] Cannot proceed without valid target", file=sys.stderr)
        sys.exit(1)
    
    success = scanner.scan_ports(target)
    
    if success:
        scanner.parse_nmap_xml()
    
    print("\n[✓] Port scanning complete!")
    print(f"[*] Results saved to: {scanner.ports_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
