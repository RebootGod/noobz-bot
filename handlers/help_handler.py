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
Kirim announcement film ke channel/group dengan AI-powered content.

Format:
```
/announce [Target] [Context] [ID Film]
```

Contoh:
```
/announce Test Channel Ada film baru nih! [550988]
/announce @channelku Rekomendasi film bagus [603]
/announce "My Group" Film action seru [157336]
```

Parameter:
• **Target**: Nama channel/group (bisa pakai "" jika ada spasi) atau username @channelname
• **Context**: Konteks/tema untuk AI (opsional, default "Ada film baru")
• **ID Film**: ID film dari TMDB dalam [kurung siku]

Fitur:
✅ Generate caption AI dengan Gemini
✅ Kirim poster film otomatis
✅ Info lengkap: judul, rating, durasi, genre
✅ Link nonton di noobz.space
✅ Promosi channel t.me/noobzspace

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

Fitur:
✅ Kirim via personal message
✅ Poster film + info lengkap
✅ Rating, durasi, genre, sinopsis
✅ Bahasa Indonesia (fallback ke English)

---

📖 **Cara Cari ID Film TMDB**

1. Buka https://www.themoviedb.org/
2. Search film yang dicari
3. Lihat URL film: `themoviedb.org/movie/550988-joker`
4. ID film adalah angka setelah `/movie/`: **550988**

Contoh:
• Joker (2019): ID **550988**
• The Matrix (1999): ID **603**
• Inception (2010): ID **27205**

---

ℹ️ **Tips Penggunaan**

• Semua command dikirim di **Saved Messages**
• Bot akan reply hasilnya di Saved Messages
• Target harus sudah exist (channel/group/user)
• Untuk channel/group: bot harus punya akses
• Untuk user: bot harus bisa kirim PM ke mereka

---

❓ **Butuh Bantuan?**

Hubungi admin jika ada error atau pertanyaan:
Channel: t.me/noobzspace
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
