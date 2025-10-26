"""
Module: UI Formatters
Purpose: Format data into user-friendly display text

Provides formatting functions for:
- Movie/Series information
- Episode lists
- Statistics
- Timestamps

Author: RebootGod
Date: 2025
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class MovieFormatters:
    """Formatters for movie data"""
    
    @staticmethod
    def format_movie_info(movie_data: Dict[str, Any]) -> str:
        """
        Format movie data into readable text
        
        Args:
            movie_data: Dict with movie information from TMDB
            
        Returns:
            Formatted movie information string
        """
        title = movie_data.get('title', 'Unknown')
        year = movie_data.get('year', 'N/A')
        rating = movie_data.get('vote_average', 0)
        runtime = movie_data.get('runtime')
        overview = movie_data.get('overview', 'No overview available')
        
        # Truncate long overview
        if len(overview) > 150:
            overview = overview[:147] + "..."
        
        runtime_str = f"{runtime} min" if runtime else "N/A"
        
        genres = movie_data.get('genres', [])
        genre_names = [g['name'] for g in genres] if genres else []
        genres_str = ', '.join(genre_names[:3]) if genre_names else 'N/A'
        
        return (
            f"🎬 **{title}** ({year})\n\n"
            f"⭐ Rating: {rating}/10\n"
            f"⏱️ Runtime: {runtime_str}\n"
            f"🎭 Genres: {genres_str}\n\n"
            f"📝 {overview}"
        )
    
    @staticmethod
    def format_movie_preview(movie_data: Dict[str, Any], embed_url: Optional[str] = None) -> str:
        """
        Format movie preview with upload status
        
        Args:
            movie_data: Dict with movie information
            embed_url: Optional embed URL if set
            
        Returns:
            Formatted preview string
        """
        title = movie_data.get('title', 'Unknown')
        year = movie_data.get('year', 'N/A')
        tmdb_id = movie_data.get('tmdb_id', 'N/A')
        
        preview = (
            f"✅ TMDB ID set\n\n"
            f"🎬 {title} ({year})\n"
            f"🆔 TMDB ID: {tmdb_id}\n"
        )
        
        if embed_url:
            preview += f"🔗 Embed URL: Set\n"
        else:
            preview += f"🔗 Embed URL: Not set\n"
        
        return preview


class SeriesFormatters:
    """Formatters for series data"""
    
    @staticmethod
    def format_series_info(series_data: Dict[str, Any]) -> str:
        """
        Format series data into readable text
        
        Args:
            series_data: Dict with series information from TMDB
            
        Returns:
            Formatted series information string
        """
        title = series_data.get('title', 'Unknown')
        year = series_data.get('year', 'N/A')
        rating = series_data.get('vote_average', 0)
        seasons = series_data.get('number_of_seasons', 0)
        episodes = series_data.get('number_of_episodes', 0)
        overview = series_data.get('overview', 'No overview available')
        status = series_data.get('status', 'Unknown')
        
        # Truncate long overview
        if len(overview) > 150:
            overview = overview[:147] + "..."
        
        genres = series_data.get('genres', [])
        genre_names = [g['name'] for g in genres] if genres else []
        genres_str = ', '.join(genre_names[:3]) if genre_names else 'N/A'
        
        return (
            f"📺 **{title}** ({year})\n\n"
            f"⭐ Rating: {rating}/10\n"
            f"📊 Status: {status}\n"
            f"🎬 {seasons} seasons, {episodes} episodes\n"
            f"🎭 Genres: {genres_str}\n\n"
            f"📝 {overview}"
        )
    
    @staticmethod
    def format_season_info(season_data: Dict[str, Any]) -> str:
        """
        Format season information
        
        Args:
            season_data: Dict with season information
            
        Returns:
            Formatted season info string
        """
        season_num = season_data.get('season_number', 0)
        name = season_data.get('name', f'Season {season_num}')
        episode_count = season_data.get('episode_count', 0)
        air_date = season_data.get('air_date', 'Unknown')
        
        return (
            f"📺 {name}\n"
            f"📅 Air Date: {air_date}\n"
            f"📹 {episode_count} Episodes"
        )


class EpisodeFormatters:
    """Formatters for episode data"""
    
    @staticmethod
    def format_episode_preview(episodes: List[Dict[str, Any]]) -> str:
        """
        Format episode list preview for bulk upload
        
        Args:
            episodes: List of episode dicts to be uploaded
            
        Returns:
            Formatted preview string
        """
        if not episodes:
            return "No episodes to upload"
        
        preview = "Preview:\n"
        for ep in episodes[:10]:  # Show first 10
            ep_num = ep.get('episode_number', '?')
            title = ep.get('title', f'Episode {ep_num}')
            action = ep.get('action', 'New')  # 'New' or 'Update'
            
            # Truncate long titles
            if len(title) > 25:
                title = title[:22] + "..."
            
            preview += f"• E{ep_num:02d}: {title} ({action})\n"
        
        if len(episodes) > 10:
            preview += f"• ... and {len(episodes) - 10} more\n"
        
        return preview
    
    @staticmethod
    def format_episode_status(episode: Dict[str, Any]) -> str:
        """
        Format single episode status
        
        Args:
            episode: Dict with episode status information
            
        Returns:
            Formatted status string
        """
        ep_num = episode.get('episode_number', 0)
        title = episode.get('title', f'Episode {ep_num}')
        complete = episode.get('complete', False)
        needs_update = episode.get('needs_update', False)
        
        # Truncate long titles
        if len(title) > 30:
            title = title[:27] + "..."
        
        if complete:
            return f"✅ E{ep_num:02d} - {title} (Complete)"
        elif needs_update:
            return f"⚠️ E{ep_num:02d} - {title} (No URLs)"
        else:
            return f"❌ E{ep_num:02d} - {title}"


class StatsFormatters:
    """Formatters for statistics"""
    
    @staticmethod
    def format_user_stats(stats: Dict[str, Any]) -> str:
        """
        Format user upload statistics
        
        Args:
            stats: Dict with user statistics
            
        Returns:
            Formatted statistics string
        """
        total = stats.get('total_uploads', 0)
        movies = stats.get('movies', 0)
        series = stats.get('series', 0)
        episodes = stats.get('episodes', 0)
        
        return (
            f"📊 Your Upload Statistics\n\n"
            f"Total Uploads: {total}\n\n"
            f"By Type:\n"
            f"🎬 Movies: {movies}\n"
            f"📺 Series: {series}\n"
            f"📹 Episodes: {episodes}"
        )
    
    @staticmethod
    def format_recent_activity(activities: List[Dict[str, Any]]) -> str:
        """
        Format recent activity list
        
        Args:
            activities: List of activity dicts
            
        Returns:
            Formatted activity list string
        """
        if not activities:
            return "No recent activity"
        
        activity_str = "📈 Recent Activity:\n\n"
        for activity in activities[:10]:  # Show last 10
            date = activity.get('created_at', '')
            upload_type = activity.get('upload_type', 'upload')
            title = activity.get('title', 'Unknown')
            success = activity.get('success', True)
            
            # Format date
            date_str = TimeFormatters.format_relative_time(date) if date else 'Unknown'
            
            # Status emoji
            status = "✅" if success else "❌"
            
            # Truncate long titles
            if len(title) > 20:
                title = title[:17] + "..."
            
            activity_str += f"{status} {date_str} - {upload_type.title()}: {title}\n"
        
        return activity_str


class PasswordFormatters:
    """Formatters for password management"""
    
    @staticmethod
    def format_password_info(password: Dict[str, Any], show_stats: bool = True) -> str:
        """
        Format password information
        
        Args:
            password: Dict with password information
            show_stats: Whether to show usage statistics
            
        Returns:
            Formatted password info string
        """
        hint = password.get('password_hint', '****????')
        password_type = password.get('password_type', 'admin')
        created_at = password.get('created_at', 'Unknown')
        last_used = password.get('last_used_at', 'Never')
        is_current = password.get('is_current', False)
        
        type_emoji = "👑" if password_type == 'master' else "👤"
        current_marker = " - You" if is_current else ""
        
        info = f"{type_emoji} {hint} ({password_type.title()}){current_marker}\n"
        info += f"   Created: {created_at[:10] if created_at != 'Unknown' else 'Unknown'}\n"
        
        if last_used and last_used != 'Never':
            last_used_display = TimeFormatters.format_relative_time(last_used)
            info += f"   Last used: {last_used_display}\n"
        else:
            info += f"   Last used: Never\n"
        
        if show_stats and not is_current:
            uploads = password.get('total_uploads', 0)
            info += f"   Uploads: {uploads}\n"
        
        return info


class TimeFormatters:
    """Formatters for time/date"""
    
    @staticmethod
    def format_relative_time(timestamp: str) -> str:
        """
        Format timestamp as relative time (e.g., "2 hours ago")
        
        Args:
            timestamp: ISO format timestamp string
            
        Returns:
            Relative time string
        """
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
            delta = now - dt
            
            if delta.days > 365:
                years = delta.days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"
            elif delta.days > 30:
                months = delta.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            elif delta.days > 0:
                return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif delta.seconds > 60:
                minutes = delta.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
        except:
            return timestamp
    
    @staticmethod
    def format_time_remaining(timestamp: str) -> str:
        """
        Format timestamp as time remaining (e.g., "23 hours", "5 minutes")
        
        Args:
            timestamp: ISO format timestamp string (future time)
            
        Returns:
            Time remaining string
        """
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
            delta = dt - now  # Future - now = remaining
            
            # If expired
            if delta.total_seconds() <= 0:
                return "Expired"
            
            # Calculate remaining time
            if delta.days > 0:
                return f"{delta.days} day{'s' if delta.days > 1 else ''}"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''}"
            elif delta.seconds > 60:
                minutes = delta.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''}"
            else:
                return "Less than 1 minute"
        except:
            return timestamp
    
    @staticmethod
    def format_date(timestamp: str) -> str:
        """
        Format timestamp as date string
        
        Args:
            timestamp: ISO format timestamp string
            
        Returns:
            Formatted date string (e.g., "Oct 26, 2025")
        """
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%b %d, %Y")
        except:
            return timestamp


class URLFormatters:
    """Formatters for URLs"""
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: Full URL string
            
        Returns:
            Domain name
        """
        try:
            if '://' in url:
                domain = url.split('://')[1].split('/')[0]
            else:
                domain = url.split('/')[0]
            return domain
        except:
            return url
    
    @staticmethod
    def truncate_url(url: str, max_length: int = 50) -> str:
        """
        Truncate long URL for display
        
        Args:
            url: Full URL string
            max_length: Maximum length before truncation
            
        Returns:
            Truncated URL
        """
        if len(url) <= max_length:
            return url
        
        # Keep protocol and domain, truncate path
        if '://' in url:
            parts = url.split('://')
            protocol = parts[0] + '://'
            rest = parts[1]
            
            if len(rest) > (max_length - len(protocol) - 3):
                domain = rest.split('/')[0]
                return f"{protocol}{domain}/..."
        
        return url[:max_length - 3] + "..."


def format_progress_bar(current: int, total: int, length: int = 10) -> str:
    """
    Format progress bar
    
    Args:
        current: Current progress value
        total: Total value
        length: Bar length in characters
        
    Returns:
        Progress bar string
    """
    if total == 0:
        return "░" * length
    
    filled = int((current / total) * length)
    bar = "▓" * filled + "░" * (length - filled)
    percentage = int((current / total) * 100)
    
    return f"{bar} {percentage}%"
