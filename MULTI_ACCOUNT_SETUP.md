# Multi-Account Setup Guide

Bot ini mendukung **multiple Telegram accounts** untuk menghindari flood limit. Ketika account pertama kena rate limit, bot akan otomatis switch ke account kedua.

## 🎯 Kenapa Perlu Multiple Accounts?

Telegram membatasi jumlah pesan yang bisa dikirim ke user lain dalam waktu tertentu (flood limit). Dengan multiple accounts:
- ✅ Bot tetap bisa kirim messages meskipun satu account kena limit
- ✅ Auto-switch antar accounts secara otomatis
- ✅ Cooldown tracking untuk setiap account

## 📋 Prerequisites

1. **Primary Account** - Sudah setup (account utama)
2. **Secondary Account** - Siapkan nomor Telegram kedua untuk backup

## 🚀 Setup Secondary Account

### Step 1: Tambah Configuration

Edit file `.env` dan tambahkan config untuk account kedua:

```bash
# Primary Account (sudah ada)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef123456
TELEGRAM_PHONE=+628123456789

# Secondary Account (tambahkan ini)
TELEGRAM_API_ID_2=87654321
TELEGRAM_API_HASH_2=654321fedcba
TELEGRAM_PHONE_2=+628987654321
```

**Note:**
- `TELEGRAM_API_ID_2` dan `TELEGRAM_API_HASH_2` bisa **sama** dengan primary account (menggunakan same API credentials)
- `TELEGRAM_PHONE_2` **harus berbeda** - nomor Telegram kedua untuk backup

### Step 2: Get API Credentials (jika belum punya)

Jika kamu belum punya API credentials untuk account kedua:

1. Buka https://my.telegram.org
2. Login dengan nomor Telegram **kedua** (TELEGRAM_PHONE_2)
3. Klik "API Development Tools"
4. Isi form app (nama bebas)
5. Copy `api_id` dan `api_hash`

**ATAU** gunakan credentials yang sama dengan primary account.

### Step 3: Run Setup Script

Jalankan script setup untuk login account kedua:

```bash
# On Windows
python setup_secondary_account.py

# On Linux/VPS
python3 setup_secondary_account.py
```

Script akan:
1. ✅ Check apakah config sudah lengkap
2. ✅ Connect ke Telegram API
3. ✅ Minta kode verifikasi (dikirim ke Telegram app)
4. ✅ Minta 2FA password (jika enabled)
5. ✅ Buat session file untuk account kedua

**Output:**
```
============================================================
SETUP SECONDARY TELEGRAM ACCOUNT
============================================================
Phone number: +628987654321

Please enter the code you received: 12345

✅ SUCCESS!
============================================================
Logged in as: John Doe
Username: @johndoe
Phone: +628987654321
Session file: noobz_bot_session_2.session
============================================================
```

### Step 4: Verify Setup

Check apakah session file berhasil dibuat:

```bash
# Harus ada 2 session files
ls *.session

# Output:
noobz_bot_session.session      # Primary account
noobz_bot_session_2.session    # Secondary account
```

### Step 5: Run Bot

Jalankan bot seperti biasa:

```bash
python main.py
```

Bot akan otomatis initialize **kedua accounts** dan siap switch otomatis saat flood limit terdeteksi.

## 🔄 Cara Kerja Auto-Switch

```
┌─────────────────────────────────────┐
│  Bot sends message via Account 1    │
└───────────────┬─────────────────────┘
                │
        ┌───────▼────────┐
        │ FloodWaitError? │
        └───────┬────────┘
         Yes    │    No
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
┌────────────────┐    ┌──────────────┐
│ Mark Account 1  │    │  Success ✅  │
│ as LIMITED      │    └──────────────┘
│ Cooldown: 30s   │
└────────┬────────┘
         │
         ▼
┌────────────────┐
│ Auto-switch to │
│ Account 2      │
└────────┬────────┘
         │
         ▼
┌────────────────┐
│ Retry send     │
│ via Account 2  │
└────────┬────────┘
         │
         ▼
    ┌──────────┐
    │Success ✅│
    └──────────┘
```

## 📊 Monitor Account Status

Saat bot running, log akan menunjukkan:

```log
INFO - Multi-Account Manager initialized with 2 account(s)
INFO - ✅ Primary account initialized: +628123456789
INFO - ✅ Secondary account initialized: +628987654321

# Saat flood limit detected:
WARNING - FloodWaitError on account 1: Need to wait 30 seconds
INFO - Switching to account 2
INFO - Message sent successfully using account 2
```

## ⚙️ Configuration Options

### Optional: Hanya Gunakan Primary Account

Jika tidak ingin menggunakan multiple accounts, **jangan tambahkan** config `TELEGRAM_*_2` di `.env`. Bot akan work normal dengan single account.

### Optional: Tambah Lebih Banyak Accounts

Saat ini bot support **2 accounts**. Jika perlu lebih banyak, bisa extend `MultiAccountManager`.

## 🐛 Troubleshooting

### Error: "Secondary account not configured"

**Solution:** Pastikan sudah tambah `TELEGRAM_API_ID_2`, `TELEGRAM_API_HASH_2`, dan `TELEGRAM_PHONE_2` di `.env`.

### Error: "The phone number is invalid"

**Solution:** Pastikan format nomor: `+628xxx` (dengan `+` dan country code, tanpa spasi).

### Error: "SessionPasswordNeededError"

**Solution:** Account kedua punya 2FA enabled. Masukkan password 2FA saat diminta.

### Session File Tidak Terbuat

**Solution:**
1. Check permissions folder (harus bisa write)
2. Run script dengan sudo (Linux): `sudo python3 setup_secondary_account.py`
3. Check apakah ada error di log

## 📝 Notes

- **Session files** disimpan di root folder project (`.session` files)
- **Jangan share** session files ke orang lain (berisi auth token)
- **Backup** session files jika pindah server
- Jika ganti phone number, hapus old session dan setup ulang

## 🔐 Security

- Session files berisi encrypted auth tokens
- Jangan commit session files ke git (sudah di `.gitignore`)
- Jangan share API credentials
- Gunakan 2FA untuk kedua accounts

## ✅ Checklist Setup

- [ ] Punya 2 nomor Telegram
- [ ] Primary account sudah login dan work
- [ ] Tambah config `TELEGRAM_*_2` di `.env`
- [ ] Run `setup_secondary_account.py`
- [ ] Verify session file terbuat
- [ ] Test run `main.py`
- [ ] Check log: "Multi-Account Manager initialized with 2 account(s)"

Done! 🎉
