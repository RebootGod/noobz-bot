# Quick Start Guide - Account Setup

Ada **3 cara** untuk setup Telegram accounts:

## 🚀 Option 1: Setup Wizard (RECOMMENDED)

Setup semua accounts sekaligus dengan wizard interaktif:

```bash
python setup_accounts.py
```

**Wizard akan:**
- ✅ Detect existing sessions
- ✅ Tanya apakah mau hapus dan start fresh
- ✅ Setup primary account step-by-step
- ✅ Optional: Setup secondary account untuk multi-account support
- ✅ Show summary dan next steps

**Perfect untuk:**
- First time setup
- Reset semua accounts
- Guided step-by-step process

---

## 📱 Option 2: Setup Individual Accounts

### Setup Primary Account Only

```bash
python setup_primary_account.py
```

Untuk login account utama (yang akan dipakai bot).

### Setup Secondary Account Only

```bash
python setup_secondary_account.py
```

Untuk login account backup (auto-switch saat flood limit).

**Perfect untuk:**
- Setup account satu-satu
- Ganti salah satu account saja
- Tambah secondary account kemudian

---

## ⚡ Option 3: Run Main Bot (Old Way)

```bash
python main.py
```

Bot akan otomatis minta login jika session belum ada.

**Note:** Cara ini hanya setup primary account. Untuk secondary account tetap perlu `setup_secondary_account.py`.

---

## 🔄 Reset & Start Fresh

Jika mau mulai dari awal (hapus semua sessions):

```bash
# Hapus session files
rm noobz_bot_session.session
rm noobz_bot_session_2.session

# Run wizard
python setup_accounts.py
```

---

## 📋 Checklist Setup

- [ ] Punya nomor Telegram untuk primary account
- [ ] Punya API credentials dari https://my.telegram.org
- [ ] (Optional) Punya nomor Telegram kedua untuk backup
- [ ] Config `.env` sudah lengkap
- [ ] Run setup script
- [ ] Session files terbuat
- [ ] Test run `python main.py`

---

## 🆘 Troubleshooting

### "The phone number is invalid"
Format harus: `+62xxx` (dengan + dan country code, tanpa spasi)

### "SessionPasswordNeededError"
Account punya 2FA enabled. Masukkan password 2FA saat diminta.

### Script stuck atau error
Press `Ctrl+C` untuk cancel, hapus session files, dan coba lagi.

### Wrong account logged in
Hapus session files dan setup ulang dengan nomor yang benar.

---

## 📖 Full Documentation

Untuk dokumentasi lengkap, lihat:
- [MULTI_ACCOUNT_SETUP.md](MULTI_ACCOUNT_SETUP.md) - Multi-account guide lengkap
- [SETUP.md](SETUP.md) - General setup guide
- [README.md](README.md) - Project overview
