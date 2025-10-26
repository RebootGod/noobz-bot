# Official Bot Testing Guide

## 📋 Pre-Testing Checklist

### 1. VPS Deployment (dilakukan dulu)
```bash
# 1. Login ke VPS
ssh user@your-vps-ip

# 2. Clone repository
cd /home/noobz
git clone https://github.com/RebootGod/noobz-bot.git
cd noobz-bot

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r official_bot/requirements.txt

# 5. Configure environment
cd official_bot
cp .env.example .env
nano .env
```

### 2. Configure .env File

Isi dengan data berikut:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=7999999999:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# ^ Dari @BotFather setelah /newbot

# Noobz API Configuration
NOOBZ_API_URL=https://noobz.space
NOOBZ_BOT_TOKEN=your_bot_api_token_from_laravel
# ^ Token khusus untuk bot (buat di Laravel backend)

# TMDB Configuration
TMDB_API_KEY=your_tmdb_api_key
# ^ Dari https://www.themoviedb.org/settings/api

# Database Configuration
DATABASE_PATH=bot_secure.db

# Security Configuration
SESSION_EXPIRY_HOURS=24
PASSWORD_MIN_LENGTH=8
BCRYPT_ROUNDS=12

# Master Password (auto-created on first run)
INITIAL_MASTER_PASSWORD=YourSecureMasterPassword123!
# ^ CHANGE THIS! Password untuk master access

# Bulk Upload Configuration
MAX_BULK_EPISODES=20

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Development
DEBUG=False
```

### 3. Create Bot Token (jika belum ada)

1. Open Telegram, cari **@BotFather**
2. Send command: `/newbot`
3. Ikuti instruksi:
   - Bot name: `Noobz Official Upload Bot`
   - Bot username: `noobz_upload_bot` (atau nama lain yang available)
4. Copy token yang diberikan ke `TELEGRAM_BOT_TOKEN`

### 4. Start Bot

```bash
# Dari directory official_bot/
python main.py
```

**Expected Output:**
```
========================================
🚀 Starting Noobz Official Bot
========================================
Bot Token: 7999999999:AAH...
API URL: https://noobz.space
Database: bot_secure.db
Initializing database...
✅ Database initialized successfully
Initializing services...
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

---

## 🧪 Testing Flows

### Test 1: Authentication Flow ✅

**1.1 First Time User (Master Login)**

1. Open Telegram, cari bot: `@noobz_upload_bot`
2. Send command: `/start`

**Expected:**
```
🎬 Noobz Upload Bot

Welcome! This bot helps you upload movies and series.

🔒 Authentication Required
━━━━━━━━━━━━━━━━━━━━━━━━

Please enter your password:
```

3. Enter password: `YourSecureMasterPassword123!` (dari INITIAL_MASTER_PASSWORD)

**Expected:**
```
✅ Authentication successful!
Welcome back, Master!

Your session will expire in 24 hours.

[🎥 Upload Movie]  [📺 Upload Series]
[📊 My Stats]      [🔐 Password Manager]
[❓ Help]
```

**✅ Pass Criteria:**
- Bot responds ke /start
- Password prompt muncul
- Login berhasil dengan master password
- Main menu tampil dengan 5 buttons (termasuk Password Manager)

**❌ Fail Cases:**
- Bot tidak respond
- Password tidak diterima
- Error saat create session
- Password Manager button tidak muncul (harusnya muncul untuk Master)

---

**1.2 Wrong Password**

1. Logout: Click [🏠 Main Menu] → Wait for session expired atau restart bot
2. Send `/start`
3. Enter wrong password: `wrongpassword123`

**Expected:**
```
❌ Invalid password. Please try again.

[🔄 Retry]  [❌ Cancel]
```

4. Click [🔄 Retry]

**Expected:**
```
🔒 Authentication

Please enter your password:
```

**✅ Pass Criteria:**
- Wrong password rejected
- Retry button works
- User dapat login ulang

---

**1.3 Session Management**

1. After login, close Telegram
2. Open Telegram lagi, click bot
3. Click any button (e.g., [📊 My Stats])

**Expected:**
```
📊 Upload Statistics

Total Uploads: 0

By Type:
🎬 Movies: 0
📺 Series: 0
📹 Episodes: 0

No uploads yet.

[🏠 Main Menu]
```

**✅ Pass Criteria:**
- Session persistent (tidak perlu login lagi)
- Button works without re-authentication
- Session berlangsung 24 jam

---

### Test 2: Movie Upload Flow 🎥

**2.1 Complete Movie Upload**

1. From main menu, click [🎥 Upload Movie]

**Expected:**
```
┌─────────────────────────────────┐
│ 🎥 Upload Movie                 │
│                                 │
│ TMDB ID: [Not Set]              │
│ Embed URL: [Not Set]            │
│ Download URL: [Optional]        │
│                                 │
│ Status: ❌ Incomplete           │
└─────────────────────────────────┘

[📝 Set TMDB ID]  [🔗 Set Embed URL]
[📥 Set Download URL]  [❌ Cancel]
```

2. Click [📝 Set TMDB ID]

**Expected:**
```
📝 Set TMDB ID

Please enter TMDB ID:

Example: 550 (for Fight Club)

You can find TMDB ID from:
https://www.themoviedb.org/

[❌ Cancel]
```

3. Send: `550` (Fight Club)

**Expected:**
```
✅ TMDB ID set
Fetching movie info...

🎬 Fight Club (1999)
⭐ 8.4/10
📝 A ticking-time-bomb insomniac and a slippery soap salesman...

┌─────────────────────────────────┐
│ 🎥 Upload Movie                 │
│                                 │
│ TMDB ID: ✅ 550                 │
│ Title: Fight Club (1999)        │
│ Embed URL: [Not Set]            │
│ Download URL: [Optional]        │
│                                 │
│ Status: ⚠️ Pending              │
└─────────────────────────────────┘

[🔗 Set Embed URL]  [📥 Set Download URL]
[❌ Cancel]
```

4. Click [🔗 Set Embed URL]

**Expected:**
```
🔗 Set Embed URL

Please enter Embed URL:

Example: https://vidsrc.to/embed/movie/550

[❌ Cancel]
```

5. Send: `https://vidsrc.to/embed/movie/550`

**Expected:**
```
✅ Embed URL set

┌─────────────────────────────────┐
│ 🎥 Upload Movie                 │
│                                 │
│ TMDB ID: ✅ 550                 │
│ Title: Fight Club (1999)        │
│ Embed URL: ✅ Set               │
│ Download URL: [Optional]        │
│                                 │
│ Status: ✅ Ready                │
└─────────────────────────────────┘

[📥 Set Download URL]  [✅ Upload Now]
[❌ Cancel]
```

6. Click [✅ Upload Now]

**Expected:**
```
⏳ Uploading...

(wait...)

✅ Movie uploaded successfully!

🎬 Fight Club (1999)
🆔 TMDB ID: 550
🔗 Embed: vidsrc.to/embed/movie/550
⏳ Status: Processing...

The movie will be published automatically.

[📤 Upload Another Movie]  [🏠 Main Menu]
```

**✅ Pass Criteria:**
- Form-style UI works
- TMDB fetch berhasil
- Upload ke Laravel API berhasil
- Success message tampil

**❌ Fail Cases:**
- TMDB fetch gagal
- Invalid URL format tidak di-reject
- Upload API error
- Duplicate tidak terdeteksi

---

**2.2 Test Duplicate Detection**

1. Upload movie yang sama (TMDB ID: 550)
2. Fill form completely
3. Click [✅ Upload Now]

**Expected:**
```
⚠️ Movie already exists!

🎬 Fight Club (1999) already exists in the database.

[📤 Upload Another Movie]  [🏠 Main Menu]
```

**✅ Pass Criteria:**
- Duplicate terdeteksi
- User diberi tahu movie sudah ada
- Tidak membuat duplicate entry

---

**2.3 Test Optional Download URL**

1. Start new movie upload
2. Set TMDB ID: `238` (The Godfather)
3. Set Embed URL: `https://vidsrc.to/embed/movie/238`
4. Skip download URL (click [✅ Upload Now] without setting download)

**Expected:**
```
✅ Movie uploaded successfully!

🎬 The Godfather (1972)
🆔 TMDB ID: 238
🔗 Embed: vidsrc.to/embed/movie/238
📥 Download: Not provided

[📤 Upload Another Movie]  [🏠 Main Menu]
```

**✅ Pass Criteria:**
- Upload berhasil tanpa download URL
- Download URL bersifat optional

---

### Test 3: Series Upload Flow 📺

**3.1 Complete Series Upload (New Series)**

1. From main menu, click [📺 Upload Series]

**Expected:**
```
┌─────────────────────────────────┐
│ 📺 Upload Series                │
│                                 │
│ TMDB ID: [Not Set]              │
│                                 │
│ Status: ❌ Incomplete           │
└─────────────────────────────────┘

[📝 Set TMDB ID]  [❌ Cancel]
```

2. Click [📝 Set TMDB ID]

**Expected:**
```
📝 Set Series TMDB ID

Please enter Series TMDB ID:

Example: 1396 (for Breaking Bad)

[❌ Cancel]
```

3. Send: `1396` (Breaking Bad)

**Expected:**
```
✅ TMDB ID set
Fetching series info...

📺 Breaking Bad (2008-2013)
⭐ 9.5/10
🔢 5 Seasons Available

Creating series in database...
✅ Series created!

┌─────────────────────────────────┐
│ 📺 Breaking Bad                 │
│ 5 Seasons • 62 Episodes         │
│                                 │
│ Select season to upload:        │
└─────────────────────────────────┘

[1️⃣ Season 1 (7 ep)]  [2️⃣ Season 2 (13 ep)]
[3️⃣ Season 3 (13 ep)] [4️⃣ Season 4 (13 ep)]
[5️⃣ Season 5 (16 ep)] [🏠 Main Menu]
```

4. Click [1️⃣ Season 1 (7 ep)]

**Expected:**
```
⏳ Checking episode status...
Fetching data from TMDB...

┌─────────────────────────────────┐
│ 📺 Breaking Bad - Season 1      │
│ 7 Episodes                      │
│                                 │
│ Status:                         │
│ ❌ E01 - Pilot                  │
│ ❌ E02 - Cat's in the Bag...    │
│ ❌ E03 - ...And the Bag's in... │
│ ❌ E04 - Cancer Man             │
│ ❌ E05 - Gray Matter            │
│ ❌ E06 - Crazy Handful of...    │
│ ❌ E07 - A No-Rough-Stuff...    │
│                                 │
│ Progress: 0/7 complete          │
└─────────────────────────────────┘

Upload mode:
[📦 Bulk Upload]  [🔄 Refresh Status]
[🔙 Back]
```

5. Click [📦 Bulk Upload]

**Expected:**
```
┌─────────────────────────────────┐
│ 📦 Bulk Episode Upload          │
│                                 │
│ Series: Breaking Bad            │
│ Season: 1                       │
│ Episodes to upload: 7           │
│                                 │
│ Format (one per line):          │
│ EP | EMBED_URL | DL_URL         │
│                                 │
│ Use "-" for no download URL     │
└─────────────────────────────────┘

Example:
1 | https://vidsrc.to/embed/tv/1396/1/1 | -
2 | https://vidsrc.to/embed/tv/1396/1/2 | -

[❌ Cancel]
```

6. Send bulk data (paste):
```
1 | https://vidsrc.to/embed/tv/1396/1/1 | -
2 | https://vidsrc.to/embed/tv/1396/1/2 | -
3 | https://vidsrc.to/embed/tv/1396/1/3 | -
```

**Expected:**
```
📊 Validating...
✅ 3 episodes valid
⚠️ 0 errors

Preview:
- E01: Pilot (New)
- E02: Cat's in the Bag... (New)
- E03: ...And the Bag's in the River (New)

[✅ Upload 3 Episodes]  [❌ Cancel]
```

7. Click [✅ Upload 3 Episodes]

**Expected:**
```
⏳ Uploading episodes...
▓▓▓░░░ 33% (1/3)

✅ E01 created
⏳ Uploading...
▓▓▓▓▓░ 66% (2/3)

✅ E02 created
⏳ Uploading...
▓▓▓▓▓▓ 100% (3/3)

✅ E03 created

━━━━━━━━━━━━━━━━━━━━━━━━
📈 Upload Summary:
✅ Success: 3 episodes
❌ Failed: 0 episodes
⏳ Processing in background...

Episodes will be published automatically.

Continue?
[📤 Upload More]  [🔄 Change Season]
[🏠 Main Menu]
```

**✅ Pass Criteria:**
- Series creation berhasil
- Season selection works
- Episode status checking works
- Bulk upload parsing berhasil
- Progress bar tampil
- Episodes uploaded successfully

---

**3.2 Test Episode Status Update (Existing Series)**

1. Click [📺 Upload Series]
2. Enter TMDB ID: `1396` (Breaking Bad - sudah ada)

**Expected:**
```
⚠️ Series already exists!

📺 Breaking Bad (2008-2013)
⭐ 9.5/10

Series already in database. Select season to upload episodes.

┌─────────────────────────────────┐
│ Select season to upload:        │
└─────────────────────────────────┘

[1️⃣ Season 1 (7 ep)]  [2️⃣ Season 2 (13 ep)]
...
```

3. Click [1️⃣ Season 1 (7 ep)]

**Expected:**
```
┌─────────────────────────────────┐
│ 📺 Breaking Bad - Season 1      │
│ 7 Episodes                      │
│                                 │
│ Status:                         │
│ ✅ E01 - Pilot (Complete)       │
│ ✅ E02 - Cat's in... (Complete) │
│ ✅ E03 - ...And the... (Complete)│
│ ❌ E04 - Cancer Man             │
│ ❌ E05 - Gray Matter            │
│ ❌ E06 - Crazy Handful of...    │
│ ❌ E07 - A No-Rough-Stuff...    │
│                                 │
│ Progress: 3/7 complete          │
└─────────────────────────────────┘

Upload mode:
[📦 Bulk Upload]  [🔄 Refresh Status]
[🔙 Back]
```

**✅ Pass Criteria:**
- Episodes yang sudah ada ditandai dengan ✅
- Episodes yang belum ada ditandai dengan ❌
- Progress bar akurat

---

**3.3 Test Episode URL Update**

1. Create episode without URLs (via Laravel backend directly)
2. Check status via bot

**Expected:**
```
│ Status:                         │
│ ✅ E01 - Pilot (Complete)       │
│ ⚠️ E02 - Cat's in... (No URLs)  │ ← Episode exists but no URLs
│ ❌ E03 - ...And the Bag's...    │
```

3. Upload E02 dengan bulk upload:
```
2 | https://vidsrc.to/embed/tv/1396/1/2 | -
```

**Expected:**
```
Preview:
- E02: Cat's in the Bag... (Update)  ← Marked as Update

[✅ Upload 1 Episode]  [❌ Cancel]
```

4. Confirm upload

**Expected:**
```
✅ E02 updated

━━━━━━━━━━━━━━━━━━━━━━━━
📈 Upload Summary:
✅ Success: 1 episode (updated)
```

**✅ Pass Criteria:**
- Episodes tanpa URLs terdeteksi dengan ⚠️
- Update episode berhasil
- Status berubah dari ⚠️ ke ✅

---

### Test 4: Password Manager (Master Only) 🔐

**4.1 Access Password Manager**

1. Login as Master
2. From main menu, click [🔐 Password Manager]

**Expected:**
```
┌─────────────────────────────────┐
│ 🔐 Password Management          │
│                                 │
│ Active Passwords: 1             │
│                                 │
│ 🔑 ****1234 (Master) - You      │
│    Created: Oct 26, 2025        │
│    Last used: Just now          │
│    Uploads: 3                   │
└─────────────────────────────────┘

[➕ Add Password]  [📊 View Stats]
[🔙 Back]
```

**✅ Pass Criteria:**
- Master dapat akses Password Manager
- Password list tampil
- Master password ditampilkan dengan hint (****1234)

---

**4.2 Create Admin Password**

1. Click [➕ Add Password]

**Expected:**
```
┌─────────────────────────────────┐
│ ➕ Create New Password           │
│                                 │
│ Password Type:                  │
└─────────────────────────────────┘

[👑 Master Password]  [👤 Admin Password]
[❌ Cancel]

⚠️ Warning: Master passwords have full access
including password management!
```

2. Click [👤 Admin Password]

**Expected:**
```
Creating Admin Password

Please enter new password:
(Min 8 characters, mix of letters & numbers)
```

3. Send: `admin123456`

**Expected:**
```
Please confirm password:
```

4. Send: `admin123456` (same password)

**Expected:**
```
Optional: Add notes
(e.g., "Password for John")

Send "-" to skip
```

5. Send: `Password for Testing`

**Expected:**
```
✅ Password Created!

Password: ****3456
Type: Admin
Created: Oct 26, 2025
Notes: Password for Testing

⚠️ Save this password securely!
It will not be shown again.

[🔙 Back to Manager]  [🏠 Main Menu]
```

6. Click [🔙 Back to Manager]

**Expected:**
```
┌─────────────────────────────────┐
│ 🔐 Password Management          │
│                                 │
│ Active Passwords: 2             │
│                                 │
│ 🔑 ****1234 (Master) - You      │
│    Created: Oct 26, 2025        │
│    Last used: Just now          │
│    Uploads: 3                   │
│                                 │
│ 🔑 ****3456 (Admin)             │
│    Created: Oct 26, 2025        │
│    Last used: Never             │
│    Uploads: 0                   │
│    Notes: Password for Testing  │
└─────────────────────────────────┘
```

**✅ Pass Criteria:**
- Admin password creation berhasil
- Password hint displayed (****3456)
- Notes tersimpan
- Password list updated

---

**4.3 Test Admin Access (No Password Manager)**

1. Logout dari Master account
2. Login dengan Admin password: `admin123456`

**Expected:**
```
✅ Authentication successful!
Welcome back!

Your session will expire in 24 hours.

[🎥 Upload Movie]  [📺 Upload Series]
[📊 My Stats]      [❓ Help]
```

**✅ Pass Criteria:**
- Admin login berhasil
- Main menu tampil TANPA [🔐 Password Manager] button
- Admin dapat upload movies/series
- Admin TIDAK dapat manage passwords

---

### Test 5: Error Handling ❌

**5.1 Invalid TMDB ID**

1. Start movie upload
2. Send TMDB ID: `999999999` (tidak valid)

**Expected:**
```
❌ Error fetching movie data

Movie not found on TMDB. Please check the ID.

[🔄 Try Again]  [❌ Cancel]
```

---

**5.2 Invalid URL Format**

1. Start movie upload
2. Set TMDB ID: `550`
3. Set Embed URL: `not-a-valid-url`

**Expected:**
```
❌ Invalid URL format

Please enter a valid URL starting with http:// or https://

Example: https://vidsrc.to/embed/movie/550

[🔄 Try Again]  [❌ Cancel]
```

---

**5.3 Bulk Upload Parse Error**

1. Start bulk episode upload
2. Send invalid format:
```
1 | wrong format
2 missing pipe
3 | url | dl | extra
```

**Expected:**
```
❌ Validation Errors:

Line 1: Invalid URL format
Line 2: Invalid format (missing separators)
Line 3: Too many fields (expected 3, got 4)

Please fix errors and try again.

[🔄 Try Again]  [❌ Cancel]
```

---

**5.4 API Connection Error**

1. Stop Laravel backend (temporary)
2. Try to upload movie

**Expected:**
```
❌ Upload Failed

Unable to connect to server. Please try again later.

Error: Connection timeout

[🔄 Retry]  [🏠 Main Menu]
```

---

### Test 6: Session & Logout 🔓

**6.1 Logout**

1. From main menu, send command: `/start`
2. Bot should show main menu (already logged in)
3. Wait or manually expire session (change DB)
4. Click any button

**Expected:**
```
⚠️ Session Expired

Your session has expired. Please login again.

[🔑 Login]
```

---

**6.2 Multiple Devices**

1. Login from Device A (Phone)
2. Login from Device B (Desktop) with same password

**Expected on Device A:**
```
⚠️ Session Terminated

Your session was terminated because you logged in from another device.

[🔑 Login Again]
```

**✅ Pass Criteria:**
- Only 1 active session per user (single session policy)
- Old session terminated saat login baru

---

## 📊 Testing Checklist Summary

### Authentication ✅
- [ ] First time login (Master)
- [ ] Wrong password rejection
- [ ] Retry authentication
- [ ] Session persistence (24h)
- [ ] Session expiry handling
- [ ] Logout functionality

### Movie Upload ✅
- [ ] Complete movie upload flow
- [ ] TMDB fetch & preview
- [ ] Optional download URL
- [ ] Duplicate detection
- [ ] Success confirmation
- [ ] Upload another movie

### Series Upload ✅
- [ ] New series creation
- [ ] Season selection
- [ ] Episode status checking (✅⚠️❌)
- [ ] Bulk episode upload (3-5 episodes)
- [ ] Bulk upload parsing
- [ ] Progress bar display
- [ ] Episode URL update (⚠️ → ✅)
- [ ] Existing series handling

### Password Manager (Master) ✅
- [ ] View password list
- [ ] Create Admin password
- [ ] Password confirmation
- [ ] Optional notes
- [ ] Password hint display
- [ ] Admin login (no manager access)
- [ ] Master-only access control

### Error Handling ✅
- [ ] Invalid TMDB ID
- [ ] Invalid URL format
- [ ] Bulk upload parse errors
- [ ] API connection errors
- [ ] Duplicate content handling

### Session Management ✅
- [ ] Session persistence
- [ ] Session expiry (24h)
- [ ] Single session policy
- [ ] Multi-device handling

---

## 🐛 Bug Report Template

Jika menemukan bug, report dengan format ini:

```markdown
**Bug Title:** [Short description]

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happened]

**Screenshots/Logs:**
[Include if available]

**Environment:**
- Bot version: [commit hash]
- Python version: [3.x.x]
- OS: [Ubuntu/Debian]

**Priority:** [High/Medium/Low]
```

---

## 📝 Testing Notes

### Important Files to Monitor

1. **Bot Logs:**
```bash
# View live logs
tail -f official_bot/bot.log

# View errors only
grep ERROR official_bot/bot.log
```

2. **Database:**
```bash
# Check database
sqlite3 official_bot/bot_secure.db

# Useful queries
SELECT * FROM passwords;
SELECT * FROM sessions;
SELECT * FROM upload_logs ORDER BY created_at DESC LIMIT 10;
```

3. **System Logs:**
```bash
# If using systemd
sudo journalctl -u noobz-bot -f
```

### Performance Metrics

Monitor:
- Response time (should be < 2 seconds for most operations)
- TMDB API calls (avoid rate limit 40 req/10sec)
- Laravel API response time
- Database query performance
- Memory usage

### Security Checks

- [ ] .env file chmod 600
- [ ] bot_secure.db chmod 600
- [ ] No sensitive data in logs
- [ ] Password messages deleted after input
- [ ] Session tokens secure
- [ ] HTTPS enforced for API calls

---

## ✅ Test Completion

Setelah semua testing selesai, konfirmasikan:

- [ ] All authentication flows work
- [ ] Movie uploads successful
- [ ] Series uploads with bulk episodes work
- [ ] Password manager functional (Master only)
- [ ] Error handling graceful
- [ ] Session management correct
- [ ] No security vulnerabilities found
- [ ] Performance acceptable
- [ ] Logs comprehensive and useful

**Status:** `[ ] READY FOR PRODUCTION` or `[ ] NEEDS FIXES`

**Date Tested:** _______________

**Tested By:** _______________

**Notes:** _____________________________________
