#!/usr/bin/env python3

"""
Screenshot Module (Fixed)
Fixes: Better error handling, fallback options, thumbnail generation
"""

import sys
import subprocess
import os
from pathlib import Path
from PIL import Image

class ScreenshotTaker:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
        self.aquatone_dir = f"{output_dir}/aquatone"
        self.screenshots_dir = f"{self.aquatone_dir}/screenshots"
        self.thumbs_dir = f"{self.aquatone_dir}/thumbs"
        
        # Create directories
        Path(self.screenshots_dir).mkdir(parents=True, exist_ok=True)
        Path(self.thumbs_dir).mkdir(parents=True, exist_ok=True)
    
    def check_tools(self):
        """Check if required tools are installed"""
        if subprocess.run(['which', 'aquatone'], capture_output=True).returncode != 0:
            print("[!] aquatone is not installed")
            return False
        return True
    
    def get_target_file(self):
        """Find the target file for screenshots"""
        # Check for httpx results first
        httpx_file = f"{self.output_dir}/httpx_results.txt"
        if os.path.exists(httpx_file):
            print(f"[✓] Using httpx results: {httpx_file}")
            return httpx_file
        
        # Fall back to subdomains
        subdomain_file = f"{self.output_dir}/all_subdomains.txt"
        if os.path.exists(subdomain_file):
            print(f"[*] Using subdomain file: {subdomain_file}")
            # Add http:// prefix for aquatone
            return self.prepare_urls(subdomain_file)
        
        print("[!] No target file found")
        return None
    
    def prepare_urls(self, input_file):
        """Prepare URLs with http/https prefix"""
        output_file = f"{self.output_dir}/urls_for_screenshots.txt"
        
        try:
            with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
                for line in infile:
                    url = line.strip()
                    if url and not url.startswith('#'):
                        # Add protocol if missing
                        if not url.startswith(('http://', 'https://')):
                            outfile.write(f"https://{url}\n")
                            outfile.write(f"http://{url}\n")
                        else:
                            outfile.write(f"{url}\n")
            
            print(f"[✓] Prepared URLs: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"[!] Error preparing URLs: {str(e)}")
            return None
    
    def run_aquatone(self, target_file):
        """Run aquatone to capture screenshots"""
        print("[*] Starting screenshot capture with aquatone...")
        print("[*] This may take a while depending on number of targets...")
        
        aquatone_cmd = f"cat {target_file} | aquatone -out {self.aquatone_dir}"
        
        try:
            process = subprocess.Popen(
                aquatone_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Stream output
            for line in process.stdout:
                print(f"  {line.strip()}")
            
            process.wait(timeout=1800)  # 30 minute timeout
            
            if process.returncode == 0:
                print("[✓] Screenshot capture completed")
                return True
            else:
                print("[!] Screenshot capture completed with warnings")
                return True  # Still consider successful
                
        except subprocess.TimeoutExpired:
            print("[!] Screenshot capture timed out")
            process.kill()
            return False
        except KeyboardInterrupt:
            print("\n[!] Capture interrupted by user")
            process.kill()
            return False
        except Exception as e:
            print(f"[!] Error during screenshot capture: {str(e)}")
            return False
    
    def generate_thumbnails(self):
        """Generate thumbnails from screenshots"""
        print("[*] Generating thumbnails...")
        
        # Look for screenshots in aquatone output
        screenshot_sources = [
            f"{self.aquatone_dir}/screenshots",
            self.aquatone_dir
        ]
        
        screenshot_files = []
        for source_dir in screenshot_sources:
            if os.path.exists(source_dir):
                for file in os.listdir(source_dir):
                    if file.endswith('.png'):
                        screenshot_files.append(os.path.join(source_dir, file))
        
        if not screenshot_files:
            print("[!] No screenshots found to process")
            return
        
        print(f"[*] Processing {len(screenshot_files)} screenshots...")
        
        thumbnail_count = 0
        for screenshot_path in screenshot_files:
            try:
                # Open image
                img = Image.open(screenshot_path)
                
                # Create thumbnail (max 400x300)
                img.thumbnail((400, 300), Image.Resampling.LANCZOS)
                
                # Save thumbnail
                filename = os.path.basename(screenshot_path)
                thumb_path = os.path.join(self.thumbs_dir, f"thumb_{filename}")
                img.save(thumb_path, 'PNG', optimize=True)
                
                thumbnail_count += 1
                
            except Exception as e:
                print(f"[!] Error processing {screenshot_path}: {str(e)}")
                continue
        
        print(f"[✓] Generated {thumbnail_count} thumbnails")
        print(f"[✓] Thumbnails saved to: {self.thumbs_dir}")
    
    def create_gallery_html(self):
        """Create a simple HTML gallery of screenshots"""
        html_file = f"{self.aquatone_dir}/gallery.html"
        
        # Get all thumbnails
        thumbs = []
        if os.path.exists(self.thumbs_dir):
            for file in sorted(os.listdir(self.thumbs_dir)):
                if file.endswith('.png'):
                    thumbs.append(file)
        
        if not thumbs:
            print("[!] No thumbnails found for gallery")
            return
        
        try:
            with open(html_file, 'w') as f:
                f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Screenshot Gallery</title>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { text-align: center; color: #0ff; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; }
        .item { background: #2a2a2a; border: 1px solid #444; border-radius: 8px; padding: 10px; }
        .item img { width: 100%; cursor: pointer; border-radius: 4px; }
        .item p { text-align: center; margin: 10px 0 0 0; font-size: 12px; color: #0ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Screenshot Gallery</h1>
        <div class="gallery">
""")
                
                for thumb in thumbs:
                    # Get original screenshot name
                    original = thumb.replace('thumb_', '')
                    f.write(f"""
            <div class="item">
                <img src="thumbs/{thumb}" alt="{original}" onclick="window.open('screenshots/{original}')">
                <p>{original}</p>
            </div>
""")
                
                f.write("""
        </div>
    </div>
</body>
</html>
""")
            
            print(f"[✓] Gallery created: {html_file}")
            
        except Exception as e:
            print(f"[!] Error creating gallery: {str(e)}")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>")
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"SCREENSHOT CAPTURE - {domain}")
    print("=" * 60)
    
    taker = ScreenshotTaker(domain, output_dir)
    
    # Check tools
    if not taker.check_tools():
        print("[!] Please run installer.sh")
        sys.exit(1)
    
    # Get target file
    target_file = taker.get_target_file()
    if not target_file:
        print("[!] No targets available for screenshots")
        sys.exit(1)
    
    print()
    
    # Run aquatone
    success = taker.run_aquatone(target_file)
    
    if success:
        print()
        taker.generate_thumbnails()
        print()
        taker.create_gallery_html()
    
    print("\n[✓] Screenshot capture complete!")
    print(f"[*] Results saved to: {taker.aquatone_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
