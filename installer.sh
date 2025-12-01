#!/bin/bash

# T-SLYTHERINS Installer Script
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
    "chromium"
    "xterm"
    "gnome-terminal"
)

for dep in "${SYSTEM_DEPS[@]}"; do
    install_package "$dep"
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
su - "$ACTUAL_USER" -c "pip3 install --user --upgrade pillow requests python-nmap dnspython" || {
    echo -e "${RED}[!] Failed to install Python dependencies${NC}"
    exit 1
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
install_go_tool "aquatone" "github.com/michenriksen/aquatone@latest"

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
echo -e "${GREEN}║         Installation Complete!         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}[*] Next steps:${NC}"
echo -e "    1. Run: ${GREEN}source /etc/profile.d/golang.sh${NC}"
echo -e "    2. Verify: ${GREEN}subfinder -version${NC}"
echo -e "    3. Execute: ${GREEN}./recon_slytherins${NC}"
echo ""
echo -e "${YELLOW}[*] Note: Logout and login again for PATH changes to take effect${NC}"
