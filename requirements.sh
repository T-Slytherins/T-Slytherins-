#!/bin/bash

echo ""
echo "=========================================="
echo "  T-SLYTHERINS Recon Suite Installer"
echo "=========================================="
echo ""

sleep 1

# Make script NEVER fail
set +e

log() { echo -e "\033[92m[+] $1\033[0m"; }
err() { echo -e "\033[91m[✘] $1\033[0m"; }

# ------------------------------------------------------
log "Updating system..."
sudo apt update -y

# ------------------------------------------------------
log "Removing any old Go installation..."
sudo rm -rf /usr/local/go
rm -rf "$HOME/go"

# ------------------------------------------------------
log "Fetching latest Go version..."
LATEST_GO=$(curl -s https://go.dev/VERSION?m=text)

if [[ -z "$LATEST_GO" ]]; then
    err "Could not fetch Go version! Using fallback: go1.23.3"
    LATEST_GO="go1.23.3"
fi

GO_URL="https://go.dev/dl/${LATEST_GO}.linux-amd64.tar.gz"
log "Downloading: $GO_URL"

# Try normal download
wget --no-check-certificate -O /tmp/go.tar.gz "$GO_URL"

# On failure, retry using curl
if [[ $? -ne 0 ]]; then
    err "wget failed. Retrying with curl..."
    curl -L "$GO_URL" -o /tmp/go.tar.gz
fi

if [[ ! -f /tmp/go.tar.gz ]]; then
    err "Go download failed completely."
    exit 1
fi

# ------------------------------------------------------
log "Extracting Go..."
sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz

# ------------------------------------------------------
log "Creating system-wide Go PATH..."
sudo tee /etc/profile.d/golang.sh >/dev/null <<'EOF'
export GOPATH="$HOME/go"
export PATH="$PATH:/usr/local/go/bin:$HOME/go/bin"
EOF

sudo chmod +x /etc/profile.d/golang.sh
source /etc/profile.d/golang.sh

# ------------------------------------------------------
log "Installing APT dependencies..."
sudo apt install -y amass xfce4-terminal python3 python3-pip

# ------------------------------------------------------
log "Installing Go tools (subfinder, httpx, katana, assetfinder)..."

go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/tomnomnom/assetfinder@latest

# ------------------------------------------------------
log "Verifying tools..."

TOOLS=(go amass subfinder assetfinder httpx katana)

for tool in "${TOOLS[@]}"; do
    if command -v "$tool" >/dev/null; then
        log "$tool OK"
    else
        err "$tool NOT FOUND — trying reinstall"
        go install $(which "$tool")@latest 2>/dev/null
    fi
done

echo ""
echo "=========================================="
echo "   INSTALLATION COMPLETE"
echo "=========================================="
echo ""
echo "➡ Run to activate:   source /etc/profile.d/golang.sh"
echo "➡ Then start recon:  ./recon_slytherins"
echo ""
