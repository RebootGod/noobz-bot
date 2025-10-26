# Official Bot Development Plan

**Project:** Noobz Official Telegram Bot (Upload-focused)  
**Purpose:** Replace user bot dengan official bot untuk upload movies/series/episodes  
**Date:** October 26, 2025  
**Status:** Planning Phase

---

## 🎯 Project Goals

1. **Security:** Pisahkan bot credentials dari production database
2. **UX:** Form-style interface dengan inline buttons (modern, efisien)
3. **Context-Aware:** Bot ingat state upload (series → season → episodes)
4. **Bulk Upload:** Support upload multiple episodes sekaligus (max 20)
5. **Password Management:** Master password untuk manage admin passwords
6. **Validation:** Check TMDB & database sebelum upload
7. **Fallback:** Manual mode untuk TMDB data incomplete

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram User                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Official Bot (Python + python-telegram-bot)     │
│                                                              │
│  ├── Authentication Layer (SQLite)                          │
│  │   ├── Master Password                                    │
│  │   ├── Admin Passwords                                    │
│  │   └── Session Management (24h expiry)                   │
│  │                                                          │
│  ├── UI Layer (Inline Buttons)                             │
│  │   ├── Form-style inputs                                 │
│  │   ├── Context-aware navigation                          │
│  │   └── Progress indicators                               │
│  │                                                          │
│  ├── Business Logic                                         │
│  │   ├── TMDB integration                                  │
│  │   ├── Episode status checking                           │
│  │   ├── Bulk upload processing                            │
│  │   └── Context state management                          │
│  │                                                          │
│  └── Storage (SQLite: bot_secure.db)                       │
│      ├── passwords table                                    │
│      ├── sessions table                                     │
│      ├── upload_contexts table                              │
│      └── upload_logs table                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓ (HTTP API calls)
┌─────────────────────────────────────────────────────────────┐
│              Laravel Backend (Production)                    │
│                                                              │
│  ├── API Authentication Middleware                          │
│  │   └── Bot Token Validation (Authorization: Bearer)      │
│  │                                                          │
│  ├── Bot API Endpoints                                      │
│  │   ├── POST /api/bot/movies                              │
│  │   ├── POST /api/bot/series                              │
│  │   ├── POST /api/bot/series/{tmdbId}/seasons            │
│  │   ├── POST /api/bot/series/{tmdbId}/episodes           │
│  │   ├── GET  /api/bot/series/{tmdbId}/episodes-status    │ ← NEW
│  │   └── PUT  /api/bot/episodes/{episodeId}               │ ← NEW
│  │                                                          │
│  ├── Services                                               │
│  │   ├── ContentUploadService (FIXED)                      │
│  │   ├── TmdbDataService                                   │
│  │   └── Episode validation & update logic                 │
│  │                                                          │
│  └── Database (MySQL/PostgreSQL)                            │
│      ├── movies                                             │
│      ├── series                                             │
│      ├── series_seasons                                     │
│      └── series_episodes                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Phase 1: Backend Fixes (Laravel)

### 1.1 Fix ContentUploadService

**File:** `app/Services/ContentUploadService.php`

**Problem:** `checkEpisodeExists()` returns true even when episode has no URLs

**Solution:**
```php
public function checkEpisodeExists(
    int $seasonId, 
    int $episodeNumber,
    bool $requireUrls = false
): array
{
    $episode = SeriesEpisode::where('season_id', $seasonId)
        ->where('episode_number', $episodeNumber)
        ->first();

    if ($episode) {
        $hasUrls = !empty($episode->embed_url);
        
        // If URLs required and episode has no URLs, treat as not exists
        if ($requireUrls && !$hasUrls) {
            return [
                'exists' => false,
                'episode' => $episode,
                'needs_update' => true,
                'details' => [
                    'id' => $episode->id,
                    'episode_number' => $episode->episode_number,
                    'name' => $episode->name,
                    'has_embed' => false,
                    'has_download' => !empty($episode->download_url)
                ]
            ];
        }
        
        return [
            'exists' => true,
            'episode' => $episode,
            'needs_update' => false,
            'details' => [
                'id' => $episode->id,
                'episode_number' => $episode->episode_number,
                'name' => $episode->name,
                'has_embed' => !empty($episode->embed_url),
                'has_download' => !empty($episode->download_url)
            ]
        ];
    }

    return [
        'exists' => false,
        'episode' => null,
        'needs_update' => false
    ];
}
```

**Add new method:**
```php
public function updateEpisodeUrls(
    int $episodeId,
    string $embedUrl,
    ?string $downloadUrl = null
): array
{
    $episode = SeriesEpisode::findOrFail($episodeId);
    
    $episode->update([
        'embed_url' => $embedUrl,
        'download_url' => $downloadUrl,
        'status' => 'published', // Auto-publish
        'is_active' => true
    ]);
    
    return [
        'success' => true,
        'episode' => $episode
    ];
}
```

---

### 1.2 New API Endpoints

#### Endpoint 1: Get Episodes Status
**Route:** `GET /api/bot/series/{tmdbId}/episodes-status?season={seasonNumber}`

**Controller:** `App\Http\Controllers\Api\Bot\BotEpisodeStatusController.php`

**Purpose:** Check which episodes exist and which need URLs

**Response:**
```json
{
    "success": true,
    "data": {
        "series": {
            "id": 123,
            "tmdb_id": 1396,
            "title": "Breaking Bad",
            "slug": "breaking-bad-2008"
        },
        "season": {
            "id": 456,
            "season_number": 1,
            "episode_count": 7
        },
        "episodes": [
            {
                "episode_number": 1,
                "name": "Pilot",
                "exists_in_db": true,
                "has_urls": true,
                "episode_id": 789,
                "status": "complete"
            },
            {
                "episode_number": 2,
                "name": "Cat's in the Bag...",
                "exists_in_db": true,
                "has_urls": false,
                "episode_id": 790,
                "status": "needs_urls"
            },
            {
                "episode_number": 3,
                "name": "...And the Bag's in the River",
                "exists_in_db": false,
                "has_urls": false,
                "episode_id": null,
                "status": "not_created"
            }
        ],
        "tmdb_data_available": true,
        "summary": {
            "total_episodes": 7,
            "complete": 1,
            "needs_urls": 1,
            "not_created": 5
        }
    }
}
```

**Fallback:** If TMDB data incomplete:
```json
{
    "success": true,
    "tmdb_data_available": false,
    "message": "TMDB data incomplete. Use manual mode.",
    "data": {
        "series": {...},
        "season": {...},
        "episodes": [] // Empty or partial
    }
}
```

---

#### Endpoint 2: Update Episode URLs
**Route:** `PUT /api/bot/episodes/{episodeId}`

**Controller:** `App\Http\Controllers\Api\Bot\BotEpisodeUpdateController.php`

**Purpose:** Update existing episode with URLs

**Request:**
```json
{
    "embed_url": "https://vidsrc.to/embed/tv/1396/1/2",
    "download_url": "https://dl.noobz.space/bb-s01e02.mp4" // optional
}
```

**Response:**
```json
{
    "success": true,
    "message": "Episode URLs updated successfully",
    "data": {
        "episode_id": 790,
        "episode_number": 2,
        "season_number": 1,
        "name": "Cat's in the Bag...",
        "embed_url": "https://vidsrc.to/...",
        "download_url": "https://dl.noobz.space/...",
        "status": "published"
    }
}
```

---

### 1.3 Update ProcessEpisodeUploadJob

**File:** `app/Jobs/ProcessEpisodeUploadJob.php`

**Update logic:**
```php
// Check if episode exists
$existingCheck = $uploadService->checkEpisodeExists(
    $season->id, 
    $this->episodeNumber,
    true // Require URLs = true
);

if ($existingCheck['exists'] && !$existingCheck['needs_update']) {
    // Episode complete, skip
    Log::info('Episode already complete, skipping');
    DB::rollBack();
    return;
}

if ($existingCheck['needs_update']) {
    // Episode exists but no URLs, update it
    Log::info('Updating episode with URLs');
    $episode = $existingCheck['episode'];
    
    $episode->update([
        'embed_url' => $this->embedUrl,
        'download_url' => $this->downloadUrl,
        'status' => 'published',
        'is_active' => true
    ]);
    
    DB::commit();
    Log::info('Episode updated successfully');
    return;
}

// Episode not exists, create new
// ... (existing create logic)
```

---

### 1.4 Files to Create/Modify

**New Files:**
- `app/Http/Controllers/Api/Bot/BotEpisodeStatusController.php` (~200 lines)
- `app/Http/Controllers/Api/Bot/BotEpisodeUpdateController.php` (~150 lines)
- `app/Http/Requests/Bot/UpdateEpisodeRequest.php` (~50 lines)

**Modified Files:**
- `app/Services/ContentUploadService.php` (add methods, ~350 lines total)
- `app/Jobs/ProcessEpisodeUploadJob.php` (update logic, ~250 lines)
- `routes/api.php` (add 2 new routes)

---

## 📋 Phase 2: Official Bot (Python)

### 2.1 Project Structure

```
noobz-bot/
└── official_bot/
    ├── main.py                          # Entry point
    ├── bot_secure.db                    # SQLite database (gitignored)
    ├── .env                             # Bot configuration
    ├── requirements.txt                 # Python dependencies
    ├── README.md                        # Official bot documentation
    │
    ├── config/
    │   ├── __init__.py
    │   ├── settings.py                  # Environment settings
    │   ├── database.py                  # SQLite connection
    │   └── constants.py                 # Constants & enums
    │
    ├── database/
    │   ├── __init__.py
    │   ├── schema.sql                   # SQLite schema
    │   ├── models.py                    # SQLAlchemy models
    │   └── migrations/                  # Database migrations
    │
    ├── services/
    │   ├── __init__.py
    │   ├── auth_service.py              # Password authentication (~250 lines)
    │   ├── session_service.py           # Session management (~200 lines)
    │   ├── context_service.py           # Upload context state (~200 lines)
    │   ├── tmdb_service.py              # TMDB API integration (~300 lines)
    │   ├── noobz_api_service.py         # Laravel API client (~350 lines)
    │   └── password_manager_service.py  # Password CRUD (~250 lines)
    │
    ├── handlers/
    │   ├── __init__.py
    │   ├── start_handler.py             # /start command (~150 lines)
    │   ├── auth_handler.py              # Password authentication (~200 lines)
    │   ├── movie_upload_handler.py      # Movie upload flow (~300 lines)
    │   ├── series_upload_handler_1.py   # Series upload flow (~350 lines)
    │   ├── series_upload_handler_2.py   # Series upload continuation (~350 lines)
    │   ├── episode_bulk_handler.py      # Bulk episode upload (~300 lines)
    │   ├── episode_manual_handler.py    # Manual episode upload (~250 lines)
    │   ├── password_manager_handler.py  # Master password management (~300 lines)
    │   ├── stats_handler.py             # Statistics view (~200 lines)
    │   └── help_handler.py              # Help messages (~150 lines)
    │
    ├── ui/
    │   ├── __init__.py
    │   ├── keyboards.py                 # Inline keyboard builders (~300 lines)
    │   ├── messages.py                  # Message templates (~250 lines)
    │   └── formatters.py                # Response formatters (~200 lines)
    │
    ├── utils/
    │   ├── __init__.py
    │   ├── validators.py                # Input validators (~200 lines)
    │   ├── parsers.py                   # Message parsers (~250 lines)
    │   ├── crypto.py                    # Password hashing (~100 lines)
    │   └── logger.py                    # Logging setup (~100 lines)
    │
    └── tests/
        ├── __init__.py
        ├── test_auth.py
        ├── test_upload.py
        └── test_password_manager.py
```

---

### 2.2 SQLite Database Schema

**File:** `official_bot/database/schema.sql`

```sql
-- Passwords table
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password_hash TEXT NOT NULL,
    password_type TEXT NOT NULL CHECK(password_type IN ('master', 'admin')),
    password_hint TEXT NOT NULL,  -- Last 4 chars for display: ****1234
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by_telegram_id INTEGER,
    is_active INTEGER DEFAULT 1,
    last_used_at DATETIME,
    total_uploads INTEGER DEFAULT 0,
    notes TEXT
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER NOT NULL UNIQUE,
    telegram_username TEXT,
    password_id INTEGER NOT NULL,
    session_token TEXT NOT NULL UNIQUE,
    is_master INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (password_id) REFERENCES passwords(id) ON DELETE CASCADE
);

-- Upload contexts table (for state management)
CREATE TABLE IF NOT EXISTS upload_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER NOT NULL,
    context_type TEXT NOT NULL CHECK(context_type IN ('series', 'season', 'episode')),
    series_tmdb_id INTEGER,
    series_title TEXT,
    season_number INTEGER,
    step TEXT,  -- Current step: 'selecting_season', 'uploading_episodes', etc
    data TEXT,  -- JSON data for additional state
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Upload logs table (for tracking & stats)
CREATE TABLE IF NOT EXISTS upload_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER NOT NULL,
    telegram_username TEXT,
    password_id INTEGER NOT NULL,
    upload_type TEXT NOT NULL CHECK(upload_type IN ('movie', 'series', 'season', 'episode')),
    tmdb_id INTEGER,
    title TEXT,
    success INTEGER DEFAULT 1,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (password_id) REFERENCES passwords(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_telegram_user ON sessions(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_contexts_telegram_user ON upload_contexts(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_logs_telegram_user ON upload_logs(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_logs_password ON upload_logs(password_id);
CREATE INDEX IF NOT EXISTS idx_logs_created ON upload_logs(created_at);
```

---

### 2.3 User Flows

#### Flow 1: First Time User (Authentication)

```
User: /start

Bot:
┌─────────────────────────────────┐
│ 🎬 Noobz Upload Bot             │
│                                 │
│ Welcome! This bot helps you     │
│ upload movies and series.       │
│                                 │
│ 🔒 Authentication Required      │
└─────────────────────────────────┘

Please enter your password:

User: [enters password]

Bot (if correct):
✅ Authentication successful!
Welcome back!

Your session will expire in 24 hours.

[🎥 Upload Movie]  [📺 Upload Series]
[📊 My Stats]      [❓ Help]

Bot (if wrong):
❌ Invalid password. Please try again.

[🔄 Retry]  [❌ Cancel]

Bot (if master password):
✅ Master access granted!
Welcome, Master!

[🎥 Upload Movie]  [📺 Upload Series]
[📊 My Stats]      [🔐 Password Manager]  ← Extra button
[❓ Help]
```

---

#### Flow 2: Upload Movie

```
User: Click [🎥 Upload Movie]

Bot:
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

User: Click [📝 Set TMDB ID]

Bot: Please enter TMDB ID:
Example: 550 (for Fight Club)

User: 550

Bot: ✅ TMDB ID set
Fetching movie info...

🎬 Fight Club (1999)
⭐ 8.4/10
📝 A ticking-time-bomb insomniac...

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

User: Click [🔗 Set Embed URL]

Bot: Please enter Embed URL:
Example: https://vidsrc.to/embed/movie/550

User: https://vidsrc.to/embed/movie/550

Bot: ✅ Embed URL set

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

User: Click [✅ Upload Now]

Bot:
⏳ Uploading...

✅ Movie uploaded successfully!
🎬 Fight Club (1999)
🆔 TMDB ID: 550
🔗 Embed: vidsrc.to/embed/movie/550
⏳ Status: Processing...

The movie will be published automatically.

[📤 Upload Another Movie]  [🏠 Main Menu]
```

---

#### Flow 3: Upload Series (Context-Aware)

```
User: Click [📺 Upload Series]

Bot:
┌─────────────────────────────────┐
│ 📺 Upload Series                │
│                                 │
│ TMDB ID: [Not Set]              │
│                                 │
│ Status: ❌ Incomplete           │
└─────────────────────────────────┘

[📝 Set TMDB ID]  [❌ Cancel]

User: Click [📝 Set TMDB ID]

Bot: Please enter Series TMDB ID:
Example: 1396 (for Breaking Bad)

User: 1396

Bot: ✅ TMDB ID set
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

User: Click [1️⃣ Season 1 (7 ep)]

Bot:
⏳ Checking episode status...
Fetching data from TMDB...

┌─────────────────────────────────┐
│ 📺 Breaking Bad - Season 1      │
│ 7 Episodes                      │
│                                 │
│ Status:                         │
│ ✅ E01 - Pilot (Complete)       │
│ ⚠️ E02 - Cat's in... (No URLs)  │
│ ❌ E03 - ...And the Bag's...    │
│ ❌ E04 - Cancer Man             │
│ ❌ E05 - Gray Matter            │
│ ❌ E06 - Crazy Handful...       │
│ ❌ E07 - A No-Rough-Stuff...    │
│                                 │
│ Progress: 1/7 complete          │
└─────────────────────────────────┘

Upload mode:
[📦 Bulk Upload]  [📝 Single Episode]
[🔄 Refresh Status]  [🔙 Back]

User: Click [📦 Bulk Upload]

Bot:
┌─────────────────────────────────┐
│ 📦 Bulk Episode Upload          │
│                                 │
│ Series: Breaking Bad            │
│ Season: 1                       │
│ Episodes to upload: 6           │
│                                 │
│ Format (one per line):          │
│ EP | EMBED_URL | DL_URL         │
│                                 │
│ Use "-" for no download URL     │
│ Skip E01 (already complete)     │
└─────────────────────────────────┘

Example:
2 | https://vidsrc.to/embed/tv/1396/1/2 | -
3 | https://vidsrc.to/embed/tv/1396/1/3 | https://dl.../s01e03.mp4

[📋 Copy Template]  [❌ Cancel]

User: (pastes data)
2 | https://vidsrc.to/embed/tv/1396/1/2 | -
3 | https://vidsrc.to/embed/tv/1396/1/3 | -
4 | https://vidsrc.to/embed/tv/1396/1/4 | -

Bot:
📊 Validating...
✅ 3 episodes valid
⚠️ 0 errors

Preview:
- E02: Cat's in the Bag... (Update)
- E03: ...And the Bag's in the River (New)
- E04: Cancer Man (New)

[✅ Upload 3 Episodes]  [❌ Cancel]

User: Click [✅ Upload 3 Episodes]

Bot:
⏳ Uploading episodes...
▓▓▓░░░ 33% (1/3)

✅ E02 updated
⏳ Uploading...
▓▓▓▓▓░ 66% (2/3)

✅ E03 created
⏳ Uploading...
▓▓▓▓▓▓ 100% (3/3)

✅ E04 created

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

---

#### Flow 4: Manual Mode (TMDB Incomplete)

```
User: Select season

Bot:
⚠️ TMDB Data Incomplete
Season 1 has no episode data on TMDB.

┌─────────────────────────────────┐
│ ⚠️ TMDB Data Unavailable        │
│                                 │
│ Series: Old Series XYZ          │
│ Season: 1                       │
│                                 │
│ Choose mode:                    │
└─────────────────────────────────┘

[✍️ Manual Mode]  [🔙 Back]

User: Click [✍️ Manual Mode]

Bot:
┌─────────────────────────────────┐
│ ✍️ Manual Episode Upload        │
│                                 │
│ Series: Old Series XYZ          │
│ Season: 1                       │
│                                 │
│ Format options:                 │
│                                 │
│ [Full] EP | TITLE | EMBED | DL  │
│ [Quick] EP | EMBED | DL         │
│                                 │
│ Quick mode uses "Episode X"     │
│ as default title.               │
└─────────────────────────────────┘

[📝 Full Mode]  [⚡ Quick Mode]  [❌ Cancel]

User: Click [⚡ Quick Mode]

Bot:
⚡ Quick Upload Mode

Format per line:
EP | EMBED_URL | DOWNLOAD_URL

Example:
1 | https://vidsrc.to/... | -
2 | https://vidsrc.to/... | https://dl.../ep02.mp4

[📋 Copy Template]  [❌ Cancel]

(Rest of flow same as bulk upload)
```

---

#### Flow 5: Password Manager (Master Only)

```
User (Master): Click [🔐 Password Manager]

Bot:
┌─────────────────────────────────┐
│ 🔐 Password Management          │
│                                 │
│ Active Passwords: 3             │
│                                 │
│ 🔑 ****1234 (Master) - You      │
│    Created: Oct 20, 2025        │
│    Last used: Just now          │
│                                 │
│ 🔑 ****5678 (Admin)             │
│    Created: Oct 22, 2025        │
│    Last used: 2 hours ago       │
│    Uploads: 23                  │
│                                 │
│ 🔑 ****9012 (Admin)             │
│    Created: Oct 25, 2025        │
│    Last used: 1 day ago         │
│    Uploads: 5                   │
└─────────────────────────────────┘

[➕ Add Password]  [🗑️ Revoke Password]
[📊 View Stats]    [🔙 Back]

User: Click [➕ Add Password]

Bot:
┌─────────────────────────────────┐
│ ➕ Create New Password           │
│                                 │
│ Password Type:                  │
└─────────────────────────────────┘

[👑 Master Password]  [👤 Admin Password]
[❌ Cancel]

⚠️ Warning: Master passwords have full access
including password management!

User: Click [👤 Admin Password]

Bot:
Creating Admin Password

Please enter new password:
(Min 8 characters, mix of letters & numbers)

User: (enters password)

Bot:
Please confirm password:

User: (confirms)

Bot:
Optional: Add notes
(e.g., "Password for John")

User: Password for John

Bot:
✅ Password Created!

Password: ****3456
Type: Admin
Created: Oct 26, 2025
Notes: Password for John

⚠️ Save this password securely!
It will not be shown again.

[🔙 Back to Manager]  [🏠 Main Menu]

User: Click [🗑️ Revoke Password]

Bot:
┌─────────────────────────────────┐
│ 🗑️ Revoke Password              │
│                                 │
│ Select password to revoke:      │
└─────────────────────────────────┘

[🔑 ****5678 (Admin)]
   Last: 2h ago • Uploads: 23

[🔑 ****9012 (Admin)]
   Last: 1d ago • Uploads: 5

[❌ Cancel]

User: Click [🔑 ****5678 (Admin)]

Bot:
⚠️ Confirm Revocation

Password: ****5678 (Admin)
Created: Oct 22, 2025
Total Uploads: 23
Last Used: 2 hours ago

This action cannot be undone.
Active sessions will be terminated.

[✅ Confirm Revoke]  [❌ Cancel]

User: Click [✅ Confirm Revoke]

Bot:
✅ Password Revoked

Password ****5678 has been revoked.
Active sessions terminated.

[🔙 Back to Manager]  [🏠 Main Menu]

User: Click [📊 View Stats]

Bot:
┌─────────────────────────────────┐
│ 📊 Upload Statistics            │
│                                 │
│ Total Uploads: 51               │
│                                 │
│ By Type:                        │
│ 🎬 Movies: 20                   │
│ 📺 Series: 3                    │
│ 📹 Episodes: 28                 │
│                                 │
│ By Password:                    │
│ ****1234 (Master): 20           │
│ ****5678 (Admin): 23            │
│ ****9012 (Admin): 5             │
│ ****3456 (Admin): 3             │
│                                 │
│ Recent Activity:                │
│ Oct 26 14:30 - Episode upload   │
│ Oct 26 12:15 - Movie upload     │
│ Oct 25 18:45 - Episode upload   │
└─────────────────────────────────┘

[🔙 Back]
```

---

## 🔐 Security Considerations

### 1. Password Security
- ✅ Bcrypt hashing (cost factor 12)
- ✅ No plain text storage
- ✅ Session tokens with 24h expiry
- ✅ Master password can revoke any password
- ✅ Failed login attempts tracked

### 2. SQLite Security
- ✅ File permissions: 600 (owner only)
- ✅ Database file location: `official_bot/bot_secure.db`
- ✅ Gitignored (never committed)
- ✅ Encrypted backup recommended

### 3. API Security
- ✅ Bot token in .env (never in code)
- ✅ HTTPS only for API calls
- ✅ Token validation on Laravel side
- ✅ Rate limiting (100 req/min)
- ✅ Request timeout (30s)

### 4. Session Security
- ✅ 24-hour expiry
- ✅ Auto-logout on expiry
- ✅ Token regeneration on login
- ✅ Single active session per user
- ✅ Session hijacking protection

### 5. Input Validation
- ✅ TMDB ID: Integer validation
- ✅ URLs: Regex validation, whitelist domains
- ✅ Episode numbers: 1-999 range
- ✅ SQL Injection: Parameterized queries
- ✅ XSS: HTML escaping (not needed in Telegram)

---

## 📦 Dependencies

### Python Packages (requirements.txt)

```txt
# Telegram Bot Framework
python-telegram-bot==20.7

# HTTP Client
aiohttp==3.9.1
requests==2.31.0

# Database
sqlalchemy==2.0.23

# Password Hashing
bcrypt==4.1.2

# Environment Variables
python-dotenv==1.0.0

# Logging
colorlog==6.8.0

# Date/Time
python-dateutil==2.8.2

# Validation
validators==0.22.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
```

---

## 📝 Configuration (.env)

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Noobz API Configuration
NOOBZ_API_URL=https://noobz.space
NOOBZ_BOT_TOKEN=your_bot_api_token_from_laravel

# TMDB Configuration
TMDB_API_KEY=your_tmdb_api_key

# Database Configuration
DATABASE_PATH=bot_secure.db

# Security Configuration
SESSION_EXPIRY_HOURS=24
PASSWORD_MIN_LENGTH=8

# Bulk Upload Configuration
MAX_BULK_EPISODES=20

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Development
DEBUG=False
```

---

## 🧪 Testing Strategy

### Unit Tests
- ✅ Password hashing/verification
- ✅ Session management
- ✅ Input validators
- ✅ Message parsers

### Integration Tests
- ✅ Database operations
- ✅ API client calls
- ✅ TMDB service

### End-to-End Tests
- ✅ Full upload flows
- ✅ Password management
- ✅ Context state management

---

## 📊 Monitoring & Logging

### Logging Levels
- **INFO:** Normal operations, successful uploads
- **WARNING:** Failed validations, TMDB issues
- **ERROR:** API failures, database errors
- **CRITICAL:** Bot crashes, security issues

### Log Files
- `bot.log` - Main bot log
- `uploads.log` - Upload tracking
- `errors.log` - Error details

### Metrics to Track
- Total uploads (movies, series, episodes)
- Success/failure rates
- Average response time
- Active sessions
- Password usage statistics

---

## 🚀 Deployment Checklist

### Phase 1 Backend (Laravel)
- [ ] Fix ContentUploadService
- [ ] Create BotEpisodeStatusController
- [ ] Create BotEpisodeUpdateController
- [ ] Update ProcessEpisodeUploadJob
- [ ] Add new routes to api.php
- [ ] Test endpoints with Postman
- [ ] Push to git
- [ ] Verify Laravel Forge deployment
- [ ] Test on production

### Phase 2 Official Bot (Python)
- [ ] Setup project structure
- [ ] Create SQLite schema
- [ ] Implement authentication service
- [ ] Implement session management
- [ ] Create UI keyboards & messages
- [ ] Implement movie upload handler
- [ ] Implement series upload handler (part 1)
- [ ] Implement series upload handler (part 2)
- [ ] Implement bulk episode upload
- [ ] Implement manual mode
- [ ] Implement password manager
- [ ] Create TMDB service
- [ ] Create Noobz API service
- [ ] Add logging & error handling
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Create documentation
- [ ] Setup master password
- [ ] Test all flows
- [ ] Deploy to VPS
- [ ] Monitor initial usage

---

## 📅 Timeline Estimate

### Phase 1: Backend (2-3 hours)
- ContentUploadService fix: 30 min
- New controllers: 1 hour
- Update job: 30 min
- Testing & deployment: 1 hour

### Phase 2: Official Bot (8-10 hours)
- Project setup: 1 hour
- Database & models: 1 hour
- Authentication & session: 2 hours
- Upload handlers: 3 hours
- Password manager: 1 hour
- Testing & debugging: 2 hours

**Total: 10-13 hours**

---

## 🎯 Success Criteria

### Phase 1 (Backend)
- ✅ Episodes without URLs treated as "needs update"
- ✅ New endpoints return correct status
- ✅ Update logic works without errors
- ✅ No breaking changes to existing features

### Phase 2 (Bot)
- ✅ Users can authenticate with password
- ✅ Master can manage passwords
- ✅ Movie upload flow works end-to-end
- ✅ Series upload with context awareness
- ✅ Bulk upload handles 20 episodes
- ✅ Manual mode for incomplete TMDB
- ✅ Session expires after 24h
- ✅ All data stored in SQLite
- ✅ No production DB access from bot
- ✅ Comprehensive logging

---

## 📚 Documentation To Create

1. **README.md** - Official bot overview
2. **SETUP.md** - Installation & configuration guide
3. **USER_GUIDE.md** - How to use the bot
4. **MASTER_GUIDE.md** - Password management guide
5. **API.md** - Laravel API endpoints documentation
6. **SECURITY.md** - Security best practices
7. **TROUBLESHOOTING.md** - Common issues & solutions

---

## 🔄 Future Enhancements (Post-MVP)

1. **Batch Operations**
   - Upload entire season at once
   - Update multiple episodes

2. **Advanced Stats**
   - Per-user analytics
   - Upload trends
   - Popular content

3. **Notifications**
   - Processing complete alerts
   - Error notifications

4. **Content Management**
   - Edit uploaded content
   - Delete content
   - View upload history

5. **Multi-Language Support**
   - Indonesian & English

6. **Admin Panel Integration**
   - View bot uploads from web
   - Manage passwords from web

---

## 📞 Support & Maintenance

### Contact
- Primary: User (Master password holder)
- Secondary: Bot development team

### Backup Strategy
- Daily SQLite database backup
- .env configuration backup
- Log rotation (7 days retention)

### Update Strategy
- Zero-downtime deployment
- Backward compatibility
- Version tagging

---

**Last Updated:** October 26, 2025  
**Status:** Ready for Implementation  
**Next Step:** Begin Phase 1 - Backend Fixes
