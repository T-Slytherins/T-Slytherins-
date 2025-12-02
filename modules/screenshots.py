#!/usr/bin/env python3

"""
Screenshot Module
"""

import sys
import subprocess
import os
from pathlib import Path
from PIL import Image
from shutil import which

class ScreenshotTaker:
    def __init__(self, domain, output_dir):
        self.domain = domain
        self.output_dir = output_dir
        self.aquatone_dir = f"{output_dir}/aquatone"
        self.screenshots_dir = f"{self.aquatone_dir}/screenshots"
        self.thumbs_dir = f"{self.aquatone_dir}/thumbs"
        
        Path(self.screenshots_dir).mkdir(parents=True, exist_ok=True)
        Path(self.thumbs_dir).mkdir(parents=True, exist_ok=True)
    
    def check_tools(self):
        """Check if required tools are installed"""
        if not which('aquatone'):
            print("[!] aquatone is not installed", file=sys.stderr)
            return False
        return True
    
    def get_target_file(self):
        """Find the target file for screenshots"""
        httpx_file = f"{self.output_dir}/httpx_results.txt"
        if os.path.exists(httpx_file):
            print(f"[✓] Using httpx results: {httpx_file}")
            return httpx_file
        
        subdomain_file = f"{self.output_dir}/all_subdomains.txt"
        if os.path.exists(subdomain_file):
            print(f"[*] Using subdomain file: {subdomain_file}")
            return self.prepare_urls(subdomain_file)
        
        print(f"[!] No target file found", file=sys.stderr)
        return None
    
    def prepare_urls(self, input_file):
        """Prepare URLs with http/https prefix, filter invalid"""
        output_file = f"{self.output_dir}/urls_for_screenshots.txt"
        
        try:
            with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
                for line in infile:
                    url = line.strip()
                    if url and not url.startswith('#') and '.' in url:  # Basic filter
                        if not url.startswith(('http://', 'https://')):
                            outfile.write(f"https://{url}\n")
                            outfile.write(f"http://{url}\n")
                        else:
                            outfile.write(f"{url}\n")
            print(f"[✓] Prepared URLs: {output_file}")
            return output_file
        except Exception as e:
            print(f"[!] Error preparing URLs: {str(e)}", file=sys.stderr)
            return None
    
    def run_aquatone(self, target_file):
        """Run aquatone using Popen for pipe"""
        print("[*] Starting screenshot capture with aquatone...")
        print("[*] This may take a while...")
        
        try:
            with open(target_file, 'r') as input_f:
                proc = subprocess.Popen(["aquatone", "-out", self.aquatone_dir], stdin=input_f, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                output, _ = proc.communicate()
                if proc.returncode == 0:
                    print(f"[✓] aquatone completed: {output.decode()}")
                    return True
                else:
                    print(f"[!] aquatone failed", file=sys.stderr)
                    return False
        except Exception as e:
            print(f"[!] Error running aquatone: {str(e)}", file=sys.stderr)
            return False
    
    def generate_thumbnails(self):
        """Generate thumbnails for screenshots"""
        print("[*] Generating thumbnails...")
        
        thumbnail_size = (400, 300)
        thumb_count = 0
        fail_count = 0
        
        for screenshot_file in os.listdir(self.screenshots_dir):
            if screenshot_file.endswith(('.png', '.jpg')):
                try:
                    img_path = os.path.join(self.screenshots_dir, screenshot_file)
                    img = Image.open(img_path)
                    img.thumbnail(thumbnail_size)
                    thumb_path = os.path.join(self.thumbs_dir, f"thumb_{screenshot_file}")
                    img.save(thumb_path)
                    thumb_count += 1
                except Exception as e:
                    print(f"[!] Error thumbnail {screenshot_file}: {str(e)}", file=sys.stderr)
                    fail_count += 1
        
        print(f"[✓] Generated {thumb_count} thumbnails ({fail_count} failures)")
        print(f"[✓] Thumbnails saved to: {self.thumbs_dir}")
    
    def create_gallery_html(self):
        """Create a simple HTML gallery of screenshots"""
        html_file = f"{self.aquatone_dir}/gallery.html"
        
        thumbs = [file for file in os.listdir(self.thumbs_dir) if file.endswith('.png')]
        
        if not thumbs:
            print("[!] No thumbnails found for gallery", file=sys.stderr)
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
            print(f"[!] Error creating gallery: {str(e)}", file=sys.stderr)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <domain> <output_dir>", file=sys.stderr)
        sys.exit(1)
    
    domain = sys.argv[1]
    output_dir = sys.argv[2]
    
    print("=" * 60)
    print(f"SCREENSHOT CAPTURE - {domain}")
    print("=" * 60)
    
    taker = ScreenshotTaker(domain, output_dir)
    
    if not taker.check_tools():
        print("[!] Please run installer.sh", file=sys.stderr)
        sys.exit(1)
    
    target_file = taker.get_target_file()
    if not target_file:
        print("[!] No targets available for screenshots", file=sys.stderr)
        sys.exit(1)
    
    print()
    
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
