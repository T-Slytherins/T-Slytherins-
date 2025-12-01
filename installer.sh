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
    firefox-esr
    chromium
    unzip
    wget
    curl
    xvfb
    scrot
)

for pkg in "${APT_PACKAGES[@]}"; do
    echo "[*] Installing $pkg ..."
    sudo apt install -y "$pkg" || echo -e "${YELLOW}[!] Skipped $pkg (not available)${RESET}"
done

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
echo -e "${GREEN}[+] Creating Python Virtual Environment (venv)...${RESET}"

if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    echo -e "${GREEN}[+] venv created.${RESET}"
else
    echo -e "${YELLOW}[!] venv already exists — reusing it.${RESET}"
fi

echo -e "${GREEN}[+] Activating virtual environment...${RESET}"
source venv/bin/activate

echo -e "${GREEN}[+] Installing Python requirements inside venv...${RESET}"

if [[ -f "requirements.txt" ]]; then
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo -e "${YELLOW}[!] No requirements.txt found, skipping.${RESET}"
fi

deactivate

# -------------------------------------------------------------------
echo -e "${GREEN}[+] Creating auto-launch wrapper script...${RESET}"

cat << 'EOF' > run_slytherins.sh
#!/bin/bash
source venv/bin/activate
python3 recon_slytherins
deactivate
EOF

chmod +x run_slytherins.sh

# -------------------------------------------------------------------
echo -e "${GREEN}[+] Verifying essential tools...${RESET}"

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
echo -e "[*] Your virtual environment is ready: ${YELLOW}./venv/${RESET}"
echo -e "[*] Start the recon suite using:"
echo -e "      ${GREEN}./run_slytherins.sh${RESET}"
echo ""
echo -e "[*] If terminal doesn't recognize Go, run:"
echo -e "      ${YELLOW}source /etc/profile.d/golang.sh${RESET}"
echo ""
