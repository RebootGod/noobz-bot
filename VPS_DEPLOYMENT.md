# VPS Deployment Guide - Noobz Bot

## 🚀 Setup di VPS Linux (Ubuntu/Debian)

### Prerequisites
- VPS dengan Ubuntu 20.04+ atau Debian 10+
- SSH access ke VPS
- Python 3.9+ (recommended 3.11)
- Internet connection

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
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+62xxxxxxxxxxxxx

GEMINI_API_KEY=your_gemini_api_key_here
TMDB_API_KEY=your_tmdb_api_key_here

WEBSITE_URL=https://noobz.space
BOT_NAME=Noobz Announcement Bot
DEBUG=False
```

**Save dan exit:**
- Nano: `Ctrl+X`, tekan `Y`, tekan `Enter`
- Vim: tekan `Esc`, ketik `:wq`, tekan `Enter`

### 7. First Run & Authentication

```bash
# Activate venv jika belum
source venv/bin/activate

# Run bot
python main.py
```

**First time setup:**
1. Bot akan minta verification code
2. Check Telegram app di phone kamu
3. Copy code dan paste ke terminal
4. Jika ada 2FA, masukkan password
5. Session file akan dibuat otomatis
6. Bot akan running!

**Test:** Kirim command di Saved Messages Telegram kamu

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
- [ ] First authentication done (session created)
- [ ] Bot tested manually (python main.py)
- [ ] Systemd service created & enabled
- [ ] Bot running as service
- [ ] Logs checked (no errors)
- [ ] Commands tested in Telegram
- [ ] Firewall configured (if needed)
- [ ] Backup created (.env & session files)

---

**Bot kamu siap production di VPS! 🎉**
