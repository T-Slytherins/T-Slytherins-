#!/bin/bash

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
# 2. REMOVE OLD GO (if any)
# ------------------------------------------------------
if command -v go >/dev/null 2>&1; then
    echo "[2] Removing old Go installation..."
    sudo rm -rf /usr/local/go
fi


# ------------------------------------------------------
# 3. INSTALL LATEST GO (OFFICIAL)
# ------------------------------------------------------
echo "[3] Installing latest Go version..."

LATEST_GO=$(curl -s https://go.dev/VERSION?m=text)

wget https://go.dev/dl/${LATEST_GO}.linux-amd64.tar.gz -O /tmp/go.tar.gz

sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz

# Ensure PATH is set
if ! grep -q "export PATH=\$PATH:/usr/local/go/bin:\$HOME/go/bin" ~/.bashrc; then
    echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc
fi

source ~/.bashrc


# ------------------------------------------------------
# 4. INSTALL APT PACKAGES
# ------------------------------------------------------
echo "[4] Installing dependencies (xfce4-terminal, amass)..."
sudo apt install -y xfce4-terminal amass


# ------------------------------------------------------
# 5. INSTALL GO-BASED RECON TOOLS
# ------------------------------------------------------
echo "[5] Installing Subfinder..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

echo "[6] Installing Httpx..."
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

echo "[7] Installing Katana..."
go install github.com/projectdiscovery/katana/cmd/katana@latest

echo "[8] Installing Assetfinder..."
go install github.com/tomnomnom/assetfinder@latest


# ------------------------------------------------------
# 6. VERIFY INSTALLATION
# ------------------------------------------------------
echo ""
echo "[✔] Checking installed tools..."

for tool in go amass subfinder httpx katana assetfinder xfce4-terminal; do
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
