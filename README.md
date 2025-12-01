T‑SLYTHERINS Recon Suite
Advanced Automated Reconnaissance Framework for Penetration Testers & Security Researchers
##
📌 Overview

T‑SLYTHERINS is a professional‑grade reconnaissance framework that automates every major phase of initial information gathering during penetration testing.
It integrates multiple industry‑standard tools, executes them in separate terminal windows, captures website screenshots using Firefox GUI mode, generates thumbnails, and compiles a full HTML report containing:

Subdomains
DNS data
Port scan results
HTTP probe results
Vulnerability scan results
Screenshot gallery
Crawl results (Katana)
It also includes:
A live progress spinner
A separate terminal showing a snake animation
A clean modular architecture
A single installer script

⚠️ LEGAL DISCLAIMER
You must have explicit permission to scan any system.
Unauthorized scanning is illegal.
This tool is for ethical hacking, training, and research only.

🧭 Table of Contents

Features
Architecture
Requirements
Installation (Step‑by‑Step)
Manual Dependency Installation (Optional)
Running the Tool
How Each Module Works
Output Directory Structure
HTML Report Details
Troubleshooting Guide
Extending the Framework
Legal & Ethical Use
Contact / Support

⭐ Features:

✔ Full Recon Workflow Automation
Runs all recon phases in parallel:
Category	Tools
Subdomain Enumeration	amass, subfinder, assetfinder
DNS Recon	dig, host
Port Scanning	nmap
HTTP Probing	httpx
Web Crawling	katana
Vulnerability Testing	nuclei
Screenshots	aquatone + Firefox GUI
Reporting	HTML generation

✔ Multi‑Terminal Execution
Each module launches in a separate terminal window (xfce4-terminal recommended):
Subdomain terminal
DNS terminal
Port scan terminal
Vulnerability scan terminal
Screenshot terminal
Crawl terminal
Snake animation terminal

✔ Screenshot + Thumbnail System
Full‑page screenshots using Firefox GUI
Thumbnails generated locally
No cloud upload
Report auto‑embeds thumbnails

✔ Professional Report
An auto‑generated report.html containing:
Subdomain list
HTTP info
Ports & services
DNS info
Vulnerability findings
Katana crawl output
Full screenshot gallery

✔ Progress Visualization

Main terminal displays:
Animated spinner
Status of each module
Time elapsed

```bash
🏗 Architecture
T-SLYTHERINS/
├── installer.sh
├── recon_slytherins
├── modules/
│   ├── subdomains.py
│   ├── dnsscan.py
│   ├── portscan.py
│   ├── vulnscan.py
│   ├── screenshots.py
│   ├── report.py
│   ├── progress.py
│   ├── snake.py
│   └── utils.py
└── README.md
```

Modular by design — each module is independent.

🧰 Requirements
Operating System

✔ Kali Linux
✔ Parrot OS
✔ Ubuntu / Debian (with Firefox + X11 installed)

Core Tools (installer installs automatically)
Go (latest)
Python 3.8+
amass
subfinder
assetfinder
httpx
katana
nuclei
nmap
aquatone
firefox

📥 Installation (Step-by-Step)
```bash
1. Make the installer executable
chmod +x installer.sh
```
##
```bash
2. Run the installer
sudo ./installer.sh
```

Installer does:

✔ Installs Go
✔ Installs all Go‑based recon tools
✔ Installs Python dependencies
✔ Installs aquatone
✔ Ensures Firefox is installed
✔ Creates system PATH configs
✔ Verifies all tools exist

3. Activate Go path
```bash
source /etc/profile.d/golang.sh
```

5. Verify installation
```bash
subfinder -h
amass -h
httpx -h
``` 

If all work: Installation successful.

▶️ Running the Tool
```bash
#Run the main script:
./recon_slytherins
```

You will be prompted for a domain:

Enter target domain: example.com


The suite launches:
Multiple terminals
Snake animation terminal
Screenshot module
Progress spinner
HTML report builder
Everything runs automatically.

🔍 How Each Module Works
1️⃣ Subdomain Enumeration (subdomains.py)

Sources used:
amass (passive)
subfinder
assetfinder

Output:
```bash
T-SLYTHERINS-OUTPUT/all_subdomains.txt
```

2️⃣ DNS Recon (dnsscan.py)
Collects:
A / AAAA
CNAME
MX
TXT
NS

Also performs:
Zone transfer test
Misconfiguration checks

3️⃣ Port Scanning (portscan.py)
Runs:
```bash
nmap -sV -T4 -p- --open
```

Parses:
Open ports
Services
Versions

4️⃣ Vulnerability Scanning (vulnscan.py)

Runs nuclei with:
default templates
technologies detected by httpx

Output:
```bash
T-SLYTHERINS-OUTPUT/nuclei.log
```

5️⃣ Screenshot Module (screenshots.py)
Uses:
Aquatone
Firefox GUI mode (Mode A)

Outputs:
```bash
T-SLYTHERINS-OUTPUT/aquatone/screenshots/
T-SLYTHERINS-OUTPUT/aquatone/thumbs/
```

Thumbnails are locally stored.
6️⃣ Crawl Module (katana.py)
Discovers:
Endpoints
Parameters
Hidden paths

7️⃣ HTML Reporting (report.py)

Generates:
```bash
T-SLYTHERINS-OUTPUT/report.html
```

Contains:

✔ Subdomains
✔ Ports
✔ DNS
✔ Vulnerabilities
✔ Screenshots
✔ Crawled URLs

📂 Output Directory Structure
```bash
T-SLYTHERINS-OUTPUT/
├── all_subdomains.txt
├── dns/
│   ├── records.txt
│   ├── zone_attempt.txt
│   └── misconfig.txt
├── ports/
│   ├── nmap.txt
│   └── nmap.xml
├── nuclei/
│   └── nuclei.log
├── aquatone/
│   ├── screenshots/
│   └── thumbs/
├── katana.txt
└── report.html
```

🖥 HTML Report Details
Includes:
Clean UX layout
Embedded screenshot thumbnails
Click to open full images
Port scan summary
Vulnerabilities sorted by severity
Subdomains linked with http/https
DNS section
Crawl findings

Suitable for:
Client reports
Internal documentation
Pentest evidence

🩺 Troubleshooting Guide
❗ Firefox not opening / screenshots fail
Install Firefox manually:
```bash
sudo apt install firefox-esr
```
❗ aquatone: command not found
Reinstall:
```bash
go install github.com/michenriksen/aquatone@latest
```
❗ xfce4-terminal not found
Install:
```bash
sudo apt install xfce4-terminal
```
❗ No recon terminals opening
Run:
```bash
echo $DISPLAY
```
If empty, you're in a non‑GUI environment.
❗ Python modules missing
Run:
```bash
pip3 install pillow requests
```

⚖️ Legal & Ethical Use

This tool must only be used on
Systems you own
Systems you administer
Systems where you have explicit written permission
Any other usage violates:
Computer Misuse Laws
CFAA
GDPR
Security Professional Ethics

📬 Contact / Support
For improvements, bug fixes, or professional‑grade enhancements, open an issue or contact the maintainer.
