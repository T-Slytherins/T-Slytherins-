#!/bin/bash
set -e

echo ""
echo "=========================================="
echo "  T-SLYTHERINS Recon Suite Installer"
echo "=========================================="
echo ""
sleep 1

# ------------------------------------------------------
echo "[1] Updating system..."
sudo apt update -y

# ------------------------------------------------------
echo "[2] Removing old Go..."
sudo rm -rf /usr/local/go

# ------------------------------------------------------
echo "[3] Installing latest Go..."
LATEST_GO=$(curl -s https://go.dev/VERSION?m=text)
wget -q "https://go.dev/dl/${LATEST_GO}.linux-amd64.tar.gz" -O /tmp/go.tar.gz
sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz

# ------------------------------------------------------
echo "[4] Creating system-wide Go PATH..."
sudo tee /etc/profile.d/golang.sh >/dev/null <<'EOF'
export GOPATH="$HOME/go"
export PATH="$PATH:/usr/local/go/bin:$HOME/go/bin"
EOF

sudo chmod +x /etc/profile.d/golang.sh

# load immediately
source /etc/profile.d/golang.sh

# ------------------------------------------------------
echo "[5] Installing APT tools..."
sudo apt install -y amass xfce4-terminal

# ------------------------------------------------------
echo "[6] Installing Go tools..."
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/tomnomnom/assetfinder@latest

# ------------------------------------------------------
echo "[7] Verifying tools..."
TOOLS=(go amass subfinder assetfinder httpx katana)

for tool in "${TOOLS[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo "   ✔ $tool OK"
    else
        echo "   ✘ $tool NOT FOUND"
    fi
done

# ------------------------------------------------------
echo ""
echo "=========================================="
echo "   INSTALLATION COMPLETE"
echo "=========================================="
echo ""
echo "➡ RUN THIS COMMAND to enable Go tools NOW:"
echo "   source /etc/profile.d/golang.sh"
echo ""
echo "➡ Then run       ./recon_slytherins"
echo ""
