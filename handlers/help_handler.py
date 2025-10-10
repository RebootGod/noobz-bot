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
Kirim announcement ke channel/group dengan AI-powered content.

Format:
```
/announce [Target] [Context]
/announce [Target] [movies/series] [Context] [Judul Tahun]
/announce [Target] [movies/series] [Context] [sinopsis] (Custom synopsis) [Judul Tahun]
```

Contoh:
```
/announce "Noobz Space" Ada konten baru nih!
/announce TestChannel [movies] Film action keren [Inception 2010]
/announce @channelku [series] Rekomendasi bagus [Breaking Bad 2008]
/announce "My Group" [movies] [sinopsis] Film tentang mimpi berlapis yang mind-blowing [Inception 2010]
```

Parameter:
• **Target**: Nama channel/group (bisa pakai "" jika ada spasi) atau username @channelname
• **Context**: Konteks/tema untuk AI
• **[movies/series]**: Opsional - pilih tipe konten (wajib jika pakai [Judul Tahun])
• **[Judul Tahun]**: Opsional - judul + tahun rilis (contoh: [Fight Club 1999])
• **[sinopsis]**: Opsional - custom synopsis untuk AI generation

---

🎬 **InfoFilm Command**
Kirim info film ke user tertentu via personal message.

Format:
```
/infofilm [Username] [ID Film]
```

Contoh:
```
/infofilm @johndoe [550988]
/infofilm @username [603]
```

Parameter:
• **Username**: Username Telegram target (harus pakai @)
• **ID Film**: ID film dari TMDB dalam [kurung siku]
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
