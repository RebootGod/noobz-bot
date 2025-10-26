# Official Noobz Upload Bot

Official Telegram bot for uploading movies, series, and episodes to Noobz.space platform.

## 🎯 Features

- 🔐 **Secure Authentication** - Password-based authentication with bcrypt hashing
- 👑 **Master Password** - Full access including password management
- 👤 **Admin Passwords** - Upload access without password management
- 📝 **Form-Style UI** - Modern inline button interface
- 🎬 **Movie Upload** - Upload movies with TMDB validation
- 📺 **Series Upload** - Context-aware series and episode upload
- 📦 **Bulk Upload** - Upload up to 20 episodes at once
- ✍️ **Manual Mode** - Fallback for incomplete TMDB data
- 📊 **Statistics** - Track upload history and performance
- 🔒 **Isolated Storage** - SQLite database separate from production

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     Telegram User Interface         │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│     Official Bot (Python)           │
│  ├── Authentication Layer           │
│  ├── UI Layer (Inline Buttons)     │
│  ├── Business Logic                 │
│  └── SQLite Storage                 │
└──────────────┬──────────────────────┘
               │
               ↓ (HTTP API)
┌─────────────────────────────────────┐
│     Laravel Backend (Production)    │
│  ├── Bot API Endpoints              │
│  ├── Content Upload Service         │
│  └── Production Database            │
└─────────────────────────────────────┘
```

## 📁 Project Structure

```
official_bot/
├── main.py                      # Entry point
├── bot_secure.db               # SQLite database (gitignored)
├── .env                        # Configuration (gitignored)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── config/
│   ├── settings.py            # Environment settings
│   ├── database.py            # SQLite connection
│   └── constants.py           # Constants & enums
│
├── database/
│   ├── schema.sql             # SQLite schema
│   └── models.py              # SQLAlchemy models
│
├── services/
│   ├── auth_service.py        # Password authentication
│   ├── session_service.py     # Session management
│   ├── context_service.py     # Upload context state
│   ├── tmdb_service.py        # TMDB API integration
│   ├── noobz_api_service.py   # Laravel API client
│   └── password_manager_service.py
│
├── handlers/
│   ├── start_handler.py       # /start command
│   ├── auth_handler.py        # Authentication flow
│   ├── movie_upload_handler.py
│   ├── series_upload_handler_1.py
│   ├── series_upload_handler_2.py
│   ├── episode_bulk_handler.py
│   ├── episode_manual_handler.py
│   ├── password_manager_handler.py
│   ├── stats_handler.py
│   └── help_handler.py
│
├── ui/
│   ├── keyboards.py           # Inline keyboard builders
│   ├── messages.py            # Message templates
│   └── formatters.py          # Response formatters
│
├── utils/
│   ├── validators.py          # Input validators
│   ├── parsers.py             # Message parsers
│   ├── crypto.py              # Password hashing
│   └── logger.py              # Logging setup
│
└── tests/
    ├── test_auth.py
    ├── test_upload.py
    └── test_password_manager.py
```

## 🚀 Quick Start

### 1. Installation

```bash
cd noobz-bot/official_bot
pip install -r requirements.txt
```

### 2. Configuration

```bash
cp .env.example .env
nano .env
```

Edit `.env` with your credentials:
- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/BotFather)
- `NOOBZ_BOT_TOKEN` - Get from Laravel backend
- `TMDB_API_KEY` - Get from [TMDB](https://www.themoviedb.org/settings/api)

### 3. Initialize Database

```bash
python -c "from config.database import init_database; init_database()"
```

### 4. Create Master Password

```bash
python -c "from services.auth_service import AuthService; AuthService().create_initial_master_password('your_secure_password')"
```

### 5. Run Bot

```bash
python main.py
```

## 📖 Usage Guide

### For Users (Admin Password)

1. Start bot: `/start`
2. Enter your admin password
3. Choose upload type:
   - 🎥 Upload Movie
   - 📺 Upload Series
   - 📊 View Stats

### For Master Password Holder

1. Start bot: `/start`
2. Enter master password
3. Access additional features:
   - 🔐 Password Manager
   - 👥 Create/revoke passwords
   - 📊 View all statistics

## 🔐 Security Features

- ✅ **Bcrypt Hashing** - All passwords hashed with cost factor 12
- ✅ **Session Expiry** - 24-hour automatic logout
- ✅ **Isolated Storage** - SQLite database separate from production
- ✅ **Token Validation** - Bot token validated on Laravel side
- ✅ **Rate Limiting** - 100 requests per minute
- ✅ **Input Validation** - All inputs validated and sanitized
- ✅ **SQL Injection Protection** - Parameterized queries only

## 📊 Database Schema

### Tables

1. **passwords** - Stores hashed passwords (master & admin)
2. **sessions** - Active user sessions with 24h expiry
3. **upload_contexts** - Upload state management
4. **upload_logs** - Upload history and statistics

See `database/schema.sql` for full schema.

## 🎓 Documentation

- [Setup Guide](SETUP.md) - Detailed installation and configuration
- [User Guide](USER_GUIDE.md) - How to use the bot
- [Master Guide](MASTER_GUIDE.md) - Password management guide
- [Security Guide](SECURITY.md) - Security best practices
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues

## 🧪 Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

## 📝 Logging

Logs are stored in:
- `bot.log` - Main bot log
- `uploads.log` - Upload tracking
- `errors.log` - Error details

View logs:
```bash
tail -f bot.log
```

## 🔄 Maintenance

### Backup Database

```bash
cp bot_secure.db bot_secure_backup_$(date +%Y%m%d).db
```

### View Statistics

```bash
sqlite3 bot_secure.db "SELECT * FROM upload_logs ORDER BY created_at DESC LIMIT 10;"
```

### Clean Old Sessions

```bash
sqlite3 bot_secure.db "DELETE FROM sessions WHERE expires_at < datetime('now');"
```

## 🐛 Troubleshooting

### Bot not responding

1. Check bot token in `.env`
2. Check bot is running: `ps aux | grep main.py`
3. Check logs: `tail -f bot.log`

### Authentication fails

1. Verify password is correct
2. Check session hasn't expired
3. View sessions: `sqlite3 bot_secure.db "SELECT * FROM sessions;"`

### Upload fails

1. Check API token in `.env`
2. Check Laravel backend is running
3. Check network connectivity
4. View upload logs: `tail -f uploads.log`

## 📞 Support

For issues or questions:
1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. View logs for error details
3. Contact bot administrator

## 📄 License

Proprietary - For Noobz.space internal use only.

## 🎉 Credits

Developed for Noobz.space platform.

---

**Status:** Production Ready  
**Version:** 1.0.0  
**Last Updated:** October 26, 2025
