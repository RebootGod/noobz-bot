"""
Handler untuk /help command.
Menampilkan daftar semua command yang tersedia.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HelpHandler:
    """Handler untuk menampilkan help message."""
    
    def __init__(self, client):
        """
        Initialize help handler.
        
        Args:
            client: Telethon client instance
        """
        self.client = client
    
    async def handle(self, parsed_command) -> Dict[str, Any]:
        """
        Handle /help command.
        
        Args:
            parsed_command: Parsed command object
            
        Returns:
            Dict dengan success status dan message
        """
        try:
            help_text = self._get_help_text()
            
            return {
                'success': True,
                'message': help_text
            }
            
        except Exception as e:
            logger.error(f"Error in help handler: {e}")
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
    
    def _get_help_text(self) -> str:
        """
        Generate help text dengan daftar semua commands.
        
        Returns:
            Formatted help text
        """
        help_text = """
🤖 **Noobz Bot - Daftar Command**

📢 **Announce Command**
Kirim announcement ke channel/group.

Format:
```
/announce [Target] [Context]
/announce [Target] [gemini] [Context]
/announce [Target] [movies/series] [Context] [Judul]
/announce [Target] [moviesid/seriesid][TMDB_ID] [Context]
/announce [Target] [movies/series] [gemini] [Context] [Judul 2024]
/announce [Target] [movies/series] [gemini] [Context] [sinopsis] (synopsis) [Judul]
```

Contoh:
```
/announce "Noobz Space" Ada konten baru hari ini!
/announce TestChannel [gemini] Cek konten baru yang keren!
/announce @channelku [movies] Film bagus [Inception]
/announce "My Group" [series] [gemini] Series keren [Breaking Bad 2008]
/announce TestChannel [moviesid][550] [gemini] Film keren banget!
/announce "Noobz Cinema" [seriesid][275177] Episode baru sudah ready!
/announce TestChannel [movies] [gemini] [sinopsis] Film tentang mimpi berlapis [Inception]
```

Parameter:
• **Target**: Nama channel/group (bisa pakai "" jika ada spasi)
• **[gemini]**: Opsional - enhance dengan AI generation
• **[movies/series]**: Opsional - pilih tipe konten untuk search TMDB by title
• **[moviesid][ID]** atau **[seriesid][ID]**: Opsional - cari by TMDB ID (contoh: [moviesid][550])
• **[Judul]** atau **[Judul 2024]**: Judul film/series (tahun opsional) - hanya untuk [movies/series]
• **[sinopsis]**: Opsional - custom synopsis
• **Context**: Konteks/tema announcement

---

🎬 **InfoFilm Command**
Kirim info film/series ke user via personal message.

Format:
```
/infofilm @username [Context]
/infofilm @username [gemini] [Context]
/infofilm @username [movies/series] [Context] [Judul]
/infofilm @username [moviesid/seriesid][TMDB_ID] [Context]
/infofilm @username [movies/series] [gemini] [Context] [Judul 2024]
/infofilm @username [movies/series] [gemini] [Context] [sinopsis] (synopsis) [Judul]
```

Contoh:
```
/infofilm @johndoe Ada rekomendasi nih
/infofilm @username [gemini] Cek film ini
/infofilm @user [movies] Film bagus [Inception]
/infofilm @johndoe [series] [gemini] Series keren [Breaking Bad 2008]
/infofilm @username [moviesid][550] Film ini bagus banget!
/infofilm @johndoe [seriesid][275177] Series ini keren!
/infofilm @username [movies] [gemini] [sinopsis] Film mind-bending [Inception]
```

Parameter:
• **@username**: Username Telegram target (harus pakai @)
• **[gemini]**: Opsional - enhance dengan AI generation
• **[movies/series]**: Opsional - pilih tipe konten untuk search TMDB by title
• **[moviesid][ID]** atau **[seriesid][ID]**: Opsional - cari by TMDB ID (contoh: [seriesid][275177])
• **[Judul]** atau **[Judul 2024]**: Judul film/series (tahun opsional) - hanya untuk [movies/series]
• **[sinopsis]**: Opsional - custom synopsis
• **Context**: Konteks/pesan
"""
        return help_text.strip()


def create_help_handler(client):
    """
    Factory function untuk create help handler.
    
    Args:
        client: Telethon client instance
        
    Returns:
        HelpHandler instance
    """
    return HelpHandler(client)
