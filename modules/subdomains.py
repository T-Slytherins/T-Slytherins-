#!/usr/bin/env python3

"""
Subdomain Enumeration Module 
Fixes: Better error handling, output management, tool verification
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description):
    """Run command and handle errors"""
    print(f"[*] {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            print(f"[✓] {description} completed")
            return result.stdout
        else:
            print(f"[!] {description} failed: {result.stderr}")
            return ""
    except subprocess.TimeoutExpired:
        print(f"[!] {description} timed out")
        return ""
    except Exception as e:
        print(f"[!] Error in {description}: {str(e)}")
        return ""

def deduplicate_subdomains(input_files, output_file):
    """Combine and deduplicate subdomain results"""
    subdomains = set()
    
    for file_path in input_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        subdomain = line.strip()
                        if subdomain and not subdomain.startswith('#'):
                            subdomains.add(subdomain.lower())
            except Exception as e:
                print(f"[!] Error reading {file_path}: {e}")
    
    # Sort and save
    try:
        with open(output_file, 'w') as f:
            for subdomain in sorted(subdomains):
                f.write(f"{subdomain}\n")
        
        print(f"[✓] Found {len(subdomains)} unique subdomains")
        return len(subdomains)
    except Exception as e:
        print(f"[!] Error writing results: {e}")
        return 0

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>")
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"SUBDOMAIN ENUMERATION - {domain}")
    print("=" * 60)
    
    # Verify tools exist
    required_tools = ['amass', 'subfinder', 'assetfinder']
    missing_tools = []
    
    for tool in required_tools:
        if subprocess.run(['which', tool], capture_output=True).returncode != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"[!] Missing tools: {', '.join(missing_tools)}")
        print("[!] Please run installer.sh")
        sys.exit(1)
    
    # Create temp directory for individual results
    temp_dir = f"{output_dir}/temp_subdomains"
    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    
    # Output files
    amass_output = f"{temp_dir}/amass.txt"
    subfinder_output = f"{temp_dir}/subfinder.txt"
    assetfinder_output = f"{temp_dir}/assetfinder.txt"
    final_output = f"{output_dir}/all_subdomains.txt"
    
    # Run Amass (passive mode)
    amass_cmd = f"amass enum -passive -d {domain} -o {amass_output}"
    run_command(amass_cmd, "Amass passive enumeration")
    
    # Run Subfinder
    subfinder_cmd = f"subfinder -d {domain} -silent -o {subfinder_output}"
    run_command(subfinder_cmd, "Subfinder enumeration")
    
    # Run Assetfinder
    assetfinder_cmd = f"assetfinder --subs-only {domain} > {assetfinder_output}"
    run_command(assetfinder_cmd, "Assetfinder enumeration")
    
    # Combine and deduplicate
    print("\n[*] Combining and deduplicating results...")
    total = deduplicate_subdomains(
        [amass_output, subfinder_output, assetfinder_output],
        final_output
    )
    
    # Cleanup temp files
    try:
        for file in [amass_output, subfinder_output, assetfinder_output]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(temp_dir)
    except:
        pass
    
    print(f"\n[✓] Results saved to: {final_output}")
    print(f"[✓] Total unique subdomains: {total}")
    print("=" * 60)

if __name__ == "__main__":
    main()
