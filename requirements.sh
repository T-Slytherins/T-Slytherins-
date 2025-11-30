#!/bin/bash
set -e

echo ""
echo "=========================================="
echo "  T-SLYTHERINS Recon Suite Installer"
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
# 3. INSTALL NEW GO
# ------------------------------------------------------
echo "[3] Installing latest Go version..."

LATEST_GO=$(curl -s https://go.dev/VERSION?m=text)
GO_URL="https://go.dev/dl/${LATEST_GO}.linux-amd64.tar.gz"

echo "→ Downloading $LATEST_GO ..."
wget -q "$GO_URL" -O /tmp/go.tar.gz

sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz

# ------------------------------------------------------
# 3B. GLOBAL PATH FIX (IMPORTANT!)
# ------------------------------------------------------
echo "[3B] Adding Go paths system-wide..."

sudo tee /etc/profile.d/go_path.sh >/dev/null <<EOF
export GOPATH=\$HOME/go
export PATH=\$PATH:/usr/local/go/bin:\$HOME/go/bin
EOF

sudo chmod +x /etc/profile.d/go_path.sh
source /etc/profile.d/go_path.sh


# ------------------------------------------------------
# 4. INSTALL APT TOOLS
# ------------------------------------------------------
echo "[4] Installing APT tools..."
sudo apt install -y amass xfce4-terminal


# ------------------------------------------------------
# 5. INSTALL GO-BASED TOOLS
# ------------------------------------------------------
echo "[5] Installing Go-based tools..."

go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/tomnomnom/assetfinder@latest


# ------------------------------------------------------
# 6. VERIFY
# ------------------------------------------------------
echo ""
echo "[✔] Checking installed tools..."

for tool in go amass subfinder assetfinder httpx katana; do
    if command -v $tool >/dev/null 2>&1; then
        echo "   ✔ $tool OK"
    else
        echo "   ✘ $tool NOT FOUND (PATH issue)"
    fi
done


# ------------------------------------------------------
# DONE
# ------------------------------------------------------
echo ""
echo "=========================================="
echo " ✔ INSTALLATION COMPLETE"
echo "=========================================="
echo ""
echo "➡ RUN THIS COMMAND to load everything NOW:"
echo ""
echo "     source /etc/profile.d/go_path.sh"
echo ""
echo "➡ Then run your recon tool normally."
echo ""
