# Noobz Bot - Telegram Announcement Bot

Bot Telegram untuk mengirim announcement dan info film ke channel, group, atau personal message dengan bantuan Gemini AI.

## Features

- 🤖 **AI-Powered Announcements**: Generate announcement menarik menggunakan Gemini AI
- 🎬 **Movie Info Sender**: Kirim info film dari TMDB ke user tertentu
- 📢 **Multi-Destination**: Kirim ke channel, group, atau personal message
- 💬 **Saved Messages Control**: Control bot dari Saved Messages (chat dengan diri sendiri)

## Prerequisites

1. **Telegram Account**: Account Telegram yang akan digunakan sebagai bot
2. **Telegram API Credentials**: 
   - Dapatkan dari https://my.telegram.org/apps
   - API ID dan API Hash
3. **Gemini API Key**: Dapatkan dari https://makersuite.google.com/app/apikey
4. **TMDB API Key**: Dapatkan dari https://www.themoviedb.org/settings/api

## Installation

1. Clone repository ini:
```bash
git clone <repository-url>
cd noobz-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment variables:
```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env dan isi dengan credentials kamu
```

4. Run bot:
```bash
python main.py
```

## Usage

Semua command dikirim ke **Saved Messages** (chat dengan diri sendiri).

### Command: /announce

Kirim announcement dengan AI-generated content ke channel/group.

**Format:**
```
/announce <channel/group name> <prompt with [tmdbid]>
```

**Contoh:**
```
/announce Noobz Space Gue ada upload film baru [550] buatin announcement yang bagus dan menarik dong di channel Noobz Space
```

Bot akan:
1. Cari info film dari TMDB berdasarkan ID (550 = Fight Club)
2. Generate announcement menarik dengan Gemini AI
3. Kirim ke channel/group "Noobz Space"

### Command: /infofilm

Kirim info film ke user tertentu dengan personal message.

**Format:**
```
/infofilm @username <type> <keyword> <year>
```

**Contoh:**
```
/infofilm @userA movie qodrat 2023
```

Bot akan:
1. Cari film "Qodrat" (2023) di TMDB
2. Format info film dengan link ke noobz.space
3. Kirim personal message ke @userA

## Project Structure

```
noobz-bot/
├── config/
│   └── settings.py          # Environment configuration
├── services/
│   ├── telegram_client.py   # Telethon client handler
│   ├── gemini_service.py    # Gemini AI integration
│   └── tmdb_service.py      # TMDB API integration
├── handlers/
│   ├── announce_handler.py  # /announce command handler
│   └── infofilm_handler.py  # /infofilm command handler
├── utils/
│   ├── message_parser.py    # Command parser
│   ├── chat_finder.py       # Find channel/group by name
│   └── message_formatter.py # Message formatting
├── main.py                  # Bot entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Notes

- Bot menggunakan Telethon sebagai userbot, jadi bisa kirim personal message
- Pastikan account yang digunakan sudah join ke channel/group yang ingin dikirim pesan
- Bot akan listen dari Saved Messages untuk keamanan
- Semua file maksimal 300 baris untuk kemudahan maintenance

## License

MIT License
