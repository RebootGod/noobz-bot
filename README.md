# Noobz Bot - Telegram Announcement Bot

Bot Telegram untuk mengirim announcement dan info film ke channel, group, atau personal message dengan bantuan Gemini AI.

## Features

- 🤖 **AI-Powered Announcements**: Generate announcement menarik menggunakan Gemini 2.0 Flash
- 🎬 **Movie Info Sender**: Kirim info film dari TMDB ke user tertentu
- 🖼️ **Movie Posters**: Auto-send poster film dengan announcement/info
- 📢 **Multi-Destination**: Kirim ke channel, group, atau personal message
- 💬 **Saved Messages Control**: Control bot dari Saved Messages (chat dengan diri sendiri)
- ⚡ **Multiple AI Models**: Support Gemini 2.0 Flash, 1.5 Flash, dan 1.5 Pro
- 🔗 **Channel Promotion**: Auto-include channel link (t.me/noobzspace)
- 🔄 **Multi-Account Support**: Automatic account switching when hitting flood limits
- 🛡️ **Flood Protection**: Smart fallback system to bypass Telegram rate limits

## Prerequisites

1. **Telegram Account**: Account Telegram yang akan digunakan sebagai bot
2. **Telegram API Credentials**: 
   - Dapatkan dari https://my.telegram.org/apps
   - API ID dan API Hash
3. **Gemini API Key**: 
   - Dapatkan dari https://makersuite.google.com/app/apikey
   - Support Gemini 2.0 Flash (default), 1.5 Flash, dan 1.5 Pro
   - See [GEMINI_MODELS.md](GEMINI_MODELS.md) untuk comparison
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

**Environment Variables:**
```bash
# Primary Account (Required)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+62xxxxxxxxxxxxx  # Format: +[country_code][number]

# Secondary Account (Optional - for flood protection)
TELEGRAM_API_ID_2=your_api_id_2
TELEGRAM_API_HASH_2=your_api_hash_2
TELEGRAM_PHONE_2=+62xxxxxxxxxxxxx  # Different phone number

# AI & Movie Database
GEMINI_API_KEY=your_gemini_key
TMDB_API_KEY=your_tmdb_key
```

4. Setup Telegram accounts:
```bash
# Setup primary account (required)
python setup_account_1.py

# Setup secondary account (optional - for multi-account)
python setup_account_2.py
```

5. Run bot:
```bash
python main.py
```

## Usage

Semua command dikirim ke **Saved Messages** (chat dengan diri sendiri).

### Command: /announce

Kirim announcement dengan AI-generated content ke channel/group.

**Format:**
```
/announce <channel/group name> [options] <prompt>
```

**Options:**
- `[gemini]` - Generate AI-enhanced announcement with Gemini
- `[movies]` - Search movie by title
- `[series]` - Search series by title
- `[moviesid][ID]` - Get movie by TMDB ID directly (e.g., `[moviesid][550]`)
- `[seriesid][ID]` - Get series by TMDB ID directly (e.g., `[seriesid][275177]`)
- `[Judul]` or `[Judul 2024]` - Movie/series title with optional year (requires `[movies]` or `[series]`)
- `[sinopsis]` - Custom synopsis

**Contoh dengan TMDB ID (Recommended):**
```
/announce "Noobz Cinema" [moviesid][550] [gemini] Film keren banget! Fight Club udah bisa ditonton
/announce TestChannel [seriesid][275177] Episode baru "Noobz Cinema" sudah ready!
```

**Contoh dengan Title Search:**
```
/announce "Noobz Space" [movies] [gemini] Film bagus [Inception]
/announce TestChannel [series] [gemini] Series keren [Breaking Bad 2008]
```

**Why use [moviesid]/[seriesid]?**
- ✅ **Faster** - Direct fetch tanpa search
- ✅ **More accurate** - Langsung dapat data yang tepat
- ✅ **No ambiguity** - Tidak ada salah film/series

Bot akan:
1. Ambil info film/series dari TMDB (by ID atau search by title)
2. Generate announcement menarik dengan Gemini AI (jika ada `[gemini]`)
3. Send poster film/series + announcement ke channel/group
4. Include link noobz.space dan channel Telegram

### Command: /infofilm

Kirim info film/series ke user tertentu dengan personal message.

**Format:**
```
/infofilm @username [options] <prompt>
```

**Options:**
- `[gemini]` - Generate AI-enhanced info with Gemini
- `[movies]` - Search movie by title
- `[series]` - Search series by title
- `[moviesid][ID]` - Get movie by TMDB ID directly (e.g., `[moviesid][550]`)
- `[seriesid][ID]` - Get series by TMDB ID directly (e.g., `[seriesid][275177]`)
- `[Judul]` or `[Judul 2024]` - Movie/series title with optional year (requires `[movies]` or `[series]`)
- `[sinopsis]` - Custom synopsis

**Contoh dengan TMDB ID (Recommended):**
```
/infofilm @userA [moviesid][550] Film ini bagus banget bro!
/infofilm @userB [seriesid][275177] [gemini] Series ini keren, wajib nonton!
```

**Contoh dengan Title Search:**
```
/infofilm @userA [movies] Film bagus [Inception]
/infofilm @userB [series] [gemini] Series keren [Breaking Bad 2008]
```

Bot akan:
1. Ambil info film/series dari TMDB (by ID atau search by title)
2. Format info dengan poster + details (with Gemini AI jika ada `[gemini]`)
3. Send poster film/series + info ke personal message target user
4. Include link noobz.space dan channel Telegram

## Project Structure

```
noobz-bot/
├── config/
│   └── settings.py              # Environment configuration
├── services/
│   ├── telegram_client.py       # Telethon client handler
│   ├── multi_account_manager.py # Multi-account management with flood detection
│   ├── gemini_service.py        # Gemini AI integration
│   └── tmdb_service.py          # TMDB API integration
├── handlers/
│   ├── announce_handler.py      # /announce command handler
│   ├── infofilm_handler.py      # /infofilm command handler
│   └── help_handler.py          # /help command handler
├── utils/
│   ├── message_parser.py        # Command parser
│   ├── chat_finder.py           # Find channel/group by name
│   └── message_formatter.py     # Message formatting
├── setup_account_1.py           # Setup script for primary account
├── setup_account_2.py           # Setup script for secondary account
├── main.py                      # Bot entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Multi-Account System

Bot mendukung **2 akun Telegram** untuk bypass flood limits:

### How It Works
1. **Primary Account**: Akun utama yang digunakan untuk send messages
2. **Secondary Account**: Akun backup yang otomatis dipakai jika primary kena flood limit
3. **Auto-Switching**: Bot otomatis switch ke account lain jika detect `FloodWaitError`
4. **Cooldown Tracking**: Track account mana yang sedang limited dan kapan available lagi

### Setup Multi-Account
1. Buat 2 API credentials berbeda di https://my.telegram.org/apps (satu untuk tiap akun)
2. Tambahkan credentials account kedua di `.env`:
   ```bash
   TELEGRAM_API_ID_2=your_second_api_id
   TELEGRAM_API_HASH_2=your_second_api_hash
   TELEGRAM_PHONE_2=+62xxxxxxxxxxxxx
   ```
3. Jalankan setup untuk account kedua:
   ```bash
   python setup_account_2.py
   ```
4. Restart bot - multi-account akan otomatis aktif!

### Benefits
- ✅ **No downtime** saat kena flood limit
- ✅ **Automatic failover** ke backup account
- ✅ **Smart cooldown tracking** untuk optimal account usage
- ✅ **Transparent switching** - user tidak perlu tahu pakai account mana

## Notes

- Bot menggunakan Telethon sebagai userbot, jadi bisa kirim personal message
- Pastikan account yang digunakan sudah join ke channel/group yang ingin dikirim pesan
- Bot akan listen dari Saved Messages untuk keamanan
- Semua file maksimal 300 baris untuk kemudahan maintenance

## License

MIT License
