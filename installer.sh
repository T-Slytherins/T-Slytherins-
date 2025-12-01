#!/bin/bash

set -e

echo ""
echo "=========================================="
echo "     T‑SLYTHERINS Recon Suite Installer"
echo "=========================================="
echo ""

# -----------------------------------------------------------
# 1. UPDATE SYSTEM
# -----------------------------------------------------------
echo "[+] Updating APT..."
sudo apt update -y

# -----------------------------------------------------------
# 2. INSTALL APT DEPENDENCIES
# -----------------------------------------------------------
APT_PACKAGES=(
    python3
    python3-venv
    python3-pip
    amass
    xfce4-terminal
    firefox-esr
    chromium
    unzip
    wget
    curl
    xvfb
    scrot
    libid3tag0
    libimlib2t64
)

echo "[+] Installing required APT packages..."
for pkg in "${APT_PACKAGES[@]}"; do
    echo "[*] Installing $pkg ..."
    sudo apt install -y "$pkg" >/dev/null 2>&1 || echo "[!] Warning: Failed to install $pkg (may already exist)"
done

# -----------------------------------------------------------
# 3. INSTALL GO
# -----------------------------------------------------------
echo "[+] Detecting latest Go version..."
LATEST_GO=$(curl -s https://go.dev/VERSION?m=text | head -n 1)
echo "[+] Latest Go Version: $LATEST_GO"

GO_URL="https://go.dev/dl/${LATEST_GO}.linux-amd64.tar.gz"
echo "[+] Downloading: $GO_URL"
wget -q "$GO_URL" -O /tmp/go.tar.gz

echo "[+] Extracting Go..."
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz

echo "[+] Configuring Go PATH..."
if ! grep -q "export PATH=\$PATH:/usr/local/go/bin" ~/.bashrc; then
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
fi

export PATH="$PATH:/usr/local/go/bin"

# -----------------------------------------------------------
# 4. INSTALL GO RECON TOOLS
# -----------------------------------------------------------
echo "[+] Installing Go-based Recon Tools..."

GO_TOOLS=(
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    "github.com/projectdiscovery/httpx/cmd/httpx@latest"
    "github.com/projectdiscovery/katana/cmd/katana@latest"
    "github.com/tomnomnom/assetfinder@latest"
)

for tool in "${GO_TOOLS[@]}"; do
    echo "[+] go install $tool"
    go install "$tool"
done

# -----------------------------------------------------------
# 5. CREATE PYTHON VENV
# -----------------------------------------------------------
echo "[+] Creating Python virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo "[+] Upgrading pip inside venv..."
pip install --upgrade pip setuptools wheel >/dev/null

# -----------------------------------------------------------
# 6. INSTALL PYTHON DEPENDENCIES IN VENV
# -----------------------------------------------------------
echo "[+] Installing Python modules..."
pip install pillow requests tqdm >/dev/null

deactivate

# -----------------------------------------------------------
# 7. CREATE RUN ALIASES
# -----------------------------------------------------------
if ! grep -q "TSLYTHERINS" ~/.bashrc; then
    echo "[+] Adding launcher alias to .bashrc"
    echo "" >> ~/.bashrc
    echo "# TSLYTHERINS" >> ~/.bashrc
    echo "alias slytherins='./run_recon.sh'" >> ~/.bashrc
fi

# -----------------------------------------------------------
# 8. FINISH
# -----------------------------------------------------------
echo ""
echo "=========================================="
echo "  INSTALLATION COMPLETE ✔"
echo "=========================================="
echo ""
echo "Run the tool using:"
echo "   ./run_recon.sh"
echo ""
echo "or simply:"
echo "   slytherins"
