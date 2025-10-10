# VPS Deployment Guide - Noobz Bot

## 🚀 Setup di VPS Linux (Ubuntu/Debian)

### Prerequisites
- VPS dengan Ubuntu 20.04+ atau Debian 10+
- SSH access ke VPS
- Python 3.9+ (recommended 3.11)
- Internet connection
- **API Keys Ready:**
  - Telegram API (https://my.telegram.org/apps)
  - Gemini API (https://makersuite.google.com/app/apikey)
  - TMDB API (https://www.themoviedb.org/settings/api)

---

## 📋 Step-by-Step Installation

### 1. Connect ke VPS via SSH

```bash
ssh root@your-vps-ip
# atau
ssh username@your-vps-ip
```

### 2. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Install Python & Dependencies

```bash
# Install Python 3.11 (recommended)
sudo apt install python3.11 python3.11-venv python3-pip git -y

# Atau gunakan default Python 3
sudo apt install python3 python3-venv python3-pip git -y

# Verify installation
python3 --version
pip3 --version
git --version
```

### 4. Clone Repository

```bash
# Masuk ke home directory
cd ~

# Clone dari GitHub
git clone https://github.com/RebootGod/noobz-bot.git

# Masuk ke folder project
cd noobz-bot
```

### 5. Setup Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Setup Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit dengan nano atau vim
nano .env
```

**Isi credentials di `.env`:**
```env
# Primary Telegram Account (Required)
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+62xxxxxxxxxxxxx

# Secondary Telegram Account (Optional - for flood protection)
TELEGRAM_API_ID_2=your_second_api_id
TELEGRAM_API_HASH_2=your_second_api_hash
TELEGRAM_PHONE_2=+62xxxxxxxxxxxxx  # Different phone number

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Gemini Model (Options: gemini-2.0-flash-exp, gemini-1.5-flash, gemini-1.5-pro)
GEMINI_MODEL=gemini-2.0-flash-exp

# TMDB Configuration
TMDB_API_KEY=your_tmdb_api_key_here

# Website & Bot Configuration
WEBSITE_URL=https://noobz.space
BOT_NAME=Noobz Announcement Bot
DEBUG=False
```

**⚡ Default model: `gemini-2.0-flash-exp` (Fastest & Latest)**
- See [GEMINI_MODELS.md](GEMINI_MODELS.md) untuk comparison models
- Free tier: 1500 requests/minute - more than enough!

**Save dan exit:**
- Nano: `Ctrl+X`, tekan `Y`, tekan `Enter`
- Vim: tekan `Esc`, ketik `:wq`, tekan `Enter`

### 7. Setup Telegram Accounts

```bash
# Activate venv jika belum
source venv/bin/activate

# Setup primary account (REQUIRED)
python setup_account_1.py
```

**Primary Account Setup:**
1. Bot akan show nomor telepon dari `.env`
2. Konfirmasi dengan ketik `y`
3. Check Telegram app - akan dapat kode login
4. Paste kode ke terminal
5. Jika ada 2FA, masukkan password
6. Session file `noobz_bot_session.session` akan dibuat

**Multi-Account Setup (OPTIONAL - for flood protection):**
```bash
# Setup secondary account
python setup_account_2.py
```

**Secondary Account Setup:**
1. Bot akan show nomor telepon kedua dari `.env`
2. Konfirmasi dengan ketik `y`
3. Check Telegram app - akan dapat kode login (ke phone kedua)
4. Paste kode ke terminal
5. Session file `noobz_bot_session_2.session` akan dibuat

**Multi-Account Benefits:**
- ✅ Auto-switch ke account backup jika kena flood limit
- ✅ No downtime saat rate limited
- ✅ Smart cooldown tracking
- ✅ Transparent failover

### 8. Run Bot

```bash
# Activate venv jika belum
source venv/bin/activate

# Run bot
python main.py
```

**Bot startup akan show:**
```
Starting Noobz Announcement Bot
Initializing Gemini AI...
Using model: gemini-2.0-flash-exp
✅ Primary account initialized: +62xxx (YourName)
✅ Secondary account initialized: +62yyy (BackupName)  # Jika setup multi-account
Multi-Account Manager initialized with 2 account(s)
Bot is running...
Listening for commands in Saved Messages...
```

**Test:** Kirim command di Saved Messages Telegram kamu

Press `Ctrl+C` to stop testing.

---

## 🤖 Gemini AI Model Configuration (Optional)

Bot default menggunakan **Gemini 2.0 Flash** (fastest & latest). 

### Change Model:

```bash
# Edit .env
nano ~/noobz-bot/.env

# Change model line:
GEMINI_MODEL=gemini-1.5-pro  # For best quality
# or
GEMINI_MODEL=gemini-1.5-flash  # For most stable
# or keep default
GEMINI_MODEL=gemini-2.0-flash-exp  # Fastest (default)
```

**Model Comparison:**
- `gemini-2.0-flash-exp` ⚡ - Fastest, latest (1500 RPM) **[DEFAULT]**
- `gemini-1.5-flash` - Stable, production (1000 RPM)
- `gemini-1.5-pro` - Best quality (360 RPM)

**Full guide:** See [GEMINI_MODELS.md](GEMINI_MODELS.md)

---

## 🔄 Run Bot Permanently (Background)

Ada beberapa cara untuk run bot terus-menerus:

### Option 1: Using Screen (Recommended untuk testing)

```bash
# Install screen
sudo apt install screen -y

# Create new screen session
screen -S noobz-bot

# Activate venv
source ~/noobz-bot/venv/bin/activate

# Run bot
cd ~/noobz-bot
python main.py

# Detach dari screen (bot tetap running)
# Tekan: Ctrl+A, lalu D

# Re-attach ke screen
screen -r noobz-bot

# List semua screen sessions
screen -ls

# Kill screen session
screen -X -S noobz-bot quit
```

### Option 2: Using Systemd Service (Production Recommended)

**Create systemd service file:**

```bash
sudo nano /etc/systemd/system/noobz-bot.service
```

**Paste config ini:**
```ini
[Unit]
Description=Noobz Announcement Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/noobz-bot
Environment="PATH=/root/noobz-bot/venv/bin"
ExecStart=/root/noobz-bot/venv/bin/python /root/noobz-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**⚠️ IMPORTANT: Adjust paths jika kamu login bukan sebagai root!**

Jika username kamu bukan root, ganti:
- `/root/` menjadi `/home/your-username/`
- `User=root` menjadi `User=your-username`

**Enable dan start service:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable noobz-bot

# Start service
sudo systemctl start noobz-bot

# Check status
sudo systemctl status noobz-bot

# Stop service
sudo systemctl stop noobz-bot

# Restart service
sudo systemctl restart noobz-bot

# View logs
sudo journalctl -u noobz-bot -f

# View last 100 lines
sudo journalctl -u noobz-bot -n 100
```

### Option 3: Using PM2 (Node.js Process Manager)

```bash
# Install Node.js & npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install PM2
sudo npm install -g pm2

# Start bot dengan PM2
cd ~/noobz-bot
pm2 start main.py --interpreter venv/bin/python --name noobz-bot

# Manage dengan PM2
pm2 status              # Check status
pm2 logs noobz-bot      # View logs
pm2 restart noobz-bot   # Restart
pm2 stop noobz-bot      # Stop
pm2 delete noobz-bot    # Remove from PM2

# Auto-start on boot
pm2 startup
pm2 save
```

---

## 📊 Monitoring & Logs

### View Bot Logs

```bash
# Jika pakai screen
screen -r noobz-bot

# Jika pakai systemd
sudo journalctl -u noobz-bot -f

# Jika pakai PM2
pm2 logs noobz-bot

# View log file
tail -f ~/noobz-bot/bot.log

# View last 50 lines
tail -n 50 ~/noobz-bot/bot.log
```

### Check Bot Status

```bash
# Method 1: Check process
ps aux | grep python | grep main.py

# Method 2: If using systemd
sudo systemctl status noobz-bot

# Method 3: If using PM2
pm2 status
```

---

## 🔧 Maintenance Commands

### Update Bot dari GitHub

```bash
# Stop bot first
sudo systemctl stop noobz-bot
# atau keluar dari screen: Ctrl+A, D, lalu: screen -X -S noobz-bot quit

# Pull latest changes
cd ~/noobz-bot
git pull origin main

# Update dependencies (if requirements.txt changed)
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Start bot again
sudo systemctl start noobz-bot
# atau screen -S noobz-bot, source venv/bin/activate, python main.py
```

### Backup Important Files

```bash
# Backup .env dan session files
mkdir -p ~/backups
cp ~/noobz-bot/.env ~/backups/.env.backup
cp ~/noobz-bot/*.session ~/backups/

# Dengan timestamp
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf ~/backups/noobz-bot-backup-$DATE.tar.gz ~/noobz-bot/.env ~/noobz-bot/*.session
```

---

## 🛡️ Security Best Practices

### 1. File Permissions

```bash
# Protect .env file
chmod 600 ~/noobz-bot/.env

# Protect session files
chmod 600 ~/noobz-bot/*.session

# Verify permissions
ls -la ~/noobz-bot/
```

### 2. Firewall Setup (Optional)

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH (IMPORTANT!)
sudo ufw allow ssh

# Check status
sudo ufw status
```

### 3. Create Dedicated User (Recommended)

```bash
# Create user for bot
sudo adduser noobzbot

# Add to sudo group (optional)
sudo usermod -aG sudo noobzbot

# Switch to user
su - noobzbot

# Clone dan setup ulang dengan user ini
# (repeat steps 4-6 above)
```

---

## 🐛 Troubleshooting

### Issue: Bot tidak start

```bash
# Check Python version
python3 --version

# Check dependencies
source ~/noobz-bot/venv/bin/activate
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check .env file
cat ~/noobz-bot/.env

# Test run manually
cd ~/noobz-bot
source venv/bin/activate
python main.py
```

### Issue: Permission denied

```bash
# Fix ownership
sudo chown -R $USER:$USER ~/noobz-bot

# Fix permissions
chmod -R 755 ~/noobz-bot
chmod 600 ~/noobz-bot/.env
chmod 600 ~/noobz-bot/*.session
```

### Issue: Module not found

```bash
# Ensure venv is activated
source ~/noobz-bot/venv/bin/activate

# Reinstall requirements
pip install -r ~/noobz-bot/requirements.txt
```

### Issue: Session expired

```bash
# Delete session file
rm ~/noobz-bot/*.session

# Run bot again (akan minta login ulang)
python main.py
```

### Issue: Gemini API Error

**Error: "Model not found"**
```bash
# Check model name in .env
cat ~/noobz-bot/.env | grep GEMINI_MODEL

# Valid options:
# - gemini-2.0-flash-exp (default)
# - gemini-1.5-flash
# - gemini-1.5-pro
# - gemini-pro

# Fix typo if needed
nano ~/noobz-bot/.env
```

**Error: "Quota exceeded" / "Rate limit"**
```bash
# Check rate limits:
# gemini-2.0-flash-exp: 1500 RPM (free)
# gemini-1.5-flash: 1000 RPM (free)
# gemini-1.5-pro: 360 RPM (free)

# Solutions:
# 1. Wait 1 minute for reset
# 2. Switch to model dengan higher daily limit (1.5-pro)
# 3. Upgrade to paid tier
```

**Error: "API key invalid"**
```bash
# Verify API key
cat ~/noobz-bot/.env | grep GEMINI_API_KEY

# Get new key from:
# https://makersuite.google.com/app/apikey

# Update .env
nano ~/noobz-bot/.env

# Restart bot
sudo systemctl restart noobz-bot
```

---

## 📱 Testing After Deployment

1. **Check bot is running:**
   ```bash
   sudo systemctl status noobz-bot
   ```

2. **Check logs:**
   ```bash
   sudo journalctl -u noobz-bot -n 50
   ```
   
   **You should see:**
   ```
   Starting Noobz Announcement Bot
   Initializing Gemini AI...
   Using model: gemini-2.0-flash-exp
   Gemini model 'gemini-2.0-flash-exp' initialized
   Bot is running as: YourName (@yourusername)
   Listening for commands in Saved Messages...
   ```

3. **Test commands in Telegram Saved Messages:**
   ```
   /announce Test Channel Test message [550]
   /infofilm @yourself movie inception 2010
   ```

4. **Monitor logs real-time:**
   ```bash
   sudo journalctl -u noobz-bot -f
   ```

---

## 🔄 Quick Reference Commands

```bash
# Start bot
sudo systemctl start noobz-bot

# Stop bot
sudo systemctl stop noobz-bot

# Restart bot
sudo systemctl restart noobz-bot

# Check status
sudo systemctl status noobz-bot

# View logs (follow)
sudo journalctl -u noobz-bot -f

# View logs (last 100 lines)
sudo journalctl -u noobz-bot -n 100

# Update from GitHub
cd ~/noobz-bot && git pull

# Restart after update
sudo systemctl restart noobz-bot
```

---

## 💡 Pro Tips

1. **Always use virtual environment** - Isolate dependencies
2. **Use systemd for production** - Auto-restart, logging, boot startup
3. **Regular backups** - Backup .env dan session files
4. **Monitor logs** - Check regularly untuk errors
5. **Test before production** - Use screen untuk testing dulu
6. **Keep updated** - `git pull` regularly untuk updates
7. **Use Gemini 2.0 Flash** - Default model is fastest & best for this bot
8. **Check model in logs** - Verify correct model is loaded on startup

---

## 🆘 Need Help?

Check logs untuk detailed error messages:
```bash
# Systemd logs
sudo journalctl -u noobz-bot -n 200 --no-pager

# File logs
cat ~/noobz-bot/bot.log

# Python errors
cd ~/noobz-bot
source venv/bin/activate
python main.py  # Run directly untuk lihat errors
```

---

## ✅ Deployment Checklist

- [ ] VPS ready dengan SSH access
- [ ] Python 3.9+ installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured dengan credentials
- [ ] **Gemini model configured** (default: gemini-2.0-flash-exp)
- [ ] First authentication done (session created)
- [ ] Bot tested manually (python main.py)
- [ ] **Model verified in logs** (check "Using model: ..." message)
- [ ] Systemd service created & enabled
- [ ] Bot running as service
- [ ] Logs checked (no errors)
- [ ] **Gemini model working** (test /announce command)
- [ ] Commands tested in Telegram
- [ ] Firewall configured (if needed)
- [ ] Backup created (.env & session files)

---

## 🎯 Quick Reference Card

### Essential Commands:
```bash
# Start/Stop/Restart
sudo systemctl start noobz-bot
sudo systemctl stop noobz-bot
sudo systemctl restart noobz-bot

# Check status & logs
sudo systemctl status noobz-bot
sudo journalctl -u noobz-bot -f

# Update from GitHub
cd ~/noobz-bot && git pull && sudo systemctl restart noobz-bot
```

### Model Configuration:
```bash
# Edit model
nano ~/noobz-bot/.env
# Change: GEMINI_MODEL=gemini-2.0-flash-exp

# Available models:
# gemini-2.0-flash-exp (1500 RPM, fastest) ⭐ DEFAULT
# gemini-1.5-flash (1000 RPM, stable)
# gemini-1.5-pro (360 RPM, best quality)
```

### Important Files:
```
~/noobz-bot/.env           - Your credentials ⚠️ BACKUP THIS!
~/noobz-bot/*.session      - Telegram session ⚠️ BACKUP THIS!
~/noobz-bot/bot.log        - Application logs
/etc/systemd/system/noobz-bot.service - Service file
```

### API Keys:
- **Telegram:** https://my.telegram.org/apps
- **Gemini AI:** https://makersuite.google.com/app/apikey
- **TMDB:** https://www.themoviedb.org/settings/api

### Documentation:
- **Setup Guide:** [SETUP.md](SETUP.md)
- **Gemini Models:** [GEMINI_MODELS.md](GEMINI_MODELS.md)
- **Main README:** [README.md](README.md)

---

**Bot kamu siap production di VPS! 🎉**
