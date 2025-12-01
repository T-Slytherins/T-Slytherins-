#!/bin/bash
set -euo pipefail

# T-SLYTHERINS Installer
# Installs apt deps, Go, Go tools used by the recon suite, and Python deps.

GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
RESET="\033[0m"

echo -e "${GREEN}T-SLYTHERINS Installer${RESET}"

echo -e "${GREEN}[+] Updating apt...${RESET}"
sudo apt update -y

echo -e "${GREEN}[+] Installing apt packages (may ask for sudo)...${RESET}"
sudo apt install -y wget curl git build-essential xfce4-terminal xterm \
    python3 python3-pip python3-venv nmap jq

# Install Go (latest stable) safely
echo -e "${GREEN}[+] Installing Go (latest)...${RESET}"
LATEST_GO=$(curl -s https://go.dev/VERSION?m=text | head -n1)
if [[ -z "$LATEST_GO" ]]; then
  echo -e "${RED}[✘] Could not detect go version${RESET}"
  exit 1
fi

GO_TAR="${LATEST_GO}.linux-amd64.tar.gz"
GO_URL="https://go.dev/dl/${GO_TAR}"

sudo rm -rf /usr/local/go
wget -q "$GO_URL" -O /tmp/go.tar.gz
sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm -f /tmp/go.tar.gz

# system-wide Go profile
sudo tee /etc/profile.d/golang.sh >/dev/null <<'EOF'
export GOPATH="$HOME/go"
export PATH="$PATH:/usr/local/go/bin:$HOME/go/bin"
EOF
sudo chmod +x /etc/profile.d/golang.sh
# Source for current session
source /etc/profile.d/golang.sh || true

echo -e "${GREEN}[+] Installing Go-based tools (subfinder, httpx, katana, nuclei, aquatone)...${RESET}"
# set GO111MODULE=on to ensure go install works on older go versions
export GO111MODULE=on

go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest || true
go install github.com/projectdiscovery/httpx/cmd/httpx@latest || true
go install github.com/projectdiscovery/katana/cmd/katana@latest || true
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest || true
go install github.com/michenriksen/aquatone@latest || true

# Python deps
echo -e "${GREEN}[+] Installing Python packages (Pillow, requests)...${RESET}"
python3 -m pip install --user pillow requests

echo -e "${GREEN}[+] Installer complete.${RESET}"
echo -e "${YELLOW}Important:${RESET} Run 'source /etc/profile.d/golang.sh' in your shell to make Go tools available in PATH for this session."
echo -e "${YELLOW}Then run the recon script: ./recon_slytherins${RESET}"
