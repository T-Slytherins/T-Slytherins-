#!/usr/bin/env python3

"""
DNS Reconnaissance Module 
"""

import sys
import socket
import dns.resolver
import dns.zone
import dns.query
from pathlib import Path

class DNSScanner:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
        self.dns_dir = f"{output_dir}/dns"
        Path(self.dns_dir).mkdir(parents=True, exist_ok=True)
        
        # Configure resolver
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 5
        self.resolver.lifetime = 10
    
    def query_record(self, record_type, target=None):
        """Query specific DNS record type"""
        if target is None:
            target = self.domain
        
        try:
            answers = self.resolver.resolve(target, record_type)
            return [str(rdata) for rdata in answers]
        except dns.resolver.NXDOMAIN:
            return [f"[!] Domain {target} does not exist"]
        except dns.resolver.NoAnswer:
            return [f"[!] No {record_type} records found"]
        except dns.resolver.Timeout:
            return [f"[!] Query timeout for {record_type}"]
        except dns.exception.DNSException as e:
            return [f"[!] DNS error querying {record_type}: {str(e)}"]
    
    def scan_records(self):
        """Scan all common DNS record types"""
        print("[*] Scanning DNS records...")
        
        records_file = f"{self.dns_dir}/records.txt"
        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA', 'PTR']
        
        with open(records_file, 'w') as f:
            f.write(f"DNS RECORDS FOR: {self.domain}\n")
            f.write("=" * 60 + "\n\n")
            
            for record_type in record_types:
                print(f"  [*] Querying {record_type} records...")
                results = self.query_record(record_type)
                
                f.write(f"{record_type} Records:\n")
                f.write("-" * 40 + "\n")
                for result in results:
                    f.write(f"  {result}\n")
                    print(f"    {result}")
                f.write("\n")
        
        print(f"[✓] DNS records saved to: {records_file}")
    
    def zone_transfer_test(self):
        """Attempt zone transfer (AXFR)"""
        print("[*] Testing zone transfer (AXFR)...")
        
        zone_file = f"{self.dns_dir}/zone_attempt.txt"
        
        ns_records = self.query_record('NS')
        
        with open(zone_file, 'w') as f:
            f.write(f"ZONE TRANSFER ATTEMPT FOR: {self.domain}\n")
            f.write("=" * 60 + "\n\n")
            
            zone_transfer_success = False
            
            for ns in ns_records:
                if ns.startswith('[!]'):
                    f.write(f"{ns}\n")
                    continue
                
                ns = ns.rstrip('.')
                print(f"  [*] Trying NS: {ns}")
                
                try:
                    zone = dns.zone.from_xfr(dns.query.xfr(ns, self.domain))
                    zone_transfer_success = True
                    f.write(f"[!] Zone transfer successful from {ns}!\n")
                    print(f"  [!] Zone transfer successful!")
                    for name, node in zone.nodes.items():
                        f.write(f"  {name}: {node.to_text(name)}\n")
                    f.write("\n")
                except dns.exception.FormError:
                    f.write(f"[!] Zone transfer failed (FormError) from {ns}\n")
                    print(f"  [!] Zone transfer failed (FormError)")
                except Exception as e:
                    f.write(f"[!] Zone transfer failed from {ns}: {str(e)}\n")
                    print(f"  [!] Zone transfer failed: {str(e)}")
            
            if not zone_transfer_success:
                f.write("[✓] No zone transfer possible\n")
                print("  [✓] No zone transfer possible")
        
        print(f"[✓] Zone transfer results saved to: {zone_file}")
    
    def check_misconfigurations(self):
        """Check for DNS misconfigurations"""
        print("[*] Checking DNS misconfigurations...")
        
        misconfig_file = f"{self.dns_dir}/misconfig.txt"
        
        with open(misconfig_file, 'w') as f:
            f.write(f"DNS MISCONFIGURATION CHECK FOR: {self.domain}\n")
            f.write("=" * 60 + "\n\n")
            
            # Wildcard DNS check
            print("  [*] Checking wildcard DNS...")
            f.write("Wildcard DNS Check:\n")
            f.write("-" * 40 + "\n")
            
            test_subdomains = [
                f"wildcardtest123456789.{self.domain}",
                f"nonexistent987654321.{self.domain}"
            ]
            
            wildcard_ips = set()
            for test_sub in test_subdomains:
                try:
                    result = socket.gethostbyname(test_sub)
                    wildcard_ips.add(result)
                except socket.gaierror:
                    pass
            
            if wildcard_ips:
                f.write(f"[!] Wildcard DNS detected: {', '.join(wildcard_ips)}\n")
                print(f"  [!] Wildcard DNS detected")
            else:
                f.write("[✓] No wildcard DNS detected\n")
                print(f"  [✓] No wildcard DNS detected")
            
            f.write("\n")
            
            # Check SPF records
            print("  [*] Checking SPF records...")
            f.write("SPF Record Check:\n")
            f.write("-" * 40 + "\n")
            
            txt_records = self.query_record('TXT')
            spf_found = False
            
            for record in txt_records:
                if 'spf' in record.lower():
                    f.write(f"[✓] SPF record found: {record}\n")
                    spf_found = True
            
            if not spf_found:
                f.write("[!] No SPF record found (email security risk)\n")
                print("  [!] No SPF record found")
            else:
                print("  [✓] SPF record found")
            
            f.write("\n")
            
            # Check DMARC
            print("  [*] Checking DMARC...")
            f.write("DMARC Check:\n")
            f.write("-" * 40 + "\n")
            
            dmarc_records = self.query_record('TXT', f"_dmarc.{self.domain}")
            dmarc_found = False
            
            for record in dmarc_records:
                if 'dmarc' in record.lower():
                    f.write(f"[✓] DMARC record found: {record}\n")
                    dmarc_found = True
            
            if not dmarc_found:
                f.write("[!] No DMARC record found\n")
                print("  [!] No DMARC record found")
            else:
                print("  [✓] DMARC record found")
        
        print(f"[✓] Misconfiguration check saved to: {misconfig_file}")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>", file=sys.stderr)
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"DNS RECONNAISSANCE - {domain}")
    print("=" * 60)
    
    scanner = DNSScanner(domain, output_dir)
    
    try:
        scanner.scan_records()
        print()
        scanner.zone_transfer_test()
        print()
        scanner.check_misconfigurations()
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error during DNS scan: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    print("\n[✓] DNS reconnaissance complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
