#!/usr/bin/env python3

"""
Subdomain Enumeration Module 
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd_list, description, timeout=600):
    """Run command as list, handle errors"""
    print(f"[*] {description}...")
    try:
        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"[✓] {description} completed")
            return result.stdout
        else:
            print(f"[!] {description} failed: {result.stderr}", file=sys.stderr)
            return ""
    except subprocess.TimeoutExpired:
        print(f"[!] {description} timed out", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"[!] Error in {description}: {str(e)}", file=sys.stderr)
        return ""

def deduplicate_subdomains(input_files, output_file):
    """Combine and deduplicate subdomain results"""
    subdomains = set()
    
    for file_path in input_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        subdomain = line.strip().lower()
                        if subdomain and not subdomain.startswith('#'):
                            subdomains.add(subdomain)
            except Exception as e:
                print(f"[!] Error reading {file_path}: {e}", file=sys.stderr)
    
    # Sort and save
    try:
        with open(output_file, 'w') as f:
            for subdomain in sorted(subdomains):
                f.write(f"{subdomain}\n")
        
        print(f"[✓] Found {len(subdomains)} unique subdomains")
        return len(subdomains)
    except Exception as e:
        print(f"[!] Error writing results: {e}", file=sys.stderr)
        return 0

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>", file=sys.stderr)
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"SUBDOMAIN ENUMERATION - {domain}")
    print("=" * 60)
    
    # Verify tools
    required_tools = ['amass', 'subfinder', 'assetfinder']
    missing = [tool for tool in required_tools if not subprocess.run(['which', tool], capture_output=True).returncode == 0]
    
    if missing:
        print(f"[!] Missing tools: {', '.join(missing)}", file=sys.stderr)
        print("[!] Please run installer.sh", file=sys.stderr)
        sys.exit(1)
    
    # Create temp directory
    temp_dir = f"{output_dir}/temp_subdomains"
    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    
    # Output files
    amass_output = f"{temp_dir}/amass.txt"
    subfinder_output = f"{temp_dir}/subfinder.txt"
    assetfinder_output = f"{temp_dir}/assetfinder.txt"
    final_output = f"{output_dir}/all_subdomains.txt"
    
    # Run tools with lists
    run_command(["amass", "enum", "-passive", "-d", domain, "-o", amass_output], "Amass passive enumeration")
    run_command(["subfinder", "-d", domain, "-silent", "-o", subfinder_output], "Subfinder enumeration")
    run_command(["assetfinder", "--subs-only", domain], "Assetfinder enumeration")  # Redirect output separately
    with open(assetfinder_output, 'w') as f:
        f.write(run_command(["assetfinder", "--subs-only", domain], "Assetfinder enumeration"))
    
    # Combine
    print("\n[*] Combining and deduplicating results...")
    total = deduplicate_subdomains([amass_output, subfinder_output, assetfinder_output], final_output)
    
    # Cleanup
    for file in [amass_output, subfinder_output, assetfinder_output]:
        if os.path.exists(file):
            os.remove(file)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)
    
    print(f"\n[✓] Results saved to: {final_output}")
    print(f"[✓] Total unique subdomains: {total}")
    print("=" * 60)

if __name__ == "__main__":
    main()
