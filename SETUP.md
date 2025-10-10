# Setup Instructions - Noobz Bot

## Step-by-Step Setup

### 1. Clone & Install Dependencies

```powershell
# Masuk ke folder project
cd e:\noobz-bot

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment Variables

```powershell
# Copy .env.example ke .env
Copy-Item .env.example .env

# Edit .env file dengan text editor
notepad .env
```

Isi credentials di `.env`:

```env
# Telegram - Get from https://my.telegram.org/apps
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+62xxxxxxxxxxxxx

# Gemini AI - Get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# TMDB - Get from https://www.themoviedb.org/settings/api
TMDB_API_KEY=your_tmdb_api_key_here

# Website
WEBSITE_URL=https://noobz.space
```

### 3. Get API Credentials

#### A. Telegram API
1. Buka https://my.telegram.org/apps
2. Login dengan nomor Telegram kamu
3. Create new application
4. Copy **API ID** dan **API Hash**
5. Paste ke `.env` file

#### B. Gemini AI API
1. Buka https://makersuite.google.com/app/apikey
2. Login dengan Google account
3. Click "Create API Key"
4. Copy API key
5. Paste ke `.env` file

#### C. TMDB API
1. Buka https://www.themoviedb.org/
2. Buat account (free)
3. Pergi ke Settings > API
4. Request API key (pilih Developer)
5. Copy **API Key (v3 auth)**
6. Paste ke `.env` file

### 4. First Run

```powershell
# Run bot
python main.py
```

**First time run:**
- Bot akan minta verification code dari Telegram
- Check Telegram app kamu, akan ada code
- Masukkan code tersebut
- Jika ada 2FA, masukkan password 2FA
- Bot akan create session file (`.session`)

### 5. Test Bot

1. Buka Telegram app
2. Pergi ke **Saved Messages** (chat dengan diri sendiri)
3. Test commands:

**Test /announce:**
```
/announce Test Channel Ini adalah test announcement [550]
```

**Test /infofilm:**
```
/infofilm @your_username movie inception 2010
```

### 6. Important Notes

⚠️ **PENTING:**
- Bot harus join channel/group yang ingin dikirim pesan terlebih dahulu
- Pastikan bot punya permission untuk send message di channel/group
- Semua command dikirim di **Saved Messages** untuk security
- Session file (`.session`) JANGAN di-commit ke git (sudah di `.gitignore`)

### 7. Troubleshooting

**Error: "Phone number is invalid"**
- Pastikan format: `+62xxx` (dengan country code)

**Error: "Channel not found"**
- Pastikan bot sudah join channel tersebut
- Try refresh dengan re-run bot

**Error: "User not found"**
- Pastikan username benar (tanpa @)
- User harus punya username (bukan first name saja)

**Error: "TMDB API error"**
- Check TMDB API key valid
- Check internet connection

**Error: "Gemini API error"**
- Check Gemini API key valid
- Check API quota (free tier ada limit)

### 8. Development Mode

```powershell
# Enable debug mode
# Edit .env:
DEBUG=True
```

Debug mode akan show more detailed logs.

## Project Structure

```
noobz-bot/
├── config/              # Configuration & settings
│   ├── settings.py      # Environment variables handler
│   └── __init__.py
├── services/            # External services integration
│   ├── telegram_client.py   # Telethon client
│   ├── gemini_service.py    # Gemini AI
│   ├── tmdb_service.py      # TMDB API
│   └── __init__.py
├── handlers/            # Command handlers
│   ├── announce_handler.py  # /announce command
│   ├── infofilm_handler.py  # /infofilm command
│   └── __init__.py
├── utils/               # Utilities
│   ├── message_parser.py    # Parse commands
│   ├── chat_finder.py       # Find channels/groups
│   ├── message_formatter.py # Format messages
│   └── __init__.py
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── .env                 # Your credentials (DON'T COMMIT!)
├── .env.example         # Template for .env
└── README.md           # Documentation
```

## Running in Production

### Option 1: Screen/Tmux (Linux)
```bash
screen -S noobz-bot
python main.py
# Ctrl+A+D to detach
```

### Option 2: Windows Service
```powershell
# Use NSSM (Non-Sucking Service Manager)
nssm install NoobzBot "C:\path\to\python.exe" "C:\path\to\main.py"
nssm start NoobzBot
```

### Option 3: Docker (Advanced)
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## Support

Jika ada issue atau pertanyaan, check:
1. Log file: `bot.log`
2. Console output untuk error messages
3. Telegram API status: https://telegram.org/status

## Security

🔒 **JANGAN SHARE:**
- `.env` file
- `.session` file
- API keys
- Access tokens

Semua sudah ada di `.gitignore`.
