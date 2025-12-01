#!/bin/bash
set -e

GREEN="\033[92m"
RED="\033[91m"
YELLOW="\033[93m"
RESET="\033[0m"

echo ""
echo "=========================================="
echo -e "   ${GREEN}T‑SLYTHERINS Recon Suite Installer${RESET}"
echo "=========================================="
echo ""

# -------------------------------------------------------------------
echo -e "${GREEN}[+] Updating APT...${RESET}"
sudo apt update -y

# -------------------------------------------------------------------
echo -e "${GREEN}[+] Installing required APT packages...${RESET}"

APT_PACKAGES=(
    python3
    python3-pip
    python3-venv
    amass
    xfce4-terminal
    firefox-esr     # Kali default Firefox
    chromium        # Screenshot fallback
    unzip
    wget
    curl
)

for pkg in "${APT_PACKAGES[@]}"; do
    echo "[*] Installing $pkg ..."
    sudo apt install -y "$pkg" || echo -e "${YELLOW}[!] Skipped $pkg (not available)${RESET}"
done

# -------------------------------------------------------------------
echo -e "${GREEN}[+] Installing Aquatone dependencies...${RESET}"
sudo apt install -y xvfb scrot || true

# -------------------------------------------------------------------
echo -e "${GREEN}[+] Detecting latest Go version...${RESET}"
LATEST_GO=$(curl -s https://go.dev/VERSION?m=text | head -n 1)

if [[ -z "$LATEST_GO" ]]; then
    echo -e "${RED}[✘] Failed to fetch Go version.${RESET}"
    exit 1
fi

GO_TAR="${LATEST_GO}.linux-amd64.tar.gz"
GO_URL="https://go.dev/dl/${GO_TAR}"

echo "[+] Latest Go Version: $LATEST_GO"
echo "[+] Downloading: $GO_URL"

sudo rm -rf /usr/local/go

wget -q "$GO_URL" -O /tmp/go.tar.gz || {
    echo -e "${RED}[✘] wget failed, retrying with curl...${RESET}"
    curl -L "$GO_URL" -o /tmp/go.tar.gz || {
        echo -e "${RED}[✘] Could not download Go. Aborting.${RESET}"
        exit 1
    }
}

echo "[+] Extracting Go..."
sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm -f /tmp/go.tar.gz

echo -e "${GREEN}[+] Configuring Go PATH...${RESET}"

sudo tee /etc/profile.d/golang.sh >/dev/null <<'EOF'
export GOPATH="$HOME/go"
export PATH="$PATH:/usr/local/go/bin:$HOME/go/bin"
EOF

sudo chmod +x /etc/profile.d/golang.sh
source /etc/profile.d/golang.sh

# -------------------------------------------------------------------
echo -e "${GREEN}[+] Installing Go-based Recon Tools...${RESET}"

GO_TOOLS=(
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    "github.com/projectdiscovery/httpx/cmd/httpx@latest"
    "github.com/projectdiscovery/katana/cmd/katana@latest"
    "github.com/tomnomnom/assetfinder@latest"
)

for tool in "${GO_TOOLS[@]}"; do
    echo "[+] go install $tool"
    go install "$tool" || echo -e "${YELLOW}[!] Failed installing $tool${RESET}"
done

# -------------------------------------------------------------------
echo -e "${GREEN}[+] Installing Python module dependencies...${RESET}"

pip3 install --upgrade pip

REQUIREMENTS_FILE="requirements.txt"

if [[ -f "$REQUIREMENTS_FILE" ]]; then
    pip3 install -r "$REQUIREMENTS_FILE"
else
    echo -e "${YELLOW}[!] No requirements.txt found, skipping.${RESET}"
fi

# -------------------------------------------------------------------
echo -e "${GREEN}[+] Checking essential tools...${RESET}"

TOOLS=(go amass subfinder httpx katana assetfinder firefox-esr chromium)

for t in "${TOOLS[@]}"; do
    if command -v "$t" >/dev/null 2>&1; then
        echo "   ✔ $t OK"
    else
        echo -e "   ${RED}✘ Missing: $t${RESET}"
    fi
done

# -------------------------------------------------------------------
echo ""
echo "=========================================="
echo -e "   ${GREEN}INSTALLATION COMPLETE ✔${RESET}"
echo "=========================================="
echo ""
echo "[*] Restart your terminal or run:"
echo -e "      ${YELLOW}source /etc/profile.d/golang.sh${RESET}"
echo ""
echo "Then start the recon suite:"
echo -e "      ${GREEN}./recon_slytherins${RESET}"
echo ""
