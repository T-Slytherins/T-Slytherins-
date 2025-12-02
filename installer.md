# Installation Guide for Kali Linux 2024+

## 🚨 Important: Kali Linux 2024 Changes

Starting with Kali Linux 2024, Python package management has changed:
- **System Python is now externally managed** (PEP 668)
- **pip install requires virtual environments**
- This is a **security feature**, not a bug!

## ✅ Correct Installation Process

Follow these steps **in order**:

### Step 1: Fix Repository Mirrors (If Needed)

If you got mirror errors, fix them first:

```bash
# Quick fix for mirror issues
sudo sed -i 's|mirrors.tuna.tsinghua.edu.cn|http.kali.org|g' /etc/apt/sources.list
sudo apt clean
sudo apt update
```

Or use the comprehensive fix:

```bash
# Create fix script
cat > fix_mirrors.sh << 'EOF'
#!/bin/bash
sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup
cat | sudo tee /etc/apt/sources.list << 'EOFINNER'
deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware
deb-src http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware
EOFINNER
sudo apt clean
sudo apt update
EOF

chmod +x fix_mirrors.sh
./fix_mirrors.sh
```

### Step 2: Install System Dependencies

```bash
# Essential packages
sudo apt update
sudo apt install -y wget curl git nmap python3 python3-pip python3-venv xterm
```

### Step 3: Install Go Tools (Main Installer)

```bash
# Make installer executable
chmod +x installer.sh

# Run installer (installs Go and reconnaissance tools)
sudo ./installer.sh

# Activate Go environment
source /etc/profile.d/golang.sh
```

### Step 4: Setup Python Virtual Environment

```bash
# Make venv installer executable
chmod +x install_with_venv.sh

# Run venv installer (NO sudo!)
./install_with_venv.sh
```

This will:
- ✅ Create isolated Python environment
- ✅ Install all Python dependencies safely
- ✅ Create helper scripts
- ✅ Test all imports

### Step 5: Verify Installation

```bash
# Test Go tools
subfinder -version
amass -version
nuclei -version

# Test Python (in venv)
source venv/bin/activate
python3 -c "import PIL, requests, dns.resolver, nmap; print('✓ All OK')"
deactivate
```

### Step 6: Run Reconnaissance

```bash
# Option 1: Using helper script (easiest)
./run_recon.sh

# Option 2: Manual activation
source venv/bin/activate
./recon_slytherins
deactivate
```

## 🔧 Troubleshooting

### Issue: "externally-managed-environment" Error

**This is expected!** Don't use `--break-system-packages`

**Solution:** Use the virtual environment installer:
```bash
./install_with_venv.sh
```

### Issue: Mirror Connection Errors

**Symptoms:**
```
Could not connect to mirrors.tuna.tsinghua.edu.cn
Connection refused
Network is unreachable
```

**Solution:**
```bash
# Replace problematic mirrors
sudo nano /etc/apt/sources.list

# Use this content:
deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware

# Save and update
sudo apt clean
sudo apt update
```

### Issue: "gnome-terminal not found"

**This is fine!** The tool supports multiple terminals:

```bash
# Install any of these
sudo apt install -y xterm           # Lightweight
sudo apt install -y xfce4-terminal  # Kali default
sudo apt install -y konsole         # KDE
sudo apt install -y terminator      # Advanced

# Or run in background mode (no terminals needed)
./recon_slytherins  # Will auto-detect available terminal
```

### Issue: Go tools not found

**Solution:**
```bash
# Activate Go environment
source /etc/profile.d/golang.sh

# Add to your .bashrc permanently
echo 'source /etc/profile.d/golang.sh' >> ~/.bashrc

# Verify
which subfinder
echo $GOPATH
```

## 📋 Complete Command Summary

```bash
# 1. Fix mirrors (if needed)
sudo sed -i 's|mirrors.tuna.tsinghua.edu.cn|http.kali.org|g' /etc/apt/sources.list
sudo apt update

# 2. Install system packages
sudo apt install -y wget curl git nmap python3 python3-pip python3-venv xterm

# 3. Install Go tools
chmod +x installer.sh
sudo ./installer.sh
source /etc/profile.d/golang.sh

# 4. Setup Python venv
chmod +x install_with_venv.sh
./install_with_venv.sh

# 5. Run reconnaissance
./run_recon.sh
```

## ⚠️ What NOT to Do

❌ **Don't use --break-system-packages**
```bash
# BAD - Don't do this!
pip3 install --break-system-packages package_name
```
This can break your Kali installation!

❌ **Don't run pip as root without venv**
```bash
# BAD - Don't do this!
sudo pip3 install package_name
```

❌ **Don't skip the venv installer**
The virtual environment is **required** for modern Kali!

## ✅ Best Practices for Kali 2024+

1. **Always use virtual environments** for Python packages
2. **Use apt** for system-wide tools (nmap, firefox, etc.)
3. **Use Go install** for reconnaissance tools
4. **Activate venv** before running Python scripts
5. **Keep venv isolated** - one per project

## 🎯 Quick Start (TL;DR)

```bash
# One-time setup
sudo apt update && sudo apt install -y git python3-venv xterm
git clone <your-repo>
cd T-SLYTHERINS-Fixed
sudo ./installer.sh
source /etc/profile.d/golang.sh
./install_with_venv.sh

# Every time you use it
./run_recon.sh
```

## 🔍 Understanding the Changes

### Why Virtual Environments?

**Before (Kali 2023):**
- `pip3 install` worked system-wide
- Could break system Python
- Package conflicts common

**Now (Kali 2024):**
- System Python is protected
- Virtual environments required
- Cleaner, safer, more professional

### Benefits:
- ✅ No system Python pollution
- ✅ No package conflicts
- ✅ Easy to clean up (just delete venv/)
- ✅ Follows Python best practices
- ✅ More portable

## 📚 Additional Resources

- [Kali Python Documentation](https://www.kali.org/docs/general-use/python3-external-packages/)
- [PEP 668 Specification](https://peps.python.org/pep-0668/)
- [Python Virtual Environments Guide](https://docs.python.org/3/library/venv.html)

## 🎓 Learning Points

If you're learning pentesting on Kali:

1. **Virtual environments are industry standard**
   - Professional developers use them
   - They're not a Kali quirk
   
2. **System protection is good**
   - Prevents accidental damage
   - Forces good habits
   
3. **Understanding packaging helps**
   - Know when to use apt
   - Know when to use pip (in venv)
   - Know when to use Go install

## 💡 Pro Tips

### Make venv activation automatic

Add to `~/.bashrc`:
```bash
# Auto-activate T-SLYTHERINS venv when entering directory
cd() {
    builtin cd "$@"
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
    fi
}
```

### Create alias for quick access

Add to `~/.bashrc`:
```bash
alias recon='cd ~/T-SLYTHERINS-Fixed && source venv/bin/activate && ./recon_slytherins'
```

Now just type `recon` from anywhere!

## 🆘 Still Having Issues?

If you followed all steps and still have problems:

1. **Check your Kali version:**
   ```bash
   cat /etc/os-release
   lsb_release -a
   ```

2. **Verify Python version:**
   ```bash
   python3 --version  # Should be 3.11+
   ```

3. **Check venv is created:**
   ```bash
   ls -la venv/
   ```

4. **Review logs:**
   ```bash
   tail -f T-SLYTHERINS-OUTPUT-*/subdomains.log
   ```

5. **Start fresh:**
   ```bash
   rm -rf venv/
   ./install_with_venv.sh
   ```

## 📞 Getting Help

- Open an issue on GitHub
- Include your Kali version
- Include error messages
- Describe what you tried

---

**Remember:** The virtual environment approach is the **correct** and **professional** way to handle Python packages in modern Linux distributions, not just Kali!
