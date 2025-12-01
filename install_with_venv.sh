#!/bin/bash

# T-SLYTHERINS Virtual Environment Installer
# This script installs all dependencies in a Python virtual environment
# Safer and cleaner than system-wide installation

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

VENV_DIR="venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   T-SLYTHERINS Virtual Environment Installer          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}[!] Do NOT run this script as root/sudo${NC}"
   echo -e "${YELLOW}[*] Run as normal user: ./install_with_venv.sh${NC}"
   exit 1
fi

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo -e "${YELLOW}[*] Step 1: Checking system requirements...${NC}"

# Check for Python 3
if ! command_exists python3; then
    echo -e "${RED}[!] Python 3 is not installed${NC}"
    echo -e "${YELLOW}[*] Install with: sudo apt install python3${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}[✓] Python $PYTHON_VERSION found${NC}"

# Check for pip
if ! command_exists pip3; then
    echo -e "${YELLOW}[*] pip3 not found, installing...${NC}"
    if command_exists apt; then
        sudo apt update
        sudo apt install -y python3-pip
    else
        echo -e "${RED}[!] Please install python3-pip manually${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}[✓] pip3 found${NC}"

# Check for venv module
echo -e "${YELLOW}[*] Checking python3-venv...${NC}"
if ! python3 -c "import venv" 2>/dev/null; then
    echo -e "${YELLOW}[*] python3-venv not found, installing...${NC}"
    if command_exists apt; then
        sudo apt install -y python3-venv
    else
        echo -e "${RED}[!] Please install python3-venv manually${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}[✓] python3-venv available${NC}"
echo ""

# Create virtual environment
echo -e "${YELLOW}[*] Step 2: Creating virtual environment...${NC}"

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[!] Virtual environment already exists${NC}"
    read -p "$(echo -e ${YELLOW}Delete and recreate? [y/N]: ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}[*] Removing old virtual environment...${NC}"
        rm -rf "$VENV_DIR"
    else
        echo -e "${BLUE}[*] Using existing virtual environment${NC}"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}[✓] Virtual environment created: $VENV_DIR${NC}"
else
    echo -e "${GREEN}[✓] Using existing virtual environment${NC}"
fi

echo ""

# Activate virtual environment
echo -e "${YELLOW}[*] Step 3: Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}[✓] Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo -e "${YELLOW}[*] Step 4: Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}[✓] pip upgraded${NC}"
echo ""

# Install Python dependencies
echo -e "${YELLOW}[*] Step 5: Installing Python dependencies...${NC}"

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}[*] Creating requirements.txt...${NC}"
    cat > requirements.txt << 'EOF'
# Core dependencies
pillow>=9.0.0
requests>=2.28.0
dnspython>=2.2.0
python-nmap>=0.7.1

# Optional but recommended
colorama>=0.4.6
tqdm>=4.65.0
EOF
fi

echo -e "${BLUE}[*] Installing packages from requirements.txt...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}[✓] Python dependencies installed${NC}"
echo ""

# Check if Go tools need to be installed
echo -e "${YELLOW}[*] Step 6: Checking Go-based tools...${NC}"

GO_TOOLS=(
    "amass:github.com/owasp-amass/amass/v4/...@master"
    "subfinder:github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    "assetfinder:github.com/tomnomnom/assetfinder@latest"
    "httpx:github.com/projectdiscovery/httpx/cmd/httpx@latest"
    "katana:github.com/projectdiscovery/katana/cmd/katana@latest"
    "nuclei:github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
    "aquatone:github.com/michenriksen/aquatone@latest"
)

MISSING_GO_TOOLS=()

for tool_info in "${GO_TOOLS[@]}"; do
    tool_name=$(echo "$tool_info" | cut -d: -f1)
    if ! command_exists "$tool_name"; then
        MISSING_GO_TOOLS+=("$tool_name")
    else
        echo -e "${GREEN}[✓] $tool_name found${NC}"
    fi
done

if [ ${#MISSING_GO_TOOLS[@]} -gt 0 ]; then
    echo -e "${YELLOW}[!] Missing Go tools: ${MISSING_GO_TOOLS[*]}${NC}"
    echo -e "${YELLOW}[*] These tools require Go and must be installed separately${NC}"
    echo -e "${YELLOW}[*] Run the main installer.sh with sudo to install Go tools${NC}"
    echo ""
    read -p "$(echo -e ${YELLOW}Continue anyway? [y/N]: ${NC})" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        deactivate
        exit 0
    fi
fi

echo ""

# Check system dependencies
echo -e "${YELLOW}[*] Step 7: Checking system dependencies...${NC}"

SYSTEM_DEPS=("nmap" "firefox" "git")
MISSING_DEPS=()

for dep in "${SYSTEM_DEPS[@]}"; do
    if ! command_exists "$dep"; then
        MISSING_DEPS+=("$dep")
    else
        echo -e "${GREEN}[✓] $dep found${NC}"
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}[!] Missing system dependencies: ${MISSING_DEPS[*]}${NC}"
    echo -e "${YELLOW}[*] Install with: sudo apt install ${MISSING_DEPS[*]}${NC}"
fi

echo ""

# Create activation helper script
echo -e "${YELLOW}[*] Step 8: Creating helper scripts...${NC}"

cat > activate_venv.sh << 'EOFACTIVATE'
#!/bin/bash

# Quick activation script for T-SLYTHERINS virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found!"
    echo "Run ./install_with_venv.sh first"
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "✓ Virtual environment activated"
echo "✓ Python: $(which python3)"
echo "✓ Pip: $(which pip)"
echo ""
echo "To deactivate, run: deactivate"
echo "To run reconnaissance: ./recon_slytherins"
EOFACTIVATE

chmod +x activate_venv.sh

cat > run_recon.sh << 'EOFRUN'
#!/bin/bash

# Convenience script to run reconnaissance with venv activated

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found!"
    echo "Run ./install_with_venv.sh first"
    exit 1
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Run main script
python3 "$SCRIPT_DIR/recon_slytherins" "$@"

# Deactivate on exit
deactivate
EOFRUN

chmod +x run_recon.sh

echo -e "${GREEN}[✓] Helper scripts created:${NC}"
echo -e "    ${BLUE}activate_venv.sh${NC} - Activate virtual environment"
echo -e "    ${BLUE}run_recon.sh${NC} - Run reconnaissance with venv"
echo ""

# Create .gitignore
cat > .gitignore << 'EOFGITIGNORE'
# Virtual environment
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Output directories
T-SLYTHERINS-OUTPUT*/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOFGITIGNORE

echo -e "${GREEN}[✓] .gitignore created${NC}"
echo ""

# Test imports
echo -e "${YELLOW}[*] Step 9: Testing Python imports...${NC}"

python3 << 'EOFTEST'
import sys

try:
    import PIL
    print("[✓] PIL/Pillow imported successfully")
except ImportError as e:
    print(f"[!] Error importing PIL: {e}")
    sys.exit(1)

try:
    import requests
    print("[✓] requests imported successfully")
except ImportError as e:
    print(f"[!] Error importing requests: {e}")
    sys.exit(1)

try:
    import dns.resolver
    print("[✓] dnspython imported successfully")
except ImportError as e:
    print(f"[!] Error importing dnspython: {e}")
    sys.exit(1)

try:
    import nmap
    print("[✓] python-nmap imported successfully")
except ImportError as e:
    print(f"[!] Error importing python-nmap: {e}")
    sys.exit(1)

print("\n[✓] All Python dependencies working correctly!")
EOFTEST

echo ""

# Display summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Installation Complete!                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Virtual Environment Setup:${NC}"
echo -e "  Location: ${BLUE}$SCRIPT_DIR/$VENV_DIR${NC}"
echo -e "  Python: ${BLUE}$(python3 --version)${NC}"
echo ""
echo -e "${CYAN}Usage Options:${NC}"
echo ""
echo -e "${YELLOW}Option 1 - Manual activation:${NC}"
echo -e "  ${BLUE}source venv/bin/activate${NC}"
echo -e "  ${BLUE}./recon_slytherins${NC}"
echo -e "  ${BLUE}deactivate${NC}"
echo ""
echo -e "${YELLOW}Option 2 - Use helper scripts:${NC}"
echo -e "  ${BLUE}./activate_venv.sh${NC}    # Activate environment"
echo -e "  ${BLUE}./run_recon.sh${NC}        # Run with auto-activation"
echo ""
echo -e "${YELLOW}Option 3 - Direct execution:${NC}"
echo -e "  ${BLUE}venv/bin/python3 recon_slytherins${NC}"
echo ""

if [ ${#MISSING_GO_TOOLS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Next Steps:${NC}"
    echo -e "  ${RED}Missing Go tools: ${MISSING_GO_TOOLS[*]}${NC}"
    echo -e "  ${YELLOW}Run: sudo ./installer.sh${NC}"
    echo ""
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  System Dependencies:${NC}"
    echo -e "  ${RED}Missing: ${MISSING_DEPS[*]}${NC}"
    echo -e "  ${YELLOW}Install: sudo apt install ${MISSING_DEPS[*]}${NC}"
    echo ""
fi

echo -e "${CYAN}To verify installation:${NC}"
echo -e "  ${BLUE}source venv/bin/activate${NC}"
echo -e "  ${BLUE}python3 -c 'import PIL, requests, dns.resolver, nmap; print(\"OK\")'${NC}"
echo ""
echo -e "${GREEN}Happy Hacking! 🐍${NC}"
echo ""

# Keep venv activated for user
echo -e "${BLUE}[*] Virtual environment is still activated${NC}"
echo -e "${YELLOW}[*] Run 'deactivate' when done or close this terminal${NC}"
