#!/usr/bin/env python3

"""
Report Generation Module (Fixed)
Fixes: Better HTML generation, error handling, data parsing
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

class ReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.report_file = f"{output_dir}/report.html"
    
    def read_file(self, filepath):
        """Safely read file content"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            print(f"[!] Error reading {filepath}: {str(e)}")
        return ""
    
    def read_lines(self, filepath):
        """Read file as lines"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"[!] Error reading {filepath}: {str(e)}")
        return []
    
    def parse_subdomains(self):
        """Parse subdomain results"""
        subdomains = self.read_lines(f"{self.output_dir}/all_subdomains.txt")
        return subdomains
    
    def parse_dns(self):
        """Parse DNS results"""
        dns_records = self.read_file(f"{self.output_dir}/dns/records.txt")
        zone_transfer = self.read_file(f"{self.output_dir}/dns/zone_attempt.txt")
        misconfig = self.read_file(f"{self.output_dir}/dns/misconfig.txt")
        
        return {
            'records': dns_records,
            'zone_transfer': zone_transfer,
            'misconfig': misconfig
        }
    
    def parse_ports(self):
        """Parse port scan results"""
        port_summary = self.read_file(f"{self.output_dir}/ports/port_summary.txt")
        if not port_summary:
            port_summary = self.read_file(f"{self.output_dir}/ports/nmap.txt")
        
        return port_summary
    
    def parse_vulnerabilities(self):
        """Parse vulnerability scan results"""
        summary = self.read_file(f"{self.output_dir}/nuclei/summary.txt")
        if not summary:
            summary = self.read_file(f"{self.output_dir}/nuclei/nuclei.log")
        
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
                    if file.endswith('.png'):
                        screenshots.append({
                            'filename': file,
                            'path': f"aquatone/screenshots/{file}",
                            'thumb': f"aquatone/thumbs/thumb_{file}"
                        })
        
        return screenshots
    
    def parse_crawl(self):
        """Parse crawl results"""
        crawl_results = self.read_lines(f"{self.output_dir}/katana.txt")
        return crawl_results
    
    def generate_html(self):
        """Generate complete HTML report"""
        print("[*] Generating HTML report...")
        
        # Collect all data
        subdomains = self.parse_subdomains()
        dns_data = self.parse_dns()
        port_data = self.parse_ports()
        vuln_data = self.parse_vulnerabilities()
        screenshots = self.get_screenshots()
        crawl_data = self.parse_crawl()
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>T-SLYTHERINS Reconnaissance Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}
        
        h1 {{
            color: #00d9ff;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
        }}
        
        .subtitle {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        .section {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 217, 255, 0.2);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }}
        
        .section h2 {{
            color: #00d9ff;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(0, 217, 255, 0.3);
        }}
        
        .badge {{
            display: inline-block;
            background: rgba(0, 217, 255, 0.2);
            color: #00d9ff;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-right: 10px;
        }}
        
        pre {{
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 217, 255, 0.2);
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            color: #0ff;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        .subdomain-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 10px;
        }}
        
        .subdomain-item {{
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #00d9ff;
            word-break: break-all;
        }}
        
        .screenshot-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .screenshot-item {{
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(0, 217, 255, 0.2);
            border-radius: 8px;
            padding: 15px;
            transition: transform 0.3s;
        }}
        
        .screenshot-item:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(0, 217, 255, 0.3);
        }}
        
        .screenshot-item img {{
            width: 100%;
            border-radius: 5px;
            cursor: pointer;
        }}
        
        .screenshot-item p {{
            text-align: center;
            margin-top: 10px;
            color: #00d9ff;
            font-size: 0.9em;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: rgba(0, 217, 255, 0.1);
            border: 1px solid rgba(0, 217, 255, 0.3);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            color: #00d9ff;
            font-weight: bold;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        
        .url-list {{
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .url-item {{
            background: rgba(0, 0, 0, 0.2);
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #0ff;
            word-break: break-all;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: #7f8c8d;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 T-SLYTHERINS</h1>
            <p class="subtitle">Reconnaissance Report</p>
            <p class="subtitle">Generated: {timestamp}</p>
        </header>
        
        <!-- Statistics -->
        <div class="section">
            <h2>📊 Overview Statistics</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(subdomains)}</div>
                    <div class="stat-label">Subdomains</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(screenshots)}</div>
                    <div class="stat-label">Screenshots</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(crawl_data)}</div>
                    <div class="stat-label">Crawled URLs</div>
                </div>
            </div>
        </div>
        
        <!-- Subdomains -->
        <div class="section">
            <h2>🌐 Discovered Subdomains</h2>
            <span class="badge">{len(subdomains)} found</span>
            <div class="subdomain-list">
"""
        
        for subdomain in subdomains[:100]:  # Limit to 100 for readability
            html += f'                <div class="subdomain-item">{subdomain}</div>\n'
        
        if len(subdomains) > 100:
            html += f'                <div class="subdomain-item">...and {len(subdomains) - 100} more</div>\n'
        
        html += """            </div>
        </div>
        
        <!-- DNS Information -->
        <div class="section">
            <h2>🔍 DNS Information</h2>
            <h3>DNS Records</h3>
            <pre>{}</pre>
            <h3>Zone Transfer Test</h3>
            <pre>{}</pre>
            <h3>Misconfiguration Check</h3>
            <pre>{}</pre>
        </div>
        
        <!-- Port Scan Results -->
        <div class="section">
            <h2>🔓 Port Scan Results</h2>
            <pre>{}</pre>
        </div>
        
        <!-- Vulnerability Findings -->
        <div class="section">
            <h2>⚠️ Vulnerability Findings</h2>
            <pre>{}</pre>
        </div>
        
        <!-- Screenshots -->
        <div class="section">
            <h2>📸 Screenshot Gallery</h2>
            <span class="badge">{} captured</span>
            <div class="screenshot-gallery">
""".format(
            dns_data['records'] or "No DNS records available",
            dns_data['zone_transfer'] or "No zone transfer data",
            dns_data['misconfig'] or "No misconfiguration data",
            port_data or "No port scan data available",
            vuln_data or "No vulnerability data available",
            len(screenshots)
        )
        
        for screenshot in screenshots[:50]:  # Limit to 50 screenshots
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
        
        for url in crawl_data[:500]:  # Limit to 500 URLs
            html += f'                <div class="url-item">{url}</div>\n'
        
        if len(crawl_data) > 500:
            html += f'                <div class="url-item">...and {len(crawl_data) - 500} more URLs</div>\n'
        
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
            print(f"[!] Error writing report: {str(e)}")
            return False

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output_dir>")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    
    if not os.path.exists(output_dir):
        print(f"[!] Output directory not found: {output_dir}")
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
