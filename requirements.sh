#!/bin/bash
set -e

GREEN="\033[92m"
RED="\033[91m"
RESET="\033[0m"

echo ""
echo "=========================================="
echo " T-SLYTHERINS Recon Suite Installer"
echo "=========================================="
echo ""

# -------------------------------------------------------------------
echo "[+] Updating system..."
sudo apt update -y

# -------------------------------------------------------------------
echo "[+] Detecting latest Go version safely..."
LATEST_GO=$(curl -s https://go.dev/VERSION?m=text | head -n 1)

if [[ -z "$LATEST_GO" ]]; then
    echo "${RED}[✘] Could not fetch latest Go version.${RESET}"
    exit 1
fi

GO_TAR="${LATEST_GO}.linux-amd64.tar.gz"
GO_URL="https://go.dev/dl/${GO_TAR}"

echo "[+] Latest Go = $LATEST_GO"
echo "[+] Download URL = $GO_URL"

# -------------------------------------------------------------------
echo "[+] Removing any previous Go..."
sudo rm -rf /usr/local/go

echo "[+] Downloading Go..."
wget -q "$GO_URL" -O /tmp/go.tar.gz || {
    echo "${RED}[✘] wget failed, retrying with curl...${RESET}"
    curl -L "$GO_URL" -o /tmp/go.tar.gz || {
        echo "${RED}[✘] Both wget and curl failed — exiting.${RESET}"
        exit 1
    }
}

echo "[+] Extracting Go..."
sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm -f /tmp/go.tar.gz

# -------------------------------------------------------------------
echo "[+] Creating system-wide Go PATH..."
sudo tee /etc/profile.d/golang.sh >/dev/null <<'EOF'
export GOPATH="$HOME/go"
export PATH="$PATH:/usr/local/go/bin:$HOME/go/bin"
EOF

sudo chmod +x /etc/profile.d/golang.sh
source /etc/profile.d/golang.sh

# -------------------------------------------------------------------
echo "[+] Installing APT dependencies..."
sudo apt install -y amass xfce4-terminal python3 python3-pip

# -------------------------------------------------------------------
echo "[+] Installing Go tools..."
TOOLS=(
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    "github.com/projectdiscovery/httpx/cmd/httpx@latest"
    "github.com/projectdiscovery/katana/cmd/katana@latest"
    "github.com/tomnomnom/assetfinder@latest"
)

for TOOL in "${TOOLS[@]}"; do
    echo "[+] Installing: $TOOL"
    go install "$TOOL" || echo "${RED}[!] Failed installing $TOOL${RESET}"
done

# -------------------------------------------------------------------
echo "[+] Verifying tools..."
CHECK_TOOLS=(go amass subfinder assetfinder httpx katana)

for t in "${CHECK_TOOLS[@]}"; do
    if command -v "$t" >/dev/null 2>&1; then
        echo "   ✔ $t OK"
    else
        echo "   ✘ $t missing, reinstalling..."

        case "$t" in
            subfinder)
                go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest ;;
            httpx)
                go install github.com/projectdiscovery/httpx/cmd/httpx@latest ;;
            katana)
                go install github.com/projectdiscovery/katana/cmd/katana@latest ;;
            assetfinder)
                go install github.com/tomnomnom/assetfinder@latest ;;
            go)
                echo "${RED}[!] GO missing — installation failed.${RESET}"
                ;;
        esac
    fi
done

echo ""
echo "=========================================="
echo "  INSTALLATION COMPLETE ✔"
echo "=========================================="
echo ""
echo "➡ Run this to activate Go PATH NOW:"
echo "   source /etc/profile.d/golang.sh"
echo ""
echo "➡ Then start recon:"
echo "   ./recon_slytherins"
echo ""
