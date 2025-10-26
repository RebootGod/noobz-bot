-- Official Bot SQLite Database Schema
-- Version: 1.0.0
-- Last Updated: October 26, 2025

-- Passwords table: Stores hashed passwords for authentication
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

-- Sessions table: Manages active user sessions with 24h expiry
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

-- Upload contexts table: Manages upload state (series → season → episodes)
CREATE TABLE IF NOT EXISTS upload_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER NOT NULL,
    context_type TEXT NOT NULL CHECK(context_type IN ('movie', 'series', 'season', 'episode')),
    series_tmdb_id INTEGER,
    series_title TEXT,
    season_number INTEGER,
    step TEXT,  -- Current step: 'selecting_season', 'uploading_episodes', etc
    data TEXT,  -- JSON data for additional state
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Upload logs table: Tracks all uploads for statistics and auditing
CREATE TABLE IF NOT EXISTS upload_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER NOT NULL,
    telegram_username TEXT,
    password_id INTEGER NOT NULL,
    upload_type TEXT NOT NULL CHECK(upload_type IN ('movie', 'series', 'season', 'episode')),
    tmdb_id INTEGER,
    title TEXT,
    season_number INTEGER,
    episode_number INTEGER,
    success INTEGER DEFAULT 1,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (password_id) REFERENCES passwords(id) ON DELETE CASCADE
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_passwords_active ON passwords(is_active);
CREATE INDEX IF NOT EXISTS idx_passwords_type ON passwords(password_type);
CREATE INDEX IF NOT EXISTS idx_sessions_telegram_user ON sessions(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_contexts_telegram_user ON upload_contexts(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_contexts_type ON upload_contexts(context_type);
CREATE INDEX IF NOT EXISTS idx_logs_telegram_user ON upload_logs(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_logs_password ON upload_logs(password_id);
CREATE INDEX IF NOT EXISTS idx_logs_created ON upload_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_logs_type ON upload_logs(upload_type);

-- Initial data: Master password will be created via auth_service
-- Sessions will be managed automatically with 24h expiry
-- Upload contexts will be created/updated as users navigate flows
-- Upload logs will be created on each successful/failed upload
