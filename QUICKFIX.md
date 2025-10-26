# Quick Fix Guide - Production Deployment

## 🔧 Fixes Applied (Oct 26, 2025)

### Fix 1: Missing `setup_logger` Function
**Error:**
```
ImportError: cannot import name 'setup_logger' from 'utils.logger'
```

**Solution:**
Added `setup_logger()` function to `utils/logger.py` for compatibility with service imports.

**Commit:** `6fb8ead`

---

### Fix 2: Missing Parameters in Service Initialization
**Error:**
```
TypeError: __init__() missing 1 required positional argument: 'settings'
```

**Solution:**
Updated `main.py` to pass `Settings` class to `TmdbService()` and `NoobzApiService()` constructors.

**Commit:** `7596dce`

---

## 🚀 Deployment Update Commands

If bot is already running on VPS, update with:

```bash
# Navigate to bot directory
cd /root/noobz-bot

# Pull latest fixes
git pull origin main

# Restart bot
# If running manually:
# Press Ctrl+C to stop, then:
python official_bot/main.py

# If using systemd:
sudo systemctl restart noobz-bot
```

---

## ✅ Verification

After update, you should see:

```
========================================
🚀 Starting Noobz Official Bot
========================================
08:59:26 | INFO     | official_bot | 🤖 Official Bot Logger Initialized
Bot Token: 7999999999:AAH...
API URL: https://noobz.space
Database: bot_secure.db
Initializing database...
✅ Database initialized successfully
Initializing services...
INFO     | __main__ | NoobzApiService initialized
INFO     | official_bot | All services initialized successfully
✅ All services initialized successfully
Checking master password...
✅ Master password created successfully
Password hint: ****1234
Creating Telegram application...
Registering handlers...
✅ All handlers registered
========================================
✅ Bot started successfully!
Polling for updates...
========================================
```

**No more import errors!** ✅

---

## 🐛 If You Still Get Errors

### Error: Module not found

```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r official_bot/requirements.txt
```

### Error: Permission denied (database)

```bash
# Fix database permissions
chmod 600 official_bot/bot_secure.db
```

### Error: Invalid token

```bash
# Check .env file
cd official_bot
nano .env

# Verify these are set:
# TELEGRAM_BOT_TOKEN=...
# NOOBZ_BOT_TOKEN=...
# TMDB_API_KEY=...
```

---

## 📝 Next Steps

Once bot starts successfully:
1. Send `/start` to bot in Telegram
2. Enter master password (from `INITIAL_MASTER_PASSWORD` in .env)
3. Follow **TESTING_GUIDE.md** for comprehensive testing

---

**Last Updated:** Oct 26, 2025
**Status:** ✅ Ready for Production Testing
