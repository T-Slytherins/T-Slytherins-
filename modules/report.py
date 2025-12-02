#!/usr/bin/env python3

"""
Report Generation Module 
"""

import sys
import os
import html  # For escaping
from datetime import datetime
from pathlib import Path

class ReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.report_file = f"{output_dir}/report.html"
    
    def read_file_chunked(self, filepath, max_lines=1000):
        """Read file chunked to avoid memory issues"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            lines.append("... [Truncated for report]")
                            break
                        lines.append(html.escape(line.strip()))
                    return "\n".join(lines)
        except Exception as e:
            print(f"[!] Error reading {filepath}: {str(e)}", file=sys.stderr)
        return ""
    
    def read_lines(self, filepath, max_lines=500):
        """Read file as lines, limited"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            lines.append("... [Truncated]")
                            break
                        lines.append(html.escape(line.strip()))
                    return lines
        except Exception as e:
            print(f"[!] Error reading {filepath}: {str(e)}", file=sys.stderr)
        return []
    
    def parse_subdomains(self):
        """Parse subdomain results"""
        subdomains = self.read_lines(f"{self.output_dir}/all_subdomains.txt")
        return subdomains
    
    def parse_dns(self):
        """Parse DNS results"""
        dns_records = self.read_file_chunked(f"{self.output_dir}/dns/records.txt")
        zone_transfer = self.read_file_chunked(f"{self.output_dir}/dns/zone_attempt.txt")
        misconfig = self.read_file_chunked(f"{self.output_dir}/dns/misconfig.txt")
        
        return {
            'records': dns_records,
            'zone_transfer': zone_transfer,
            'misconfig': misconfig
        }
    
    def parse_ports(self):
        """Parse port scan results"""
        port_summary = self.read_file_chunked(f"{self.output_dir}/ports/port_summary.txt")
        if not port_summary:
            port_summary = self.read_file_chunked(f"{self.output_dir}/ports/nmap.txt")
        return port_summary
    
    def parse_vulnerabilities(self):
        """Parse vulnerability scan results"""
        summary = self.read_file_chunked(f"{self.output_dir}/nuclei/summary.txt")
        if not summary:
            summary = self.read_file_chunked(f"{self.output_dir}/nuclei/nuclei.log")
        return summary
    
    def get_screenshots(self):
        """Get list of screenshots"""
        screenshots = []
        
        screenshot_dirs = [
            f"{self.output_dir}/aquatone/screenshots",
            f"{self.output_dir}/aquatone"
        ]
        
        for screenshot_dir in screenshot_dirs:
            if os.path.exists(screenshot_dir):
                for file in sorted(os.listdir(screenshot_dir)):
                    if file.endswith(('.png', '.jpg')):
                        screenshots.append({
                            'path': f"{screenshot_dir}/{file}",
                            'thumb': f"{screenshot_dir}/thumbs/thumb_{file}" if os.path.exists(f"{screenshot_dir}/thumbs/thumb_{file}") else f"{screenshot_dir}/{file}",
                            'filename': html.escape(file)
                        })
        return screenshots
    
    def parse_crawl(self):
        """Parse crawl results"""
        crawl_file = f"{self.output_dir}/katana.txt"
        return self.read_lines(crawl_file)
    
    def generate_html(self):
        """Generate HTML report with escaping"""
        subdomains = self.parse_subdomains()
        dns_data = self.parse_dns()
        port_data = self.parse_ports()
        vuln_data = self.parse_vulnerabilities()
        screenshots = self.get_screenshots()
        crawl_data = self.parse_crawl()
        
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>T-SLYTHERINS Report</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #0ff; text-align: center; }
        .section { background: #2a2a2a; border: 1px solid #444; border-radius: 8px; padding: 20px; margin: 20px 0; }
        h2 { color: #0ff; }
        pre { background: #000; padding: 10px; border-radius: 4px; overflow-x: auto; }
        .badge { background: #0ff; color: #000; padding: 5px 10px; border-radius: 20px; font-size: 12px; }
        .screenshot-gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }
        .screenshot-item img { width: 100%; cursor: pointer; border-radius: 4px; }
        .url-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 5px; }
        .url-item { background: #333; padding: 5px; border-radius: 4px; font-size: 12px; }
        footer { text-align: center; font-size: 12px; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <h1>T-SLYTHERINS Recon Report</h1>
        <p>Report generated: {}</p>
        
        <!-- Subdomains -->
        <div class="section">
            <h2>🔍 Subdomains</h2>
            <span class="badge">{} found</span>
            <pre>{}</pre>
        </div>
        
        <!-- DNS Records -->
        <div class="section">
            <h2>📡 DNS Records</h2>
            <pre>{}</pre>
        </div>
        
        <!-- Zone Transfer -->
        <div class="section">
            <h2>🔄 Zone Transfer Attempt</h2>
            <pre>{}</pre>
        </div>
        
        <!-- DNS Misconfigurations -->
        <div class="section">
            <h2>⚠️ DNS Misconfigurations</h2>
            <pre>{}</pre>
        </div>
        
        <!-- Port Scan -->
        <div class="section">
            <h2>🚪 Port Scan Results</h2>
            <pre>{}</pre>
        </div>
        
        <!-- Vulnerabilities -->
        <div class="section">
            <h2>🛡️ Vulnerabilities</h2>
            <pre>{}</pre>
        </div>
        
        <!-- Screenshots -->
        <div class="section">
            <h2>📸 Screenshot Gallery</h2>
            <span class="badge">{} captured</span>
            <div class="screenshot-gallery">
""".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            len(subdomains),
            "\n".join(subdomains) or "No subdomains found",
            dns_data['records'] or "No DNS records available",
            dns_data['zone_transfer'] or "No zone transfer data",
            dns_data['misconfig'] or "No misconfiguration data",
            port_data or "No port scan data available",
            vuln_data or "No vulnerability data available",
            len(screenshots)
        )
        
        for screenshot in screenshots:
            html += f"""                <div class="screenshot-item">
                    <img src="{screenshot['thumb']}" alt="{screenshot['filename']}" 
                         onclick="window.open('{screenshot['path']}')">
                    <p>{screenshot['filename']}</p>
                </div>
"""
        
        html += """            </div>
        </div>
        
        <!-- Crawled URLs -->
        <div class="section">
            <h2>🕷️ Crawled URLs</h2>
            <span class="badge">{} URLs</span>
            <div class="url-list">
""".format(len(crawl_data))
        
        for url in crawl_data:
            html += f'                <div class="url-item">{url}</div>\n'
        
        html += """            </div>
        </div>
        
        <footer>
            <p>🐍 T-SLYTHERINS Reconnaissance Suite</p>
            <p>Advanced Penetration Testing Framework</p>
        </footer>
    </div>
</body>
</html>
"""
        
        # Save report
        try:
            with open(self.report_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"[✓] Report generated: {self.report_file}")
            print(f"[✓] Open in browser: file://{os.path.abspath(self.report_file)}")
            return True
            
        except Exception as e:
            print(f"[!] Error writing report: {str(e)}", file=sys.stderr)
            return False

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output_dir>", file=sys.stderr)
        sys.exit(1)
    
    output_dir = sys.argv[1]
    
    if not os.path.exists(output_dir):
        print(f"[!] Output directory not found: {output_dir}", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 60)
    print("GENERATING HTML REPORT")
    print("=" * 60)
    
    generator = ReportGenerator(output_dir)
    success = generator.generate_html()
    
    if not success:
        sys.exit(1)
    
    print("=" * 60)

if __name__ == "__main__":
    main()
