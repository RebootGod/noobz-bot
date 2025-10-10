# Common Setup Issues & Solutions

## 🚨 Error: "The phone number is invalid"

### Problem:
```
ERROR - Authorization failed: The phone number is invalid (caused by SendCodeRequest)
```

### Solution:

#### ✅ **Correct Phone Format:**

```env
# ❌ WRONG - These will cause errors:
TELEGRAM_PHONE=62812345678900      # Missing +
TELEGRAM_PHONE=0812345678900       # Missing country code
TELEGRAM_PHONE=+62 812 3456 7890   # Has spaces
TELEGRAM_PHONE=+62-812-3456-7890   # Has dashes

# ✅ CORRECT - Use this format:
TELEGRAM_PHONE=+62812345678900
```

#### **Rules:**
1. ✅ **MUST start with `+`**
2. ✅ **Include country code** (62 for Indonesia)
3. ✅ **NO spaces, NO dashes**
4. ✅ **Remove leading 0** from your number

#### **Examples by Country:**

```env
# Indonesia: 0812-3456-7890 becomes:
TELEGRAM_PHONE=+62812345678900

# USA: (202) 555-1234 becomes:
TELEGRAM_PHONE=+12025551234

# UK: 07700 900123 becomes:
TELEGRAM_PHONE=+447700900123

# Singapore: 8123 4567 becomes:
TELEGRAM_PHONE=+6581234567
```

#### **How to Find Your Correct Format:**

1. Open Telegram app
2. Go to **Settings → Edit Profile**
3. Look at your phone number (e.g., +62 812 3456 7890)
4. **Remove all spaces**: `+62812345678900`
5. Use that in `.env`

#### **Fix on VPS:**

```bash
# Edit .env file
nano ~/noobz-bot/.env

# Change TELEGRAM_PHONE line to correct format
TELEGRAM_PHONE=+62812345678900

# Save: Ctrl+X, Y, Enter

# Run bot again
python main.py
```

---

## 🚨 Error: "API key is invalid" (Gemini)

### Problem:
```
ERROR - Failed to initialize Gemini model
```

### Solutions:

#### 1. **Check API Key Format:**
```bash
# View your API key (mask for security)
cat ~/noobz-bot/.env | grep GEMINI_API_KEY

# Should be ~39 characters long
# Example format: AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 2. **Get New API Key:**
- Visit: https://makersuite.google.com/app/apikey
- Click "Create API Key"
- Copy ENTIRE key (no spaces)
- Paste in `.env`:
  ```env
  GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```

#### 3. **Verify No Extra Spaces:**
```bash
# Check for trailing spaces
nano ~/noobz-bot/.env

# Make sure no spaces after the key
# ✅ GEMINI_API_KEY=AIzaSy...
# ❌ GEMINI_API_KEY=AIzaSy... 
```

---

## 🚨 Error: "Model not found"

### Problem:
```
ERROR - Failed to initialize Gemini model: Model not found
```

### Solution:

Check model name in `.env`:

```bash
cat ~/noobz-bot/.env | grep GEMINI_MODEL
```

**Valid options ONLY:**
```env
GEMINI_MODEL=gemini-2.0-flash-exp   # ✅ Default, fastest
GEMINI_MODEL=gemini-1.5-flash       # ✅ Stable
GEMINI_MODEL=gemini-1.5-pro         # ✅ Best quality
GEMINI_MODEL=gemini-pro             # ✅ Legacy

# ❌ WRONG - These will fail:
GEMINI_MODEL=gemini-2.0-flash       # Wrong name
GEMINI_MODEL=gemini2.0              # Wrong name
GEMINI_MODEL=gpt-4                  # Wrong AI (that's OpenAI!)
```

**Fix:**
```bash
nano ~/noobz-bot/.env
# Change to: GEMINI_MODEL=gemini-2.0-flash-exp
# Save and restart
```

---

## 🚨 Error: "TMDB API error"

### Problem:
```
ERROR - Failed to fetch movie: Authentication failed
```

### Solutions:

#### 1. **Check TMDB API Key:**
```bash
cat ~/noobz-bot/.env | grep TMDB_API_KEY
```

#### 2. **Get API Key:**
- Visit: https://www.themoviedb.org/settings/api
- Login/Register (free)
- Request API key (Developer option)
- Copy **API Key (v3 auth)** (32 characters)
- NOT the "API Read Access Token"!

#### 3. **Format:**
```env
# ✅ CORRECT (32 char hexadecimal):
TMDB_API_KEY=a1b2c3d4e5f6789012345678901234ab

# ❌ WRONG (Read Access Token - too long):
TMDB_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🚨 Error: "Module not found"

### Problem:
```
ModuleNotFoundError: No module named 'telethon'
```

### Solutions:

#### 1. **Ensure Virtual Environment is Activated:**
```bash
cd ~/noobz-bot

# Activate venv
source venv/bin/activate

# You should see (venv) in prompt:
# (venv) root@server:~/noobz-bot#
```

#### 2. **Reinstall Dependencies:**
```bash
pip install -r requirements.txt
```

#### 3. **Check Python Version:**
```bash
python --version
# Should be 3.9 or higher
```

---

## 🚨 Error: "Permission denied"

### Problem:
```
PermissionError: [Errno 13] Permission denied: '.env'
```

### Solutions:

#### 1. **Fix File Permissions:**
```bash
cd ~/noobz-bot

# Fix ownership
sudo chown -R $USER:$USER .

# Fix permissions
chmod 755 .
chmod 600 .env
chmod 600 *.session
```

#### 2. **Check User:**
```bash
# Don't run as wrong user
whoami

# If using systemd, check service user matches
cat /etc/systemd/system/noobz-bot.service | grep User
```

---

## 🚨 Error: "Session expired"

### Problem:
Bot asks for login code again every time.

### Solutions:

#### 1. **Check Session File Exists:**
```bash
ls -la ~/noobz-bot/*.session
```

#### 2. **Fix Session Permissions:**
```bash
chmod 600 ~/noobz-bot/*.session
```

#### 3. **If Corrupted, Delete and Re-authenticate:**
```bash
rm ~/noobz-bot/*.session
python main.py
# Enter code again
```

---

## 🚨 Error: "Rate limit exceeded" (Gemini)

### Problem:
```
ERROR - Quota exceeded: Rate limit reached
```

### Solutions:

#### 1. **Check Current Rate Limits:**
- `gemini-2.0-flash-exp`: 1500 requests/minute (free)
- `gemini-1.5-flash`: 1000 requests/minute (free)
- `gemini-1.5-pro`: 360 requests/minute (free)

#### 2. **Wait 60 Seconds:**
Rate limits reset every minute.

#### 3. **Switch to Model with Higher Limits:**
```bash
nano ~/noobz-bot/.env

# Change to Pro (higher daily limit):
GEMINI_MODEL=gemini-1.5-pro

# Restart bot
sudo systemctl restart noobz-bot
```

#### 4. **Upgrade API Key:**
If you need more, upgrade to paid tier.

---

## 🚨 Error: "Connection timeout"

### Problem:
```
ERROR - Connection to Telegram timed out
```

### Solutions:

#### 1. **Check Internet Connection:**
```bash
ping -c 3 google.com
```

#### 2. **Check Telegram Status:**
Visit: https://telegram.org/status

#### 3. **Try Again:**
Connection issues are usually temporary.

#### 4. **Check Firewall:**
```bash
# Allow outgoing HTTPS
sudo ufw allow out 443/tcp
```

---

## 🚨 Error: "Channel not found"

### Problem:
When using `/announce Channel Name`, bot can't find channel.

### Solutions:

#### 1. **Ensure Bot Account Joined Channel:**
- Your Telegram account MUST be member of channel/group
- Bot can only send to channels you've joined

#### 2. **Check Channel Name:**
```
# Try exact name from Telegram
/announce Noobz Space Test message

# Try with different casing
/announce noobz space Test message
```

#### 3. **Use @username Instead:**
```
/announce @noobzspace Test message
```

---

## 🚨 Error: "User not found"

### Problem:
`/infofilm @username` fails to find user.

### Solutions:

#### 1. **Check Username Format:**
```
# ✅ CORRECT:
/infofilm @johndoe movie inception 2010

# ❌ WRONG:
/infofilm johndoe movie inception 2010  # Missing @
/infofilm @John Doe movie inception 2010  # Username can't have space
```

#### 2. **Verify User Has Username:**
- User must have set a username in Telegram
- First name alone won't work
- Check user's profile for @username

#### 3. **Try User ID Instead:**
You can use numeric user ID instead of username.

---

## 📝 Quick Checklist

Before running bot, verify:

```bash
# 1. Virtual environment activated
source ~/noobz-bot/venv/bin/activate

# 2. Check .env format
cat ~/noobz-bot/.env

# Verify:
# ✅ TELEGRAM_PHONE starts with +
# ✅ GEMINI_API_KEY is ~39 chars
# ✅ GEMINI_MODEL is valid option
# ✅ TMDB_API_KEY is 32 chars
# ✅ No trailing spaces

# 3. Test run
python main.py

# Should see:
# ✅ Starting Noobz Announcement Bot
# ✅ Using model: gemini-2.0-flash-exp
# ✅ Bot is running as: YourName
```

---

## 🆘 Still Having Issues?

### Check Logs:
```bash
# Application log
cat ~/noobz-bot/bot.log

# System log (if using systemd)
sudo journalctl -u noobz-bot -n 100

# Run manually for full output
cd ~/noobz-bot
source venv/bin/activate
python main.py
```

### Debug Mode:
```bash
# Enable debug in .env
nano ~/noobz-bot/.env

# Set:
DEBUG=True

# Restart and check logs
```

### Verify Settings:
```bash
# Test settings validation
cd ~/noobz-bot
source venv/bin/activate
python -c "from config.settings import get_settings; s = get_settings(); s.validate(); print('Settings OK!')"
```

---

## 📚 Related Documentation

- **Setup Guide:** [SETUP.md](SETUP.md)
- **VPS Deployment:** [VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md)
- **Gemini Models:** [GEMINI_MODELS.md](GEMINI_MODELS.md)
- **Main README:** [README.md](README.md)
