#!/usr/bin/env python3

"""
Web Crawling Module 
Uses Katana to discover endpoints, parameters, and paths
"""

import sys
import subprocess
import os
from pathlib import Path

class WebCrawler:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
    
    def get_target_file(self):
        """Get the list of URLs to crawl"""
        # First try httpx results
        httpx_file = f"{self.output_dir}/httpx_results.txt"
        if os.path.exists(httpx_file):
            print(f"[✓] Using httpx results: {httpx_file}")
            return httpx_file
        
        # Fallback to subdomain list
        subdomain_file = f"{self.output_dir}/all_subdomains.txt"
        if os.path.exists(subdomain_file):
            print(f"[*] Using subdomain list: {subdomain_file}")
            # Prepare URLs with http/https prefix
            return self.prepare_urls(subdomain_file)
        
        # Last resort - just the domain
        print(f"[*] Using domain only: {self.domain}")
        temp_file = f"{self.output_dir}/temp_crawl_target.txt"
        with open(temp_file, 'w') as f:
            f.write(f"https://{self.domain}\n")
            f.write(f"http://{self.domain}\n")
        return temp_file
    
    def prepare_urls(self, input_file):
        """Add http/https prefix to domains"""
        output_file = f"{self.output_dir}/urls_for_crawl.txt"
        
        try:
            with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
                for line in infile:
                    url = line.strip()
                    if url and not url.startswith('#'):
                        if not url.startswith(('http://', 'https://')):
                            outfile.write(f"https://{url}\n")
                        else:
                            outfile.write(f"{url}\n")
            
            print(f"[✓] Prepared URLs for crawling")
            return output_file
            
        except Exception as e:
            print(f"[!] Error preparing URLs: {str(e)}")
            return None
    
    def run_katana(self, target_file):
        """Run Katana web crawler"""
        print("[*] Starting web crawling with Katana...")
        print("[*] This may take a while depending on target size...")
        
        output_file = f"{self.output_dir}/katana.txt"
        
        # Katana command
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
            # Run katana
            process = subprocess.Popen(
                katana_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Stream output
            for line in process.stdout:
                print(f"  {line.strip()}")
            
            process.wait(timeout=1800)  # 30 minute timeout
            
            if process.returncode == 0 or os.path.exists(output_file):
                print(f"[✓] Crawling completed")
                return True
            else:
                print(f"[!] Crawling completed with warnings")
                return True  # Still consider successful if output exists
                
        except subprocess.TimeoutExpired:
            print("[!] Crawling timed out")
            process.kill()
            return False
        except FileNotFoundError:
            print("[!] katana not found. Install with: go install github.com/projectdiscovery/katana/cmd/katana@latest")
            return False
        except KeyboardInterrupt:
            print("\n[!] Crawl interrupted by user")
            process.kill()
            return False
        except Exception as e:
            print(f"[!] Error during crawling: {str(e)}")
            return False
    
    def parse_results(self):
        """Parse and summarize crawl results"""
        results_file = f"{self.output_dir}/katana.txt"
        summary_file = f"{self.output_dir}/katana_summary.txt"
        
        if not os.path.exists(results_file):
            print("[!] No crawl results found")
            return
        
        print("[*] Parsing crawl results...")
        
        try:
            # Read all URLs
            with open(results_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                print("[!] No URLs found in crawl results")
                return
            
            # Categorize URLs
            endpoints = set()
            parameters = set()
            js_files = []
            api_endpoints = []
            
            for url in urls:
                # Extract endpoint (path without query)
                if '?' in url:
                    endpoint = url.split('?')[0]
                    endpoints.add(endpoint)
                    # Extract parameters
                    query = url.split('?')[1]
                    for param in query.split('&'):
                        if '=' in param:
                            parameters.add(param.split('=')[0])
                else:
                    endpoints.add(url)
                
                # Identify interesting files
                if url.endswith('.js'):
                    js_files.append(url)
                elif '/api/' in url or '/v1/' in url or '/v2/' in url:
                    api_endpoints.append(url)
            
            # Create summary
            with open(summary_file, 'w') as f:
                f.write(f"WEB CRAWLING SUMMARY FOR: {self.domain}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Total URLs Discovered: {len(urls)}\n")
                f.write(f"Unique Endpoints: {len(endpoints)}\n")
                f.write(f"Unique Parameters: {len(parameters)}\n")
                f.write(f"JavaScript Files: {len(js_files)}\n")
                f.write(f"API Endpoints: {len(api_endpoints)}\n")
                f.write("\n" + "=" * 60 + "\n\n")
                
                # Parameters section
                if parameters:
                    f.write("Discovered Parameters:\n")
                    f.write("-" * 40 + "\n")
                    for param in sorted(parameters)[:50]:  # Limit to 50
                        f.write(f"  {param}\n")
                    if len(parameters) > 50:
                        f.write(f"  ... and {len(parameters) - 50} more\n")
                    f.write("\n")
                
                # JavaScript files
                if js_files:
                    f.write("JavaScript Files:\n")
                    f.write("-" * 40 + "\n")
                    for js in js_files[:20]:  # Limit to 20
                        f.write(f"  {js}\n")
                    if len(js_files) > 20:
                        f.write(f"  ... and {len(js_files) - 20} more\n")
                    f.write("\n")
                
                # API endpoints
                if api_endpoints:
                    f.write("API Endpoints:\n")
                    f.write("-" * 40 + "\n")
                    for api in api_endpoints[:30]:  # Limit to 30
                        f.write(f"  {api}\n")
                    if len(api_endpoints) > 30:
                        f.write(f"  ... and {len(api_endpoints) - 30} more\n")
                    f.write("\n")
            
            print(f"[✓] Summary saved to: {summary_file}")
            print(f"[✓] Total URLs discovered: {len(urls)}")
            print(f"    - Unique endpoints: {len(endpoints)}")
            print(f"    - Parameters found: {len(parameters)}")
            print(f"    - JavaScript files: {len(js_files)}")
            print(f"    - API endpoints: {len(api_endpoints)}")
            
        except Exception as e:
            print(f"[!] Error parsing results: {str(e)}")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>")
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"WEB CRAWLING - {domain}")
    print("=" * 60)
    
    # Check if katana is installed
    if subprocess.run(['which', 'katana'], capture_output=True).returncode != 0:
        print("[!] katana is not installed")
        print("[!] Install with: go install github.com/projectdiscovery/katana/cmd/katana@latest")
        sys.exit(1)
    
    crawler = WebCrawler(domain, output_dir)
    
    # Get target file
    target_file = crawler.get_target_file()
    if not target_file:
        print("[!] No targets available for crawling")
        sys.exit(1)
    
    print()
    
    # Run katana
    success = crawler.run_katana(target_file)
    
    if success:
        print()
        crawler.parse_results()
    
    print("\n[✓] Web crawling complete!")
    print(f"[*] Results saved to: {output_dir}/katana.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()
