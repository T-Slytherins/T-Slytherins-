#!/usr/bin/env bash
set -euo pipefail

# T-SLYTHERINS Installer - updated (no upload, aquatone uses installed Firefox GUI)
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
RESET="\033[0m"

echo -e "${GREEN}T-SLYTHERINS Installer${RESET}"

echo -e "${GREEN}[+] Updating apt...${RESET}"
sudo apt update -y

echo -e "${GREEN}[+] Installing apt packages...${RESET}"
sudo apt install -y wget curl git build-essential xfce4-terminal xterm \
    python3 python3-pip python3-venv nmap jq firefox

# Install Go (latest)
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

sudo tee /etc/profile.d/golang.sh >/dev/null <<'EOF'
export GOPATH="$HOME/go"
export PATH="$PATH:/usr/local/go/bin:$HOME/go/bin"
EOF
sudo chmod +x /etc/profile.d/golang.sh
# source for current session if possible
if [ -f /etc/profile.d/golang.sh ]; then
  source /etc/profile.d/golang.sh || true
fi

export GO111MODULE=on

echo -e "${GREEN}[+] Installing Go tools (subfinder, httpx, katana, nuclei, aquatone)...${RESET}"
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest || true
go install github.com/projectdiscovery/httpx/cmd/httpx@latest || true
go install github.com/projectdiscovery/katana/cmd/katana@latest || true
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest || true
go install github.com/michenriksen/aquatone@latest || true

echo -e "${GREEN}[+] Installing Python packages (Pillow)...${RESET}"
python3 -m pip install --user pillow requests || true

echo -e "${GREEN}Installer finished.${RESET}"
echo -e "${YELLOW}Run 'source /etc/profile.d/golang.sh' then start recon with ./recon_slytherins${RESET}"
