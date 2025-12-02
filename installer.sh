#!/bin/bash

# T-SLYTHERINS Installer Script (Fixed Version)
# Fixes: Better error handling, path management, dependency checks

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           T-SLYTHERINS Installer       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[!] This script must be run as root (use sudo)${NC}" 
   exit 1
fi

# Detect the actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

echo -e "${YELLOW}[*] Installing for user: $ACTUAL_USER${NC}"
echo -e "${YELLOW}[*] Home directory: $ACTUAL_HOME${NC}"

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install package
install_package() {
    local package=$1
    if ! dpkg -l | grep -q "^ii  $package"; then
        echo -e "${YELLOW}[*] Installing $package...${NC}"
        apt-get install -y "$package" || {
            echo -e "${RED}[!] Failed to install $package${NC}"
            return 1
        }
    else
        echo -e "${GREEN}[✓] $package already installed${NC}"
    fi
}

# Update package list
echo -e "${YELLOW}[*] Updating package lists...${NC}"
apt-get update -qq

# Install system dependencies
echo -e "${YELLOW}[*] Installing system dependencies...${NC}"
SYSTEM_DEPS=(
    "wget"
    "curl"
    "git"
    "python3"
    "python3-pip"
    "nmap"
    "firefox-esr"
    "xterm"
)

# Try gnome-terminal separately (can fail)
OPTIONAL_DEPS=(
    "gnome-terminal"
    "chromium"
)

for dep in "${SYSTEM_DEPS[@]}"; do
    install_package "$dep"
done

# Install optional packages (don't fail if they error)
for dep in "${OPTIONAL_DEPS[@]}"; do
    echo -e "${YELLOW}[*] Trying to install $dep...${NC}"
    apt-get install -y "$dep" 2>/dev/null || echo -e "${YELLOW}[!] $dep not available, skipping${NC}"
done

# Install Go
echo -e "${YELLOW}[*] Checking Go installation...${NC}"
if ! command_exists go; then
    echo -e "${YELLOW}[*] Installing Go...${NC}"
    GO_VERSION="1.21.5"
    wget -q "https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz" -O /tmp/go.tar.gz
    rm -rf /usr/local/go
    tar -C /usr/local -xzf /tmp/go.tar.gz
    rm /tmp/go.tar.gz
    
    # Set up Go environment for all users
    cat > /etc/profile.d/golang.sh <<EOF
export GOROOT=/usr/local/go
export GOPATH=\$HOME/go
export PATH=\$PATH:\$GOROOT/bin:\$GOPATH/bin
EOF
    chmod +x /etc/profile.d/golang.sh
    
    # Also set for current session
    export GOROOT=/usr/local/go
    export GOPATH="$ACTUAL_HOME/go"
    export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
    
    echo -e "${GREEN}[✓] Go installed successfully${NC}"
else
    echo -e "${GREEN}[✓] Go already installed${NC}"
    # Ensure Go paths are set
    export GOROOT=/usr/local/go
    export GOPATH="$ACTUAL_HOME/go"
    export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
fi

# Create Go directories with proper permissions
mkdir -p "$GOPATH"/{bin,src,pkg}
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$GOPATH"

# Install Python dependencies
echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
echo -e "${BLUE}[*] Note: Python packages will be installed in virtual environment${NC}"
echo -e "${BLUE}[*] This is the recommended approach for Kali Linux 2024+${NC}"

# Try to install with --user flag first, if it fails, note it
su - "$ACTUAL_USER" -c "pip3 install --user --upgrade pillow requests python-nmap dnspython 2>/dev/null" || {
    echo -e "${YELLOW}[!] System Python is externally managed (this is normal)${NC}"
    echo -e "${YELLOW}[*] Python packages will be installed via virtual environment${NC}"
    echo -e "${YELLOW}[*] Run ./install_with_venv.sh after this completes${NC}"
}

# Install Go-based tools
echo -e "${YELLOW}[*] Installing reconnaissance tools...${NC}"

install_go_tool() {
    local tool_name=$1
    local tool_package=$2
    
    echo -e "${YELLOW}[*] Installing $tool_name...${NC}"
    su - "$ACTUAL_USER" -c "source /etc/profile.d/golang.sh && go install $tool_package" || {
        echo -e "${RED}[!] Failed to install $tool_name${NC}"
        return 1
    }
    echo -e "${GREEN}[✓] $tool_name installed${NC}"
}

# Install tools as the actual user
install_go_tool "subfinder" "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
install_go_tool "amass" "github.com/owasp-amass/amass/v4/...@master"
install_go_tool "assetfinder" "github.com/tomnomnom/assetfinder@latest"
install_go_tool "httpx" "github.com/projectdiscovery/httpx/cmd/httpx@latest"
install_go_tool "katana" "github.com/projectdiscovery/katana/cmd/katana@latest"
install_go_tool "nuclei" "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
# Install aquatone (use binary if go install fails)
echo -e "${YELLOW}[*] Installing aquatone...${NC}"
if ! su - "$ACTUAL_USER" -c "source /etc/profile.d/golang.sh && go install github.com/michenriksen/aquatone@latest" 2>/dev/null; then
    echo -e "${YELLOW}[!] Go install failed, trying binary download...${NC}"
    
    # Download pre-built binary
    AQUATONE_VERSION="1.7.0"
    TEMP_DIR=$(mktemp -d)
    
    if wget -q "https://github.com/michenriksen/aquatone/releases/download/v${AQUATONE_VERSION}/aquatone_linux_amd64_${AQUATONE_VERSION}.zip" -O "$TEMP_DIR/aquatone.zip"; then
        cd "$TEMP_DIR"
        unzip -q aquatone.zip 2>/dev/null
        mkdir -p "$ACTUAL_HOME/go/bin"
        cp aquatone "$ACTUAL_HOME/go/bin/"
        chmod +x "$ACTUAL_HOME/go/bin/aquatone"
        chown "$ACTUAL_USER:$ACTUAL_USER" "$ACTUAL_HOME/go/bin/aquatone"
        cd - > /dev/null
        rm -rf "$TEMP_DIR"
        echo -e "${GREEN}[✓] aquatone installed from binary${NC}"
    else
        echo -e "${YELLOW}[!] aquatone installation failed (optional tool)${NC}"
    fi
else
    echo -e "${GREEN}[✓] aquatone installed${NC}"
fi

# Update nuclei templates
echo -e "${YELLOW}[*] Updating nuclei templates...${NC}"
su - "$ACTUAL_USER" -c "source /etc/profile.d/golang.sh && nuclei -update-templates" 2>/dev/null || true

# Make main script executable
if [ -f "./recon_slytherins" ]; then
    chmod +x ./recon_slytherins
    chown "$ACTUAL_USER:$ACTUAL_USER" ./recon_slytherins
    echo -e "${GREEN}[✓] Main script made executable${NC}"
fi

# Create modules directory if it doesn't exist
mkdir -p ./modules
chown -R "$ACTUAL_USER:$ACTUAL_USER" ./modules

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Installation Complete!        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}[*] Go tools installed successfully${NC}"
echo ""
echo -e "${YELLOW}[*] IMPORTANT - Next Steps:${NC}"
echo -e "    1. Run: ${GREEN}source /etc/profile.d/golang.sh${NC}"
echo -e "    2. Setup Python venv: ${GREEN}./install_with_venv.sh${NC}"
echo -e "    3. Verify: ${GREEN}subfinder -version${NC}"
echo -e "    4. Execute: ${GREEN}./run_recon.sh${NC}"
echo ""
echo -e "${BLUE}[*] Why venv? Kali Linux 2024+ requires virtual environments${NC}"
echo -e "${BLUE}[*] This keeps your system Python clean and safe${NC}"
echo ""
echo -e "${YELLOW}[*] Note: Logout and login again for PATH changes to take effect${NC}"
