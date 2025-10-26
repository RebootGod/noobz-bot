# Noobz Official Bot - Systemd Service Setup

## 📋 Prerequisites

- Bot files in `/root/noobz-bot/official_bot/`
- Python virtual environment in `/root/noobz-bot/venv/`
- `.env` file configured with credentials

## 🚀 Installation Steps

### 1. Copy Service File

```bash
sudo cp /root/noobz-bot/official_bot/noobz-official-bot.service /etc/systemd/system/
```

### 2. Reload Systemd

```bash
sudo systemctl daemon-reload
```

### 3. Enable Auto-Start on Boot

```bash
sudo systemctl enable noobz-official-bot
```

### 4. Start the Bot

```bash
sudo systemctl start noobz-official-bot
```

## 🎛️ Managing the Service

### Check Status
```bash
sudo systemctl status noobz-official-bot
```

### Start Bot
```bash
sudo systemctl start noobz-official-bot
```

### Stop Bot
```bash
sudo systemctl stop noobz-official-bot
```

### Restart Bot
```bash
sudo systemctl restart noobz-official-bot
```

### View Logs (Real-time)
```bash
sudo journalctl -u noobz-official-bot -f
```

### View Last 100 Lines
```bash
sudo journalctl -u noobz-official-bot -n 100
```

### View Logs Since Today
```bash
sudo journalctl -u noobz-official-bot --since today
```

## 🔄 Update & Deploy Workflow

### Quick Update (Like Existing Userbot)

```bash
cd /root/noobz-bot
git pull origin main
sudo systemctl restart noobz-official-bot
```

### Full Update with Dependencies

```bash
cd /root/noobz-bot
git pull origin main
source venv/bin/activate
pip install -r official_bot/requirements.txt
deactivate
sudo systemctl restart noobz-official-bot
```

### Check if Update Successful

```bash
sudo systemctl status noobz-official-bot
# Should show "active (running)"

sudo journalctl -u noobz-official-bot -n 50
# Should show "✅ Bot started successfully!"
```

## 🛠️ Troubleshooting

### Bot Not Starting

1. **Check service status:**
```bash
sudo systemctl status noobz-official-bot
```

2. **View error logs:**
```bash
sudo journalctl -u noobz-official-bot -n 100 --no-pager
```

3. **Check .env file:**
```bash
cat /root/noobz-bot/official_bot/.env
# Make sure all variables are set
```

4. **Test manual run:**
```bash
cd /root/noobz-bot
source venv/bin/activate
cd official_bot
python3 main.py
# See errors directly
```

### Permission Issues

```bash
sudo chown -R root:root /root/noobz-bot/
sudo chmod 600 /root/noobz-bot/official_bot/.env
sudo chmod 644 /root/noobz-bot/official_bot/bot_secure.db
```

### Service Won't Restart

```bash
# Force kill and restart
sudo systemctl stop noobz-official-bot
sudo pkill -f "python3.*main.py"
sudo systemctl start noobz-official-bot
```

## 📊 Monitoring

### Auto-Restart on Crash

Service is configured with `Restart=always` and `RestartSec=10`. Bot will automatically restart if it crashes.

### Check Uptime

```bash
sudo systemctl status noobz-official-bot | grep "Active:"
```

### Monitor Resource Usage

```bash
ps aux | grep main.py
```

## 🔐 Security Notes

- Service runs as `root` user (same as existing userbot)
- `.env` file should have 600 permissions (owner read/write only)
- Database file `bot_secure.db` is gitignored
- Logs are stored in systemd journal (not plain text files)

## 📝 Service Configuration

**File Location:** `/etc/systemd/system/noobz-official-bot.service`

**Key Settings:**
- `Restart=always` - Auto-restart on crash
- `RestartSec=10` - Wait 10 seconds before restart
- `WorkingDirectory=/root/noobz-bot/official_bot` - Bot working directory
- `Environment="PATH=..."` - Uses virtual environment Python

## 🆚 Comparison with Existing Userbot

| Feature | Userbot (noobz-bot) | Official Bot (noobz-official-bot) |
|---------|---------------------|-----------------------------------|
| Service Name | `noobz-bot.service` | `noobz-official-bot.service` |
| Start Command | `systemctl restart noobz-bot` | `systemctl restart noobz-official-bot` |
| Logs Command | `journalctl -u noobz-bot -f` | `journalctl -u noobz-official-bot -f` |
| Working Dir | `/root/noobz-bot` | `/root/noobz-bot/official_bot` |
| Main File | Userbot main file | `main.py` |
| Update | `git pull && systemctl restart` | `git pull && systemctl restart` |

## ✅ Verification Checklist

After setup, verify:

- [ ] Service file copied to `/etc/systemd/system/`
- [ ] Systemd reloaded with `daemon-reload`
- [ ] Service enabled with `enable`
- [ ] Service started with `start`
- [ ] Status shows "active (running)"
- [ ] Logs show "✅ Bot started successfully!"
- [ ] Bot responds to `/start` command in Telegram
- [ ] Auto-restart works (test with `systemctl stop` then check if auto-restart)

## 🎯 Quick Commands Cheat Sheet

```bash
# Update & restart (most common)
cd /root/noobz-bot && git pull && systemctl restart noobz-official-bot

# Check status
systemctl status noobz-official-bot

# View logs
journalctl -u noobz-official-bot -f

# Stop/Start/Restart
systemctl stop noobz-official-bot
systemctl start noobz-official-bot
systemctl restart noobz-official-bot

# Check if enabled on boot
systemctl is-enabled noobz-official-bot
```

---

**Made with ❤️ for Noobz Cinema**
