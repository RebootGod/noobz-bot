"""
Message Formatter utility untuk format messages.
Create formatted messages untuk announcements dan info film.
"""

import logging
from typing import Dict, Any, Optional
from config.settings import get_settings

logger = logging.getLogger(__name__)


class MessageFormatter:
    """
    Formatter untuk create formatted Telegram messages.
    """
    
    def __init__(self):
        """Initialize formatter."""
        self.settings = get_settings()
        self.website_url = self.settings.website_url
    
    def format_announcement(
        self, 
        generated_text: str, 
        movie_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format announcement message.
        
        Args:
            generated_text: AI-generated announcement text
            movie_info: Optional movie info untuk tambahan context
            
        Returns:
            Formatted announcement message
        """
        if not movie_info:
            return generated_text
        
        # Extract movie info
        title = movie_info.get('title') or movie_info.get('name', 'Unknown')
        rating = movie_info.get('vote_average', 0)
        genres = movie_info.get('genres', [])
        runtime = movie_info.get('runtime') or movie_info.get('episode_run_time', [None])[0] if isinstance(movie_info.get('episode_run_time'), list) else movie_info.get('episode_run_time')
        tmdb_id = movie_info.get('id')
        
        # Debug logging
        logger.info(f"Formatting announcement for: {title}")
        logger.info(f"Runtime value: {runtime}, Type: {type(runtime)}")
        
        # Format genre (max 3)
        genre_names = [g['name'] for g in genres[:3]]
        genre_text = ', '.join(genre_names) if genre_names else 'N/A'
        
        # Format runtime
        runtime_text = ""
        if runtime and runtime > 0:
            hours = runtime // 60
            minutes = runtime % 60
            if hours > 0:
                runtime_text = f"{hours}h {minutes}m"
            else:
                runtime_text = f"{minutes}m"
        
        # Build formatted message
        message = f"🎬 **{title}**\n\n"
        message += f"{generated_text}\n\n"
        message += f"⭐ Rating: {rating}/10\n"
        # Always show duration (even if fallback)
        message += f"⏱️ Durasi: {runtime_text if runtime_text else 'N/A'}\n"
        message += f"🎭 Genre: {genre_text}\n\n"
        message += f"🔗 Nonton di: {self.website_url}\n"
        message += f"📢 Join channel: t.me/noobzspace"
        
        return message
    
    def format_movie_info(
        self, 
        movie_info: Dict[str, Any], 
        content_type: str = 'movie'
    ) -> str:
        """
        Format movie/TV info message untuk personal message.
        
        Args:
            movie_info: Dictionary berisi movie/TV info dari TMDB
            content_type: 'movie' atau 'tv'
            
        Returns:
            Formatted info message
        """
        # Extract info
        title = movie_info.get('title') or movie_info.get('name', 'Unknown')
        overview = movie_info.get('overview', 'No description available.')
        rating = movie_info.get('vote_average', 0)
        tmdb_id = movie_info.get('id')
        
        # Release date
        if content_type == 'movie':
            release_date = movie_info.get('release_date', '')
            year = release_date[:4] if release_date else 'N/A'
            date_label = 'Release'
        else:
            release_date = movie_info.get('first_air_date', '')
            year = release_date[:4] if release_date else 'N/A'
            date_label = 'First Air'
        
        # Genres
        genres = movie_info.get('genres', [])
        genre_names = ', '.join([g['name'] for g in genres]) if genres else 'N/A'
        
        # Runtime/Duration
        runtime_text = ''
        if content_type == 'movie':
            runtime = movie_info.get('runtime', 0)
            if runtime and runtime > 0:
                hours = runtime // 60
                minutes = runtime % 60
                if hours > 0:
                    runtime_text = f"{hours}h {minutes}m"
                else:
                    runtime_text = f"{minutes}m"
        else:
            # For TV series, use episode_run_time
            episode_runtime = movie_info.get('episode_run_time', [])
            if episode_runtime and len(episode_runtime) > 0:
                runtime_text = f"{episode_runtime[0]}m per episode"
        
        # Build message
        message = f"""
🎬 **{title}** ({year})

📝 **Synopsis:**
{overview}

⭐ **Rating:** {rating}/10
⏱️ **Durasi:** {runtime_text if runtime_text else 'N/A'}
🎭 **Genre:** {genre_names}
📅 **{date_label}:** {release_date or 'N/A'}
"""
        # Add website link
        if tmdb_id:
            message += f"\n🔗 **Nonton di:** {self.website_url}\n"
            message += f"� **Join channel:** t.me/noobzspace\n"
        message += "\n✨ Selamat menonton!"
        return message.strip()
    
    def format_search_results(
        self, 
        results: list, 
        content_type: str = 'movie'
    ) -> str:
        """
        Format search results sebagai numbered list.
        
        Args:
            results: List of search results dari TMDB
            content_type: 'movie' atau 'tv'
            
        Returns:
            Formatted search results message
        """
        if not results:
            return "❌ Tidak ada hasil ditemukan."
        
        message = f"🔍 **Ditemukan {len(results)} hasil:**\n\n"
        
        for idx, item in enumerate(results[:5], 1):  # Max 5 results
            title = item.get('title') or item.get('name', 'Unknown')
            year = ''
            
            if content_type == 'movie':
                release_date = item.get('release_date', '')
                year = f" ({release_date[:4]})" if release_date else ''
            else:
                first_air = item.get('first_air_date', '')
                year = f" ({first_air[:4]})" if first_air else ''
            
            rating = item.get('vote_average', 0)
            
            message += f"{idx}. **{title}**{year} - ⭐ {rating}/10\n"
        
        return message.strip()
    
    def format_error(self, error_message: str) -> str:
        """
        Format error message.
        
        Args:
            error_message: Error message text
            
        Returns:
            Formatted error message
        """
        return f"❌ **Error:** {error_message}"
    
    def format_success(self, success_message: str) -> str:
        """
        Format success message.
        
        Args:
            success_message: Success message text
            
        Returns:
            Formatted success message
        """
        return f"✅ **Success:** {success_message}"
    
    def format_info(self, info_message: str) -> str:
        """
        Format info message.
        
        Args:
            info_message: Info message text
            
        Returns:
            Formatted info message
        """
        return f"ℹ️ {info_message}"
    
    def format_help(self) -> str:
        """
        Format help message dengan list commands.
        
        Returns:
            Formatted help message
        """
        return """
🤖 **Noobz Bot Commands**

**1. /announce**
Kirim announcement ke channel/group dengan AI-generated content.

Format: `/announce <channel/group name> <prompt>`

Contoh:
`/announce Noobz Space Gue ada upload film baru [550] buatin announcement yang bagus`

**2. /infofilm**
Kirim info film ke user dengan personal message.

Format: `/infofilm @username <movie|tv> <keyword> [year]`

Contoh:
`/infofilm @userA movie qodrat 2023`

**Tips:**
- Gunakan [tmdb_id] di prompt untuk reference film tertentu
- Semua command dikirim di Saved Messages (chat dengan diri sendiri)
- Bot akan cari channel/group by name (fuzzy match)

Need help? Contact admin.
""".strip()


# Global instance
_message_formatter: Optional[MessageFormatter] = None


def get_message_formatter() -> MessageFormatter:
    """
    Get global MessageFormatter instance.
    
    Returns:
        MessageFormatter instance
    """
    global _message_formatter
    if _message_formatter is None:
        _message_formatter = MessageFormatter()
    return _message_formatter
