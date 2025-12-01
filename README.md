T-SLYTHERINS Reconnaissance Suite (Fixed Edition)
Show Image
Show Image
Show Image
Advanced Automated Reconnaissance Framework for Penetration Testers & Security Researchers

📑 Table of Contents

Overview
Features
System Requirements
Installation Guide

Method 1: Standard Installation
Method 2: Virtual Environment (Recommended)


Usage Guide
Output Structure
Module Details
Troubleshooting
FAQ
Legal Notice
Contributing


🎯 Overview
T-SLYTHERINS is a professional-grade reconnaissance framework that automates the entire information gathering phase during penetration testing. It integrates multiple industry-standard tools, executes them in parallel, captures screenshots, and generates comprehensive HTML reports.
What makes this "Fixed Edition" special?

✅ Improved error handling and stability
✅ Virtual environment support
✅ Better terminal detection and compatibility
✅ Enhanced process management
✅ Comprehensive logging and reporting
✅ Works on more Linux distributions


⭐ Features
🔍 Comprehensive Reconnaissance

Subdomain Enumeration: Amass, Subfinder, Assetfinder
DNS Reconnaissance: Full DNS record scanning, zone transfer tests, misconfiguration detection
Port Scanning: Nmap with service detection and version identification
HTTP Probing: Live host detection with httpx
Vulnerability Scanning: Nuclei with rate limiting and template updates
Web Crawling: Katana for endpoint discovery
Screenshot Capture: Aquatone with thumbnail generation

🎨 Professional Reporting

Beautiful HTML reports with dark theme
Screenshot gallery with thumbnails
Organized by severity and category
Click-to-expand functionality
Mobile-responsive design

🚀 Technical Excellence

Multi-terminal parallel execution
Graceful error handling
Process cleanup and management
Virtual environment support
Progress indicators
Comprehensive logging


💻 System Requirements
Operating Systems

✅ Kali Linux (2023.1+)
✅ Parrot OS (5.0+)
✅ Ubuntu (20.04+)
✅ Debian (11+)
✅ Any Linux with X11/GUI support

Hardware Requirements

Minimum: 4GB RAM, 20GB free disk space
Recommended: 8GB RAM, 50GB free disk space
Network: Stable internet connection

Software Requirements

Python 3.8 or higher
Go 1.19 or higher (installed automatically)
Root/sudo access (for installation only)


📦 Installation Guide
Pre-Installation Steps
1. Update your system:
```bash
bashsudo apt update && sudo apt upgrade -y
```

Install basic dependencies:
```bash
sudo apt install -y wget curl git python3 python3-pip python3-venv
```
Download T-SLYTHERINS:
```bash
git clone https://github.com/your-repo/T-Slytherins-Fixed.git
cd T-Slytherins-Fixed
```

Method 1: Standard Installation
Best for: Users who want everything installed system-wide
Step 1: Run the main installer (requires sudo)
```bash
chmod +x installer.sh
sudo ./installer.sh
```

This will install:

Go programming language
All Go-based reconnaissance tools
System dependencies (nmap, firefox, etc.)
Python packages system-wide

Step 2: Activate Go environment
```bash
bashsource /etc/profile.d/golang.sh
```

Step 3: Verify installation
```bash
subfinder -version
amass -version
httpx -version
nuclei -version
```

Step 4: Logout and login (to apply PATH changes permanently)
```bash
logout
```

# Then log back in

Method 2: Virtual Environment (Recommended)
Best for: Cleaner installation, isolated Python environment, easier management
Step 1: Install Go tools (one-time, requires sudo)
```bash
bashchmod +x installer.sh
sudo ./installer.sh
```
Step 2: Setup virtual environment (no sudo needed)
```bash
chmod +x install_with_venv.sh
./install_with_venv.sh
```
This creates an isolated Python environment with all dependencies.
Step 3: Verify installation
bash# Activate virtual environment
```bash
source venv/bin/activate
```

# Test Python imports
```bash
python3 -c "import PIL, requests, dns.resolver, nmap; print('✓ All imports OK')"
```

# Test Go tools
```bash
subfinder -version
nuclei -version
Step 4: You're ready to go!
```

🚀 Usage Guide
Quick Start
Option A: Using Virtual Environment (if installed)
Method 1 - Using helper script (easiest):
```bash
bash./run_recon.sh
```
Just run and enter your target domain. Everything else is automatic!
Method 2 - Manual activation:
bash# Activate virtual environment
```bash
source venv/bin/activate
```

# Run reconnaissance
```bash
./recon_slytherins
```

# When done
deactivate
Method 3 - Quick activation helper:
bash# Activate and stay in venv
./activate_venv.sh

# Now run any commands
./recon_slytherins
python3 modules/report.py <output_dir>

# Deactivate when done
deactivate
Option B: Standard Installation
bash./recon_slytherins

Detailed Usage Steps
Step 1: Launch the reconnaissance suite
bash./recon_slytherins
Step 2: Enter target domain when prompted
[?] Enter target domain: example.com
Important: Enter only the domain name, no protocol (http/https)
Step 3: Monitor progress
The script will:

Create output directory: T-SLYTHERINS-OUTPUT-example.com/
Launch multiple terminal windows (one for each module)
Display progress spinner in main terminal
Log everything to separate files

Terminal windows opened:

Subdomain Enumeration
DNS Reconnaissance
Port Scanning
Vulnerability Scanning
Screenshot Capture

Step 4: Wait for completion

Subdomain enumeration: ~5-10 minutes
DNS scanning: ~2-5 minutes
Port scanning: ~15-30 minutes
Vulnerability scanning: ~20-40 minutes
Screenshots: ~10-20 minutes

Total time: 1-2 hours depending on target size
Step 5: Generate HTML report
bash# If using venv, activate first
```bash
source venv/bin/activate
```

# Generate report
python3 modules/report.py T-SLYTHERINS-OUTPUT-example.com
Step 6: View results
bash# Open report in browser
firefox T-SLYTHERINS-OUTPUT-example.com/report.html

# Or use your preferred browser
google-chrome T-SLYTHERINS-OUTPUT-example.com/report.html

Advanced Usage
Run specific modules only
Subdomain enumeration only:
```bash
bashsource venv/bin/activate  # if using venv
python3 modules/subdomains.py example.com T-SLYTHERINS-OUTPUT-example.com
DNS scan only:
bashpython3 modules/dnsscan.py example.com T-SLYTHERINS-OUTPUT-example.com
Port scan only:
bashpython3 modules/portscan.py example.com T-SLYTHERINS-OUTPUT-example.com
Vulnerability scan only:
bashpython3 modules/vulnscan.py example.com T-SLYTHERINS-OUTPUT-example.com
Screenshots only:
bashpython3 modules/screenshots.py example.com T-SLYTHERINS-OUTPUT-example.com
```

Customize scans
Edit module files to customize:

modules/subdomains.py - Add/remove subdomain tools
modules/portscan.py - Change nmap parameters
modules/vulnscan.py - Modify nuclei templates
modules/screenshots.py - Adjust screenshot settings

```bash
📁 Output Structure
After a scan, your output directory will look like this:
T-SLYTHERINS-OUTPUT-example.com/
├── all_subdomains.txt          # All discovered subdomains
├── httpx_results.txt           # Live HTTP/HTTPS hosts
├── subdomains.log              # Subdomain module log
├── dns.log                     # DNS module log
├── portscan.log                # Port scan module log
├── vulnscan.log                # Vulnerability scan log
├── screenshots.log             # Screenshot module log
│
├── dns/                        # DNS reconnaissance results
│   ├── records.txt             # All DNS records
│   ├── zone_attempt.txt        # Zone transfer test results
│   └── misconfig.txt           # Misconfiguration checks
│
├── ports/                      # Port scan results
│   ├── nmap.txt                # Raw nmap output
│   ├── nmap.xml                # XML format
│   ├── nmap.gnmap              # Grepable format
│   └── port_summary.txt        # Formatted summary
│
├── nuclei/                     # Vulnerability scan results
│   ├── nuclei.log              # Raw nuclei output
│   ├── nuclei.json             # JSON format
│   └── summary.txt             # Vulnerability summary
│
├── aquatone/                   # Screenshot results
│   ├── screenshots/            # Full-size screenshots
│   │   ├── http__example.com.png
│   │   └── ...
│   ├── thumbs/                 # Thumbnail images
│   │   ├── thumb_http__example.com.png
│   │   └── ...
│   ├── gallery.html            # Screenshot gallery
│   └── aquatone_report.html    # Aquatone's report
│
└── report.html                 # 🎯 Main HTML report (start here!)
```


🔧 Module Details
1. Subdomain Enumeration Module
File: modules/subdomains.py
What it does:

Runs Amass in passive mode
Executes Subfinder with silent mode
Uses Assetfinder for additional discovery
Combines and deduplicates all results
Outputs to all_subdomains.txt

Typical output:
api.example.com
www.example.com
mail.example.com
dev.example.com
staging.example.com

2. DNS Reconnaissance Module
File: modules/dnsscan.py
What it does:

Queries all DNS record types (A, AAAA, CNAME, MX, NS, TXT, SOA)
Tests for zone transfers (AXFR)
Checks for wildcard DNS
Validates SPF and DMARC records
Identifies DNS misconfigurations

Key findings:

Mail server configurations
Name server details
Email security status
Potential DNS vulnerabilities


3. Port Scanning Module
File: modules/portscan.py
What it does:

Resolves domain to IP address
Scans top 1000 ports with nmap
Detects service versions
Identifies open services
Generates formatted summary

Output includes:

Open ports and protocols
Service names
Version information
Potential attack surfaces


4. Vulnerability Scanning Module
File: modules/vulnscan.py
What it does:

Updates nuclei templates
Runs httpx to find live hosts
Executes nuclei with rate limiting
Categorizes findings by severity
Generates JSON and text reports

Severity levels:

🔴 Critical
🟠 High
🟡 Medium
🔵 Low
⚪ Info


5. Screenshot Module
File: modules/screenshots.py
What it does:

Uses Aquatone to capture screenshots
Processes all live HTTP/HTTPS hosts
Generates thumbnail images
Creates browsable gallery
Organizes screenshots by host

Features:

Full-page screenshots
Automatic thumbnail generation
HTML gallery with click-to-expand
Organized file naming


6. Report Generation Module
File: modules/report.py
What it does:

Collects data from all modules
Generates beautiful HTML report
Embeds screenshots and findings
Organizes by category
Creates mobile-responsive layout

Report sections:

📊 Overview statistics
🌐 Discovered subdomains
🔍 DNS information
🔓 Port scan results
⚠️ Vulnerability findings
📸 Screenshot gallery
🕷️ Crawled URLs


🛠️ Troubleshooting
Common Issues and Solutions
Issue 1: "Command not found" errors for Go tools
Problem: Go tools not in PATH
Solution:
bash# Activate Go environment
```bash
source /etc/profile.d/golang.sh
```

# Verify PATH
```bash
echo $PATH | grep go
```

# If still not working, reinstall
```bash
sudo ./installer.sh
```

Issue 2: No terminal windows opening
Problem: Terminal emulator not detected
Solution:
bash# Check if DISPLAY is set
```bash
echo $DISPLAY
```

# Install a terminal emulator
```bash
sudo apt install gnome-terminal
```

# Or use xterm
```bash
sudo apt install xterm
```

# Modules will run in background if no terminal found

Issue 3: Python import errors
Problem: Missing Python packages
Solution:
bash# If using venv
```bash
source venv/bin/activate
pip install -r requirements.txt
```

# If system-wide
```bash
pip3 install pillow requests dnspython python-nmap
```

# Reinstall if needed
```bash
./install_with_venv.sh
```

Issue 4: "Permission denied" errors
Problem: Scripts not executable
Solution:
bash# Make all scripts executable
```bash
chmod +x installer.sh
chmod +x install_with_venv.sh
chmod +x recon_slytherins
chmod +x run_recon.sh
chmod +x activate_venv.sh
```

# Make modules executable
```bash
chmod +x modules/*.py
```

Issue 5: Nmap requires root
Problem: Some nmap scans need elevated privileges
Solution:
bash# Option 1: Run specific module with sudo
```bash
sudo python3 modules/portscan.py example.com output/
```

# Option 2: Give nmap capabilities (one-time)
```bash
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
```

Issue 6: Screenshots fail / Aquatone errors
Problem: Missing browser or display
Solution:
bash# Install Firefox
```bash
sudo apt install firefox-esr
```

# Check display
echo $DISPLAY  # Should show :0 or similar

# If headless, install Xvfb
```bash
sudo apt install xvfb
xvfb-run ./recon_slytherins
```

Issue 7: Virtual environment activation fails
Problem: venv module not installed
Solution:
bash# Install python3-venv
```bash
sudo apt install python3-venv
```

# Recreate virtual environment
```bash
rm -rf venv
./install_with_venv.sh
```

Issue 8: Nuclei templates outdated
Problem: Old vulnerability templates
Solution:
bash# Update templates manually
```bash
nuclei -update-templates
```

# Force update
```bash
nuclei -update-templates -force
```

Debug Mode
Enable verbose output for troubleshooting:
bash# Run with Python debug mode
```bash
python3 -v recon_slytherins
```

# Check individual module logs
```bash
tail -f T-SLYTHERINS-OUTPUT-example.com/subdomains.log
tail -f T-SLYTHERINS-OUTPUT-example.com/dns.log
tail -f T-SLYTHERINS-OUTPUT-example.com/vulnscan.log
```

❓ FAQ
Q1: How long does a full scan take?
A: Typically 1-2 hours depending on:

Number of subdomains found
Network speed
Target responsiveness
Number of vulnerabilities

Q2: Can I run this on a VPS/headless server?
A: Yes, but:

Screenshot module may fail without display
Use xvfb-run for headless mode
Modules will run in background if no terminal detected

Q3: Is this safe to use?
A: Yes, but:

Only scan authorized targets
Use rate limiting (already configured)
Respect robots.txt
Get written permission first

Q4: Can I customize the scans?
A: Absolutely! Edit the module files:

Add/remove tools
Change parameters
Modify templates
Adjust timeouts

Q5: What if a module crashes?
A: The system is resilient:

Other modules continue running
Logs are saved
Partial results are preserved
Report generates with available data

Q6: How do I uninstall?
A: Simple:
bash# Remove virtual environment
```bash
rm -rf venv
```

# Remove output directories
```bash
rm -rf T-SLYTHERINS-OUTPUT-*
```

# Uninstall Go tools (optional)
```bash
rm -rf ~/go/bin/{amass,subfinder,assetfinder,httpx,katana,nuclei,aquatone}
```

# Remove Go (optional)
```bash
sudo rm -rf /usr/local/go
sudo rm /etc/profile.d/golang.sh
```

Q7: Can I run multiple scans simultaneously?
A: Yes:

Each scan creates its own output directory
Use different terminal sessions
Or run in background: 
```bash
./recon_slytherins &
```

Q8: How do I update the tools?
A:
bash# Update Go tools
```bash
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
# ... repeat for other tools
```

# Update Python packages
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

```bash
# Update nuclei templates
nuclei -update-templates
```

⚖️ Legal Notice
⚠️ IMPORTANT - READ CAREFULLY
This tool is designed for LEGAL AND AUTHORIZED security testing only.
✅ Acceptable Use:

Testing systems you own
Testing with explicit written permission
Authorized penetration testing engagements
Educational purposes in controlled environments
Bug bounty programs with proper authorization

❌ Prohibited Use:

Scanning systems without permission
Unauthorized network reconnaissance
Violating terms of service
Accessing systems you don't own
Any illegal activity

Legal Implications:
Unauthorized use may violate:

Computer Fraud and Abuse Act (CFAA) - USA
Computer Misuse Act - UK
GDPR - European Union
Local cybercrime laws - Your jurisdiction

Penalties can include:

Criminal charges
Heavy fines
Imprisonment
Civil lawsuits
Professional consequences

Disclaimer:
The authors and contributors of T-SLYTHERINS:

Are NOT responsible for misuse
Do NOT encourage illegal activities
Provide this tool "AS IS" without warranty
Assume NO LIABILITY for your actions

By using this tool, you agree to:

Use it legally and ethically
Obtain proper authorization
Take full responsibility for your actions
Comply with all applicable laws


🤝 Contributing
We welcome contributions! Here's how:
Reporting Bugs

Check existing issues
Create detailed bug report
Include logs and error messages
Specify your environment

Suggesting Features

Open a feature request
Describe the use case
Explain expected behavior

Pull Requests

Fork the repository
Create a feature branch
Make your changes
Test thoroughly
Submit pull request with description


📧 Support

Issues: Open an issue on GitHub
Discussions: Use GitHub Discussions
Documentation: Check this README first
Updates: Watch the repository for updates


📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Tools Integrated:

Amass - OWASP Amass Project
Subfinder - ProjectDiscovery
Assetfinder - Tom Hudson
Httpx - ProjectDiscovery
Nuclei - ProjectDiscovery
Katana - ProjectDiscovery
Aquatone - Michael Henriksen
Nmap - Gordon Lyon

Special Thanks:
#-Raynox


🚀 Quick Reference Card
bash# INSTALLATION
```bash
sudo ./installer.sh                    # Install Go tools
./install_with_venv.sh                # Setup Python venv
```

# USAGE
```bash
./run_recon.sh                        # Easiest way (with venv)
./recon_slytherins                    # Standard way
```

# ACTIVATION (venv)
```bash
source venv/bin/activate              # Manual activation
./activate_venv.sh                    # Helper script
```

# REPORT GENERATION
```bash
python3 modules/report.py <output_dir>
```

# VERIFICATION
```bash
subfinder -version                     # Check Go tools
python3 -c "import PIL; print('OK')"  # Check Python
```

# TROUBLESHOOTING
```bash
source /etc/profile.d/golang.sh       # Fix PATH
tail -f output/subdomains.log         # Monitor progress
```

✅ Complete error handling overhaul
✅ Virtual environment support
✅ Better terminal detection
✅ Enhanced process management
✅ Improved documentation

v2.0 (Original)


<div align="center">
Made with ❤️ by the T-SLYTHERINS Team (Pr0Fessor_SnApe)
Happy Ethical Hacking! 🐍🔒
⬆ Back to Top
</div>
