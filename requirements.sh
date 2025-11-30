#!/bin/bash
set -e  # stop script if any command fails

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

# get only FIRST line of output (prevents "time ..." issue)
LATEST_GO=$(curl -s https://go.dev/VERSION?m=text | head -n 1 | tr -d '\r')

if [[ -z "$LATEST_GO" ]]; then
    echo "✘ ERROR: Could not fetch Go version"
    exit 1
fi

GO_URL="https://go.dev/dl/${LATEST_GO}.linux-amd64.tar.gz"
echo "→ Downloading $GO_URL"

wget -q "$GO_URL" -O /tmp/go.tar.gz

# verify it REALLY is gzip
if ! file /tmp/go.tar.gz | grep -q "gzip compressed data"; then
    echo "✘ ERROR: Go download corrupted or invalid"
    echo "    Received:"
    file /tmp/go.tar.gz
    exit 1
fi

sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz


# ------------------------------------------------------
# 3B. APPLY GO PATH TO THIS SCRIPT
# ------------------------------------------------------
echo "[3B] Updating PATH for Go..."

export GOPATH=$HOME/go
export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# persist in bashrc if not added before
grep -qxF 'export GOPATH=$HOME/go' ~/.bashrc || echo 'export GOPATH=$HOME/go' >> ~/.bashrc
grep -qxF 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' ~/.bashrc || echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc


# ------------------------------------------------------
# 4. INSTALL APT PACKAGES
# ------------------------------------------------------
echo "[4] Installing APT dependencies (amass)..."
sudo apt install -y amass


# ------------------------------------------------------
# 5. INSTALL GO-BASED TOOLS
# ------------------------------------------------------
if ! command -v go >/dev/null; then
    echo "✘ ERROR: Go installation failed"
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

TOOLS=(go amass subfinder httpx katana assetfinder)

for tool in "${TOOLS[@]}"; do
    if command -v $tool >/dev/null 2>&1; then
        echo "   ✔ $tool found"
    else
        echo "   ✘ $tool NOT FOUND — installation failed!"
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
echo "➡ Your recon suite is ready!"
echo ""
