#!/usr/bin/env python3

"""
Web Crawling Module 
"""

import sys
import subprocess
import os
from pathlib import Path
from shutil import which

class WebCrawler:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
    
    def get_target_file(self):
        """Get the list of URLs to crawl, prepare with protocols"""
        httpx_file = f"{self.output_dir}/httpx_results.txt"
        if os.path.exists(httpx_file):
            print(f"[✓] Using httpx results: {httpx_file}")
            return httpx_file
        
        subdomain_file = f"{self.output_dir}/all_subdomains.txt"
        if os.path.exists(subdomain_file):
            print(f"[*] Using subdomain list: {subdomain_file}")
            return self.prepare_urls(subdomain_file)
        
        print(f"[*] Using domain only: {self.domain}")
        temp_file = f"{self.output_dir}/temp_crawl_target.txt"
        with open(temp_file, 'w') as f:
            f.write(f"https://{self.domain}\n")
            f.write(f"http://{self.domain}\n")
        return temp_file
    
    def prepare_urls(self, input_file):
        """Add http/https prefix to domains, filter invalid"""
        output_file = f"{self.output_dir}/urls_for_crawl.txt"
        
        try:
            with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
                for line in infile:
                    url = line.strip()
                    if url and not url.startswith('#') and '.' in url:
                        if not url.startswith(('http://', 'https://')):
                            outfile.write(f"https://{url}\n")
                        else:
                            outfile.write(f"{url}\n")
            print(f"[✓] Prepared URLs for crawling")
            return output_file
        except Exception as e:
            print(f"[!] Error preparing URLs: {str(e)}", file=sys.stderr)
            return None
    
    def run_katana(self, target_file):
        """Run Katana web crawler"""
        print("[*] Starting web crawling with Katana...")
        print("[*] This may take a while...")
        
        output_file = f"{self.output_dir}/katana.txt"
        
        katana_cmd = [
            'katana',
            '-list', target_file,
            '-output', output_file,
            '-depth', '3',
            '-js-crawl',
            '-field-scope', 'rdn',
            '-crawl-duration', '10',
            '-timeout', '10',
            '-retry', '2',
            '-silent'
        ]
        
        try:
            result = subprocess.run(
                katana_cmd,
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            if result.returncode == 0:
                print(f"[✓] Katana completed")
                return True
            else:
                print(f"[!] Katana failed: {result.stderr}", file=sys.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("[!] Katana timed out", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[!] Error running Katana: {str(e)}", file=sys.stderr)
            return False
    
    def parse_results(self):
        """Parse Katana results for summary"""
        results_file = f"{self.output_dir}/katana.txt"
        summary_file = f"{self.output_dir}/katana_summary.txt"
        
        if not os.path.exists(results_file):
            print("[!] No results file found", file=sys.stderr)
            return
        
        print("[*] Parsing crawl results...")
        
        try:
            with open(results_file, 'r') as f:
                urls = set(line.strip() for line in f if line.strip())
            
            parameters = set()
            js_files = []
            api_endpoints = []
            endpoints = set()
            
            for url in urls:
                if '?' in url:
                    query = url.split('?')[1]
                    params = query.split('&')
                    for param in params:
                        if '=' in param:
                            parameters.add(param.split('=')[0])
                
                if url.endswith('.js'):
                    js_files.append(url)
                
                if '/api/' in url or url.endswith(('.json', '.xml')):
                    api_endpoints.append(url)
                
                path = url.split('?')[0]
                endpoints.add(path)
            
            with open(summary_file, 'w') as f:
                f.write(f"WEB CRAWLING SUMMARY FOR: {self.domain}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Total URLs Discovered: {len(urls)}\n")
                f.write(f"Unique Endpoints: {len(endpoints)}\n")
                f.write(f"Parameters Found: {len(parameters)}\n")
                f.write(f"JavaScript Files: {len(js_files)}\n")
                f.write(f"API Endpoints: {len(api_endpoints)}\n")
                f.write("\n" + "=" * 60 + "\n\n")
                
                if parameters:
                    f.write("Discovered Parameters:\n")
                    f.write("-" * 40 + "\n")
                    for param in sorted(parameters):
                        f.write(f"  {param}\n")
                    f.write("\n")
                
                if js_files:
                    f.write("JavaScript Files:\n")
                    f.write("-" * 40 + "\n")
                    for js in js_files:
                        f.write(f"  {js}\n")
                    f.write("\n")
                
                if api_endpoints:
                    f.write("API Endpoints:\n")
                    f.write("-" * 40 + "\n")
                    for api in api_endpoints:
                        f.write(f"  {api}\n")
                    f.write("\n")
            
            print(f"[✓] Summary saved to: {summary_file}")
            print(f"[✓] Total URLs discovered: {len(urls)}")
            
        except Exception as e:
            print(f"[!] Error parsing results: {str(e)}", file=sys.stderr)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>", file=sys.stderr)
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"WEB CRAWLING - {domain}")
    print("=" * 60)
    
    if not which('katana'):
        print("[!] katana is not installed", file=sys.stderr)
        print("[!] Install with: go install github.com/projectdiscovery/katana/cmd/katana@latest", file=sys.stderr)
        sys.exit(1)
    
    crawler = WebCrawler(domain, output_dir)
    
    target_file = crawler.get_target_file()
    if not target_file:
        sys.exit(1)
    
    print()
    
    success = crawler.run_katana(target_file)
    
    if success:
        print()
        crawler.parse_results()
    
    print("\n[✓] Web crawling complete!")
    print(f"[*] Results saved to: {output_dir}/katana.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()
