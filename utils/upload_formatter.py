"""
Upload formatter untuk format response messages.
Generate formatted messages untuk Telegram responses.
"""

from typing import Optional, Dict, Any


class UploadFormatter:
    """
    Formatter untuk upload response messages.
    Generate user-friendly messages untuk Telegram.
    """
    
    @staticmethod
    def format_movie_success(
        title: Optional[str],
        tmdb_id: int,
        job_id: str,
        skipped: bool = False
    ) -> str:
        """
        Format success message untuk movie upload.
        
        Args:
            title: Movie title
            tmdb_id: TMDB ID
            job_id: Job ID dari queue
            skipped: Whether movie was skipped (already exists)
            
        Returns:
            Formatted message
        """
        if skipped:
            return (
                f"✅ Movie sudah ada di database\n\n"
                f"🎬 **{title or 'Unknown'}**\n"
                f"🆔 TMDB ID: `{tmdb_id}`\n\n"
                f"Movie ini sudah pernah di-upload sebelumnya."
            )
        
        return (
            f"✅ Movie upload berhasil!\n\n"
            f"🎬 **{title or 'Unknown'}**\n"
            f"🆔 TMDB ID: `{tmdb_id}`\n"
            f"🎫 Job ID: `{job_id}`\n\n"
            f"Movie sedang diproses. Status: **draft**\n"
            f"Cek di admin panel untuk publish."
        )
    
    @staticmethod
    def format_series_success(
        title: Optional[str],
        tmdb_id: int,
        job_id: str,
        skipped: bool = False
    ) -> str:
        """
        Format success message untuk series upload.
        
        Args:
            title: Series title
            tmdb_id: TMDB ID
            job_id: Job ID dari queue
            skipped: Whether series was skipped
            
        Returns:
            Formatted message
        """
        if skipped:
            return (
                f"✅ Series sudah ada di database\n\n"
                f"📺 **{title or 'Unknown'}**\n"
                f"🆔 TMDB ID: `{tmdb_id}`\n\n"
                f"Series ini sudah pernah di-upload sebelumnya.\n"
                f"Gunakan /uploadseason untuk tambah season baru."
            )
        
        return (
            f"✅ Series upload berhasil!\n\n"
            f"📺 **{title or 'Unknown'}**\n"
            f"🆔 TMDB ID: `{tmdb_id}`\n"
            f"🎫 Job ID: `{job_id}`\n\n"
            f"⚠️ **NOTE**: Seasons dan episodes TIDAK dibuat otomatis.\n"
            f"Gunakan:\n"
            f"- /uploadseason untuk upload season\n"
            f"- /uploadepisode untuk upload episode"
        )
    
    @staticmethod
    def format_season_success(
        series_title: Optional[str],
        season_number: int,
        tmdb_id: int,
        job_id: str,
        skipped: bool = False
    ) -> str:
        """
        Format success message untuk season upload.
        
        Args:
            series_title: Series title
            season_number: Season number
            tmdb_id: TMDB ID
            job_id: Job ID dari queue
            skipped: Whether season was skipped
            
        Returns:
            Formatted message
        """
        if skipped:
            return (
                f"✅ Season sudah ada di database\n\n"
                f"📺 **{series_title or 'Unknown'}**\n"
                f"🔢 Season {season_number}\n"
                f"🆔 TMDB ID: `{tmdb_id}`\n\n"
                f"Season ini sudah pernah di-upload sebelumnya."
            )
        
        return (
            f"✅ Season upload berhasil!\n\n"
            f"📺 **{series_title or 'Unknown'}**\n"
            f"🔢 Season {season_number}\n"
            f"🆔 TMDB ID: `{tmdb_id}`\n"
            f"🎫 Job ID: `{job_id}`\n\n"
            f"⚠️ **NOTE**: Episodes TIDAK dibuat otomatis.\n"
            f"Gunakan /uploadepisode untuk upload episode."
        )
    
    @staticmethod
    def format_episode_success(
        series_title: Optional[str],
        season_number: int,
        episode_number: int,
        episode_title: Optional[str],
        tmdb_id: int,
        job_id: str,
        skipped: bool = False
    ) -> str:
        """
        Format success message untuk episode upload.
        
        Args:
            series_title: Series title
            season_number: Season number
            episode_number: Episode number
            episode_title: Episode title
            tmdb_id: TMDB ID
            job_id: Job ID dari queue
            skipped: Whether episode was skipped
            
        Returns:
            Formatted message
        """
        episode_label = f"S{season_number:02d}E{episode_number:02d}"
        
        if skipped:
            return (
                f"✅ Episode sudah ada di database\n\n"
                f"📺 **{series_title or 'Unknown'}**\n"
                f"📹 {episode_label} - {episode_title or 'Unknown'}\n"
                f"🆔 TMDB ID: `{tmdb_id}`\n\n"
                f"Episode ini sudah pernah di-upload sebelumnya."
            )
        
        return (
            f"✅ Episode upload berhasil!\n\n"
            f"📺 **{series_title or 'Unknown'}**\n"
            f"📹 {episode_label} - {episode_title or 'Unknown'}\n"
            f"🆔 TMDB ID: `{tmdb_id}`\n"
            f"🎫 Job ID: `{job_id}`\n\n"
            f"Episode sedang diproses. Status: **draft**\n"
            f"Cek di admin panel untuk publish."
        )
    
    @staticmethod
    def format_error(error_message: str, context: Optional[str] = None) -> str:
        """
        Format error message.
        
        Args:
            error_message: Error message
            context: Optional context information
            
        Returns:
            Formatted error message
        """
        msg = f"❌ **Upload gagal**\n\n{error_message}"
        
        if context:
            msg += f"\n\n📝 Context: {context}"
        
        return msg
    
    @staticmethod
    def format_validation_error(error_message: str) -> str:
        """
        Format validation error message.
        
        Args:
            error_message: Validation error message
            
        Returns:
            Formatted error message
        """
        return f"⚠️ **Validation Error**\n\n{error_message}"
    
    @staticmethod
    def format_unauthorized() -> str:
        """
        Format unauthorized message.
        
        Returns:
            Unauthorized message
        """
        return (
            "🚫 **Unauthorized**\n\n"
            "Kamu tidak memiliki akses untuk menggunakan upload commands.\n"
            "Hubungi admin untuk mendapatkan akses."
        )
    
    @staticmethod
    def format_api_error(status_code: Optional[int], error_message: str) -> str:
        """
        Format API error message.
        
        Args:
            status_code: HTTP status code
            error_message: Error message
            
        Returns:
            Formatted error message
        """
        if status_code == 404:
            return (
                f"❌ **Resource Not Found**\n\n"
                f"{error_message}\n\n"
                f"💡 Tips:\n"
                f"- Untuk season: Upload series dulu dengan /uploadseries\n"
                f"- Untuk episode: Upload series & season dulu"
            )
        elif status_code == 422:
            return (
                f"⚠️ **Validation Failed**\n\n"
                f"{error_message}\n\n"
                f"Cek format input dan URL kamu."
            )
        elif status_code == 401:
            return (
                f"🔒 **Authentication Failed**\n\n"
                f"Bot token tidak valid atau expired.\n"
                f"Hubungi developer untuk fix issue ini."
            )
        else:
            return (
                f"❌ **API Error**\n\n"
                f"Status: {status_code or 'Unknown'}\n"
                f"Message: {error_message}\n\n"
                f"Coba lagi atau hubungi admin jika masalah berlanjut."
            )
    
    @staticmethod
    def format_help_message() -> str:
        """
        Format help message untuk upload commands.
        
        Returns:
            Formatted help message
        """
        return (
            "📤 **Upload Commands Help**\n\n"
            "**Upload Movie:**\n"
            "`/uploadmovie <tmdb_id>`\n"
            "`embed_url: https://...`\n"
            "`download_url: https://...` (optional)\n\n"
            "**Upload Series:**\n"
            "`/uploadseries <tmdb_id>`\n\n"
            "**Upload Season:**\n"
            "`/uploadseason <tmdb_id> season: <number>`\n"
            "Contoh: `/uploadseason 12345 season: 1`\n\n"
            "**Upload Episode:**\n"
            "`/uploadepisode <tmdb_id> S01E05`\n"
            "`embed_url: https://...`\n"
            "`download_url: https://...` (optional)\n\n"
            "💡 **Tips:**\n"
            "- TMDB ID bisa dari URL themoviedb.org\n"
            "- Season/Episode bisa pakai format S01E05\n"
            "- Upload series → season → episode secara berurutan\n"
            "- Semua upload masuk queue dan berstatus **draft**"
        )
