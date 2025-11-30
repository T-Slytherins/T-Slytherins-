#!/bin/bash
set -e  # Stop on any error

echo ""
echo "=========================================="
echo "   T-SLYTHERINS Recon Suite Installer"
echo "=========================================="
echo ""

sleep 1

# ------------------------------------------------------
# 1. UPDATE SYSTEM
# ------------------------------------------------------
echo "[1] Updating system..."
sudo apt update -y


# ------------------------------------------------------
# 2. REMOVE OLD GO
# ------------------------------------------------------
if command -v go >/dev/null 2>&1; then
    echo "[2] Removing old Go installation..."
    sudo rm -rf /usr/local/go
fi


# ------------------------------------------------------
# 3. INSTALL LATEST GO
# ------------------------------------------------------
echo "[3] Installing latest Go version..."

LATEST_GO=$(curl -s https://go.dev/VERSION?m=text)  # ex: go1.23.3

# Validate
if [[ -z "$LATEST_GO" ]]; then
    echo "✘ ERROR: Could not retrieve Go version"
    exit 1
fi

GO_URL="https://go.dev/dl/${LATEST_GO}.linux-amd64.tar.gz"

echo "→ Downloading $GO_URL"
wget -q "$GO_URL" -O /tmp/go.tar.gz

# Verify file is a valid tar.gz
if ! file /tmp/go.tar.gz | grep -q "gzip compressed data"; then
    echo "✘ ERROR: Downloaded Go file is not a valid tar.gz"
    exit 1
fi

sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz


# ------------------------------------------------------
# 3B. SETUP PATH FOR GO
# ------------------------------------------------------
echo "[3B] Updating PATH for Go..."

if ! grep -q "/usr/local/go/bin" ~/.bashrc; then
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
fi

if ! grep -q '$HOME/go/bin' ~/.bashrc; then
    echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
fi

# GOPATH
if ! grep -q 'export GOPATH=' ~/.bashrc; then
    echo 'export GOPATH=$HOME/go' >> ~/.bashrc
fi

source ~/.bashrc


# ------------------------------------------------------
# 4. INSTALL APT DEPENDENCIES
# ------------------------------------------------------
echo "[4] Installing dependencies (xfce4-terminal, amass)..."
sudo apt install -y xfce4-terminal amass


# ------------------------------------------------------
# 5. INSTALL GO-BASED TOOLS
# ------------------------------------------------------
# Ensure Go is working
if ! command -v go >/dev/null; then
    echo "✘ ERROR: Go installation failed!"
    exit 1
fi

echo "[5] Installing Subfinder..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

echo "[6] Installing Httpx..."
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

echo "[7] Installing Katana..."
go install -v github.com/projectdiscovery/katana/cmd/katana@latest

echo "[8] Installing Assetfinder..."
go install -v github.com/tomnomnom/assetfinder@latest


# ------------------------------------------------------
# 6. VERIFY INSTALLATION
# ------------------------------------------------------
echo ""
echo "[✔] Checking installed tools..."

TOOLS=(go amass subfinder httpx katana assetfinder xfce4-terminal)

for tool in "${TOOLS[@]}"; do
    if command -v $tool >/dev/null 2>&1; then
        echo "   ✔ $tool found"
    else
        echo "   ✘ $tool NOT FOUND — something went wrong!"
    fi
done


# ------------------------------------------------------
# 7. DONE
# ------------------------------------------------------
echo ""
echo "=========================================="
echo " ✔ INSTALLATION COMPLETE"
echo "=========================================="
echo ""
echo "➡ Restart your terminal OR run:  source ~/.bashrc"
echo "➡ You can now run your recon tool:  ./recon_slytherins"
echo ""
