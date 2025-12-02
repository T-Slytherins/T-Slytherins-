# ✅ Complete Your Installation

## Current Status: 95% Done! 🎉

Based on your output, here's what happened:

### ✅ Successfully Installed:
- Go 1.24.10
- subfinder ✓
- amass ✓
- assetfinder ✓
- httpx ✓
- katana ✓
- nuclei ✓
- System packages (nmap, etc.)

### ⚠️ Needs Attention:
- aquatone (failed due to Go version requirement)
- Python packages (need virtual environment)

---

## 🚀 Complete Installation Now

Run these commands **in order**:

### Step 1: Fix Aquatone (Optional but Recommended)

```bash
# Option A: Download and run fix script
chmod +x fix_aquatone.sh
./fix_aquatone.sh
```

**OR manually:**

```bash
# Download pre-built binary
wget https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip

# Extract
unzip aquatone_linux_amd64_1.7.0.zip

# Install
sudo mv aquatone ~/go/bin/
chmod +x ~/go/bin/aquatone

# Verify
aquatone --version
```

### Step 2: Activate Go Environment

```bash
source /etc/profile.d/golang.sh
```

### Step 3: Verify Go Tools

```bash
# Test each tool
subfinder -version
amass -version  
httpx -version
nuclei -version
katana -version
aquatone --version  # Should work now
```

### Step 4: Setup Python Virtual Environment

```bash
# Make venv installer executable
chmod +x install_with_venv.sh

# Run it (NO sudo needed!)
./install_with_venv.sh
```

This will install:
- pillow (screenshot processing)
- requests (HTTP library)
- dnspython (DNS operations)
- python-nmap (port scanning)

### Step 5: Make Scripts Executable

```bash
chmod +x recon_slytherins
chmod +x run_recon.sh
chmod +x activate_venv.sh
chmod +x modules/*.py
```

### Step 6: Test Everything

```bash
# Activate virtual environment
source venv/bin/activate

# Test Python imports
python3 << 'EOF'
import PIL
import requests
import dns.resolver
import nmap
print("✅ All Python packages OK!")
EOF

# Test Go tools
echo "Testing reconnaissance tools..."
subfinder -version && echo "✅ subfinder OK"
amass -version && echo "✅ amass OK"
httpx -version && echo "✅ httpx OK"
nuclei -version && echo "✅ nuclei OK"

# Deactivate
deactivate
```

---

## 🎯 You're Ready! Start Using It

### Quick Start:

```bash
# Run reconnaissance (easiest way)
./run_recon.sh
```

### Step-by-Step:

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Run scan
./recon_slytherins

# 3. Enter domain when prompted
# example.com

# 4. Wait for completion (1-2 hours)

# 5. Generate report
python3 modules/report.py T-SLYTHERINS-OUTPUT-example.com

# 6. View report
firefox T-SLYTHERINS-OUTPUT-example.com/report.html

# 7. Deactivate when done
deactivate
```

---

## 📋 Quick Command Checklist

Copy and paste these commands:

```bash
# Fix aquatone (if needed)
wget https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip
unzip aquatone_linux_amd64_1.7.0.zip
mv aquatone ~/go/bin/
chmod +x ~/go/bin/aquatone

# Activate Go
source /etc/profile.d/golang.sh

# Setup Python venv
./install_with_venv.sh

# Make scripts executable
chmod +x recon_slytherins run_recon.sh activate_venv.sh
chmod +x modules/*.py

# Run your first scan
./run_recon.sh
```

---

## 🔍 Verification Commands

Use these to check if everything is working:

```bash
# Check Go tools
which subfinder && echo "✅ subfinder in PATH"
which amass && echo "✅ amass in PATH"
which httpx && echo "✅ httpx in PATH"
which nuclei && echo "✅ nuclei in PATH"
which aquatone && echo "✅ aquatone in PATH"

# Check Python venv
ls venv/ && echo "✅ Virtual environment exists"

# Check scripts
ls -l recon_slytherins run_recon.sh && echo "✅ Scripts exist"

# Full system check
echo "=== SYSTEM CHECK ==="
echo "Go version: $(go version)"
echo "Python version: $(python3 --version)"
echo "Nmap version: $(nmap --version | head -1)"
echo "==================="
```

---

## ⚠️ If Aquatone Fails

**Don't worry!** Aquatone is optional. The tool will work without it.

### Alternative: Use Manual Screenshots

You can take screenshots manually later:
```bash
# After your scan completes
cat T-SLYTHERINS-OUTPUT-example.com/httpx_results.txt | while read url; do
    firefox --screenshot "$url"
done
```

### Or: Use EyeWitness Instead

```bash
sudo apt install eyewitness
eyewitness -f T-SLYTHERINS-OUTPUT-example.com/httpx_results.txt
```

---

## 🐛 Troubleshooting

### Issue: "Command not found" for Go tools

```bash
# Add to current session
source /etc/profile.d/golang.sh

# Add permanently to .bashrc
echo 'source /etc/profile.d/golang.sh' >> ~/.bashrc

# Verify PATH
echo $PATH | grep go
```

### Issue: Python import errors

```bash
# Recreate virtual environment
rm -rf venv/
./install_with_venv.sh
```

### Issue: Permission denied

```bash
# Fix permissions
chmod +x installer.sh
chmod +x install_with_venv.sh
chmod +x recon_slytherins
chmod +x run_recon.sh
chmod +x modules/*.py
```

---

## 📊 What You Have Now

```
✅ Go 1.24.10
✅ subfinder (subdomain enumeration)
✅ amass (subdomain enumeration)
✅ assetfinder (subdomain enumeration)
✅ httpx (HTTP probing)
✅ katana (web crawling)
✅ nuclei (vulnerability scanning)
⚠️  aquatone (screenshots - fix with script above)
⏳ Python venv (install with ./install_with_venv.sh)
```

---

## 🎓 Next Steps After Installation

1. **Update nuclei templates:**
   ```bash
   nuclei -update-templates
   ```

2. **Test on a safe target:**
   ```bash
   ./run_recon.sh
   # Enter: testphp.vulnweb.com (legal test site)
   ```

3. **Read the documentation:**
   ```bash
   cat README.md
   ```

4. **Configure for your needs:**
   - Edit `modules/subdomains.py` for custom wordlists
   - Edit `modules/portscan.py` for port ranges
   - Edit `modules/vulnscan.py` for specific templates

---

## 🎉 Success Criteria

You'll know everything is working when:

✅ All commands in "Verification Commands" pass
✅ `./run_recon.sh` starts without errors
✅ Terminal windows open (or modules run in background)
✅ Output directory gets created
✅ Report generates successfully

---

## 💡 Pro Tips

1. **Always activate venv first:**
   ```bash
   source venv/bin/activate
   ```

2. **Use the helper script:**
   ```bash
   ./run_recon.sh  # Does everything for you
   ```

3. **Monitor progress:**
   ```bash
   tail -f T-SLYTHERINS-OUTPUT-*/subdomains.log
   ```

4. **Run in screen/tmux for long scans:**
   ```bash
   screen -S recon
   ./run_recon.sh
   # Press Ctrl+A then D to detach
   # screen -r recon to reattach
   ```

---

## 🚀 Ready to Go!

Your installation is **95% complete**. Just run:

```bash
source /etc/profile.d/golang.sh
./install_with_venv.sh
./run_recon.sh
```

**That's it!** You're ready to do professional reconnaissance! 🎯

---

## 📞 Need Help?

If you get stuck:
1. Check the troubleshooting section above
2. Review logs in output directories
3. Open an issue on GitHub
4. Include error messages and your Kali version

**Happy Hacking!** 🐍🔒
