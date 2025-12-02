 T-SLYTHERINS Reconnaissance Suite (Professional Edition)
https://img.shields.io/badge/version-2.1.0-blue
https://img.shields.io/badge/python-3.8%252B-green
https://img.shields.io/badge/license-MIT-orange
https://img.shields.io/badge/platform-Linux%2520%257C%2520Kali-brightgreen

Advanced Automated Reconnaissance Framework for Security Professionals

📋 Table of Contents
✨ Overview
🚀 Features
📊 System Requirements
⚡ Quick Installation
🔧 Detailed Installation
🎯 Usage Guide
📁 Output Structure
🔧 Module Documentation
🛠️ Troubleshooting
⚖️ Legal & Ethics
🤝 Contributing
📞 Support

✨ Overview
T-SLYTHERINS is a professional-grade reconnaissance framework that automates the entire information gathering phase during penetration testing and security assessments. Built with modularity and efficiency in mind, it integrates industry-standard tools, executes them in parallel, captures comprehensive data, and generates detailed HTML reports.

What Makes This Edition Special?
✅ Fixed Import Issues - Resolved all Python import errors and module path problems
✅ Professional Error Handling - Graceful degradation and comprehensive logging
✅ Virtual Environment Ready - Isolated Python environment for clean dependencies
✅ Parallel Execution - Multi-terminal simultaneous module execution
✅ Beautiful Reporting - Dark-themed HTML reports with screenshot galleries

🚀 Features
🔍 Comprehensive Reconnaissance Suite
Module	Tool	Description
Subdomain Enumeration	Amass, Subfinder, Assetfinder	Multi-source subdomain discovery with deduplication
DNS Reconnaissance	dnspython	Full DNS records, zone transfer tests, misconfig detection
Port Scanning	Nmap	Top 1000 ports with service and version detection
HTTP Probing	HTTPX	Live host detection, status codes, technology fingerprinting
Vulnerability Scanning	Nuclei	3000+ vulnerability templates with severity categorization
Web Crawling	Katana	JavaScript-aware crawling with endpoint discovery
Screenshot Capture	Aquatone	Full-page screenshots with thumbnail generation


📊 Professional Reporting
HTML Dashboard: Dark-themed, mobile-responsive interface
Interactive Gallery: Click-to-expand screenshot thumbnails
Organized Findings: Categorized by severity and module
Export Ready: All raw data preserved for further analysis
Progress Tracking: Real-time progress indicators during scans

⚙️ Technical Excellence
Parallel Processing: Multiple terminals for simultaneous execution
Graceful Error Handling: Failures don't break the entire scan
Resource Management: Rate limiting and timeout controls
Logging: Comprehensive logs for debugging and auditing
Configurable: Easy to customize scan parameters

📊 System Requirements
Minimum Requirements
OS: Kali Linux 2023+, Ubuntu 20.04+, Debian 11+
CPU: 2+ cores
RAM: 4GB minimum, 8GB recommended
Storage: 20GB free space
Network: Stable internet connection

Software Dependencies
```bash
# Core Requirements
Python 3.8+    # Included in most distributions
Go 1.19+       # Installed automatically
Git            # For cloning and updates
```
# System Packages (installed automatically)
nmap           # Port scanning
firefox-esr    # Screenshot rendering
xterm/gnome-terminal  # Terminal emulation
⚡ Quick Installation (2 Minutes)
# 1. Clone the repository
```bash
git clone https://github.com/your-repo/T-SLYTHERINS.git
cd T-SLYTHERINS
```
# 2. Run automated installation (requires sudo)
```bash
chmod +x installer.sh
sudo ./installer.sh
```
# 3. Setup Python virtual environment
```bash
./install_with_venv.sh
```
# 4. Verify installation
```bash
./run_recon.sh --test
```
🎯 Installation Verification
# Check all tools
```bash
./run_recon.sh --check
```
# Expected output:
✅ subfinder  v2.6.3
✅ amass      v4.0.0
✅ httpx      v1.3.5
✅ nuclei     v3.1.7
✅ katana     v1.0.3
✅ nmap       7.94
✅ Python     3.11.4
✅ All modules ready!
🔧 Detailed Installation
Option A: Complete Installation (Recommended)
bash
# Update system first
```bash
sudo apt update && sudo apt upgrade -y
```

# Install system dependencies
```bash
sudo apt install -y git python3 python3-pip python3-venv wget curl
```
# Clone repository
```bash
git clone https://github.com/your-repo/T-SLYTHERINS.git
cd T-SLYTHERINS
```
# Run installer (will install Go and all tools)
```bash
chmod +x installer.sh
sudo ./installer.sh
```
# Setup Python virtual environment (no sudo needed)
```bash
./install_with_venv.sh
```
# Logout and login to apply PATH changes
```bash
logout
```
# (Then log back in)
Option B: Manual Installation
# Install Go manually if needed
```bash
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc
```
# Install tools individually
```bash
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/owasp-amass/amass/v4/...@master
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/michenriksen/aquatone@latest
```
# Clone and setup T-SLYTHERINS
```bash
git clone https://github.com/your-repo/T-SLYTHERINS.git
cd T-SLYTHERINS
./install_with_venv.sh
```

🔍 Post-Installation Verification
```bash
# Activate virtual environment
source venv/bin/activate
```

# Test all imports
```bash
python3 -c "
import sys
sys.path.insert(0, 'modules')
from progress import Spinner
import utils
print('✅ All imports successful')
"
```
# Test tool availability
```bash
for tool in subfinder amass httpx nuclei katana nmap; do
    which $tool && echo "✅ $tool found" || echo "❌ $tool missing"
done
```
🎯 Usage Guide
Quick Start (Easiest Method)
```bash
# Just run this single command
./run_recon.sh
```
# Enter domain when prompted: example.com
# Watch the magic happen!
Standard Usage
```bash
# Method 1: Use helper script (auto-activates venv)
./run_recon.sh example.com
```
# Method 2: Manual execution
```bash
source venv/bin/activate
./recon_slytherins example.com
```
```bash
# Method 3: Quick activation
./activate_venv.sh
./recon_slytherins example.com
deactivate  # When done
Advanced Options
```
```bash
# Run specific modules only
source venv/bin/activate
python3 modules/subdomains.py example.com output_dir/
python3 modules/portscan.py example.com output_dir/
python3 modules/vulnscan.py example.com output_dir/
```
```bash
# Generate report from existing scan
python3 modules/report.py T-SLYTHERINS-OUTPUT-example.com
```
```bash
# Update vulnerability templates
nuclei -update-templates
```

##Scan Parameters
```bash
# Custom output directory
./recon_slytherins example.com --output custom_output/

# Limit scan time
./recon_slytherins example.com --timeout 3600  # 1 hour

# Verbose mode
./recon_slytherins example.com --verbose

# Check only (no scan)
./recon_slytherins --check

# Test on legal target
./recon_slytherins testphp.vulnweb.com
```

📁 Output Structure:
```bash
T-SLYTHERINS-OUTPUT-example.com/
├── 📊 REPORTING
│   ├── report.html              # Main HTML report (start here!)
│   └── scan_summary.txt         # Executive summary
│
├── 🔍 DISCOVERY
│   ├── all_subdomains.txt       # All discovered subdomains
│   ├── httpx_results.txt        # Live HTTP/HTTPS hosts
│   ├── httpx_summary.txt        # Status code analysis
│   └── subdomains.log           # Enumeration process log
│
├── 🌐 DNS
│   ├── records.txt              # Complete DNS records (A, AAAA, MX, NS, TXT)
│   ├── zone_attempt.txt         # Zone transfer test results
│   ├── misconfig.txt            # DNS misconfigurations found
│   └── dns.log                  # DNS scan log
│
├── 🚪 PORTS
│   ├── nmap.txt                 # Raw Nmap output
│   ├── nmap.xml                 # XML format (for parsing)
│   ├── port_summary.txt         # Formatted port summary
│   ├── services.csv             # CSV export of services
│   └── portscan.log             # Port scan log
│
├── 🛡️ VULNERABILITIES
│   ├── nuclei.json              # JSON formatted findings
│   ├── nuclei.log               # Raw scan output
│   ├── summary.txt              # Vulnerability summary by severity
│   ├── critical_findings.txt    # Critical vulnerabilities
│   └── vulnscan.log             # Vulnerability scan log
│
├── 🕷️ CRAWLING
│   ├── katana.txt               # All discovered URLs
│   ├── katana_summary.txt       # Crawl statistics
│   ├── parameters.txt           # Discovered parameters
│   ├── js_files.txt             # JavaScript files found
│   └── api_endpoints.txt        # API endpoints discovered
│
├── 📸 SCREENSHOTS
│   ├── aquatone_report.html     # Aquatone's original report
│   ├── gallery.html             # Interactive screenshot gallery
│   ├── screenshots/             # Full-size screenshots (PNG)
│   │   ├── https_example.com.png
│   │   └── http_subdomain.example.com.png
│   └── thumbs/                  # Thumbnail images (400x300)
│       ├── thumb_https_example.com.png
│       └── ...
│
└── 📋 LOGS
    ├── execution.log            # Main execution log
    ├── errors.log               # Error log
    └── timestamps.txt           # Module execution times
    ```
```
🛠️ Troubleshooting
Common Issues & Solutions
Issue 1: "ModuleNotFoundError: No module named 'progress'"
Solution:
```bash
# Ensure you're in the correct directory
cd T-SLYTHERINS
```
```bash
# Activate virtual environment
source venv/bin/activate
```
```bash
# Check module path
python3 -c "import sys; print(sys.path)"
```
Issue 2: Terminal windows not opening
Solution:
```bash
# Install a terminal emulator
sudo apt install xterm  # or gnome-terminal
```
```bash
# Check DISPLAY variable
echo $DISPLAY  # Should be :0 or similar
```
```bash
# Run in headless mode (no screenshots)
./recon_slytherins example.com --no-gui
```
Issue 3: Go tools not found
Solution:

```bash
# Source Go environment
source /etc/profile.d/golang.sh
```
```bash
# Add to .bashrc permanently
echo 'source /etc/profile.d/golang.sh' >> ~/.bashrc
source ~/.bashrc
```
```bash
# Check PATH
echo $PATH | grep go
```
Issue 4: Python package errors
Solution:
```bash
# Recreate virtual environment
rm -rf venv/
./install_with_venv.sh
```
```bash
# Check installation
source venv/bin/activate
pip list | grep -E "(pillow|requests|dnspython|nmap)"
```
Issue 5: Nmap requires root privileges
Solution:
```bash
# Option 1: Run with sudo
sudo python3 modules/portscan.py example.com output_dir/
```
```bash
# Option 2: Grant Nmap capabilities
sudo setcap cap_net_raw,cap_net_admin+eip $(which nmap)
```
# Option 3: Adjust scan parameters (remove -sV)
Issue 6: Screenshots fail
Solution:
```bash
# Install Firefox
sudo apt install firefox-esr
```
```bash
# For headless systems
sudo apt install xvfb
xvfb-run ./recon_slytherins example.com
```
```bash
# Disable screenshots
./recon_slytherins example.com --no-screenshots
```
Debug Mode
```bash
# Enable verbose output
./recon_slytherins example.com --verbose
```
```bash
# Check individual logs
tail -f T-SLYTHERINS-OUTPUT-example.com/*.log
```
```bash
# Test module individually
source venv/bin/activate
python3 -v modules/subdomains.py example.com test_output/
```
Performance Tuning
```bash
# Adjust based on system resources
export NUCLEI_RATE_LIMIT=30      # Lower for slow connections
export NUCLEI_CONCURRENCY=5      # Lower for low RAM
export NMAP_TIMING=3             # T3 for faster scans (T4 aggressive)
```
⚖️ Legal & Ethics
⚠️ IMPORTANT LEGAL NOTICE
T-SLYTHERINS is designed for legal security testing only.

✅ Authorized Use Cases
Testing your own systems
Authorized penetration testing engagements
Bug bounty programs with explicit permission
Educational environments
Security research with proper authorization

❌ Prohibited Activities
Unauthorized scanning of systems
Network reconnaissance without permission
Violating terms of service

Any illegal activities

Legal Compliance
By using this tool, you agree to:
Obtain proper authorization before scanning
Comply with all applicable laws and regulations
Respect privacy and data protection laws
Use the tool responsibly and ethically

Disclaimer
The authors and contributors:
Are not responsible for misuse
Provide no warranty for the tool
Assume no liability for damages
Recommend professional training before use

🤝 Contributing
We welcome contributions! Here's how:
Reporting Issues
Check existing issues on GitHub
Create detailed bug report with:
Error messages
Steps to reproduce
Environment details
Log files
Feature Requests
Open a feature request issue
Describe use case and expected behavior
Provide examples if possible

Code Contributions
```bash
# Fork repository
git clone https://github.com/your-fork/T-SLYTHERINS.git
```
```bash
# Create feature branch
git checkout -b feature/amazing-feature
```

# Make changes and test
# Submit pull request with description
Development Setup
```bash
# Setup development environment
python3 -m venv dev_venv
source dev_venv/bin/activate
pip install -r requirements-dev.txt
```
```bash
# Run tests
python3 -m pytest tests/
```

📞 Support
Resources
Documentation: This README and code comments
Issues: GitHub Issues page
Contact: pr0fessor_snape@t-slytheris.site
