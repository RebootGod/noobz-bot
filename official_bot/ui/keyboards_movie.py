"""
Module: UI Keyboards - Movie Upload
Purpose: Inline keyboard builders for movie upload flow

Provides keyboard layouts for:
- Movie upload form
- Setting TMDB ID, embed URL, download URL
- Upload confirmation
- Post-upload actions

Author: RebootGod
Date: 2025
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, Optional


class MovieUploadKeyboards:
    """
    Keyboard builders for movie upload flow
    
    Form-style interface with inline buttons.
    """

    @staticmethod
    def movie_form(movie_state: Dict[str, Any]) -> InlineKeyboardMarkup:
        """
        Build movie upload form keyboard
        
        Shows current state and available actions.
        
        Args:
            movie_state: Dict with keys:
                - tmdb_id: int or None
                - tmdb_data: dict or None (movie info from TMDB)
                - embed_url: str or None
                - download_url: str or None
                
        Returns:
            InlineKeyboardMarkup with form buttons
        """
        keyboard = []
        
        # TMDB ID button
        tmdb_text = "📝 Set TMDB ID" if not movie_state.get('tmdb_id') else "✅ Change TMDB ID"
        keyboard.append([
            InlineKeyboardButton(tmdb_text, callback_data="movie_set_tmdb")
        ])
        
        # Only show URL buttons if TMDB ID is set
        if movie_state.get('tmdb_id'):
            # Embed URL button
            embed_text = "🔗 Set Embed URL" if not movie_state.get('embed_url') else "✅ Change Embed URL"
            keyboard.append([
                InlineKeyboardButton(embed_text, callback_data="movie_set_embed")
            ])
            
            # Download URL button (optional)
            download_text = "📥 Set Download URL" if not movie_state.get('download_url') else "✅ Change Download URL"
            keyboard.append([
                InlineKeyboardButton(download_text, callback_data="movie_set_download")
            ])
            
            # Upload button (only if required fields are set)
            if movie_state.get('embed_url'):
                keyboard.append([
                    InlineKeyboardButton("✅ Upload Now", callback_data="movie_upload_confirm")
                ])
        
        # Cancel button
        keyboard.append([
            InlineKeyboardButton("❌ Cancel", callback_data="movie_cancel")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def tmdb_id_actions() -> InlineKeyboardMarkup:
        """
        Build TMDB ID input actions keyboard
        
        Returns:
            InlineKeyboardMarkup with cancel button
        """
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="movie_cancel")]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def embed_url_actions() -> InlineKeyboardMarkup:
        """
        Build embed URL input actions keyboard
        
        Returns:
            InlineKeyboardMarkup with cancel button
        """
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="movie_cancel")]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def download_url_actions() -> InlineKeyboardMarkup:
        """
        Build download URL input actions keyboard
        
        Includes skip option since download URL is optional.
        
        Returns:
            InlineKeyboardMarkup with skip and cancel buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("⏭️ Skip", callback_data="movie_skip_download"),
                InlineKeyboardButton("❌ Cancel", callback_data="movie_cancel")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def upload_confirmation(movie_data: Dict[str, Any]) -> InlineKeyboardMarkup:
        """
        Build upload confirmation keyboard
        
        Shows movie info and asks for final confirmation.
        
        Args:
            movie_data: Dict with movie information
            
        Returns:
            InlineKeyboardMarkup with confirm and cancel buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm Upload", callback_data="movie_upload_execute"),
                InlineKeyboardButton("❌ Cancel", callback_data="movie_cancel")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def upload_success() -> InlineKeyboardMarkup:
        """
        Build post-upload success keyboard
        
        Returns:
            InlineKeyboardMarkup with upload another or main menu
        """
        keyboard = [
            [
                InlineKeyboardButton("📤 Upload Another Movie", callback_data="movie_upload_new"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def upload_error_retry() -> InlineKeyboardMarkup:
        """
        Build upload error retry keyboard
        
        Returns:
            InlineKeyboardMarkup with retry and cancel buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("🔄 Retry Upload", callback_data="movie_upload_retry"),
                InlineKeyboardButton("🔙 Back to Form", callback_data="movie_back_to_form")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)


class MoviePreviewKeyboards:
    """
    Keyboard builders for movie preview/info screens
    """

    @staticmethod
    def movie_preview(has_embed: bool = False) -> InlineKeyboardMarkup:
        """
        Build movie preview keyboard
        
        Shown after TMDB ID is validated.
        
        Args:
            has_embed: True if embed URL is already set
            
        Returns:
            InlineKeyboardMarkup with next actions
        """
        keyboard = []
        
        if has_embed:
            keyboard.append([
                InlineKeyboardButton("📝 Edit Embed URL", callback_data="movie_set_embed")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🔗 Set Embed URL", callback_data="movie_set_embed")
            ])
        
        keyboard.extend([
            [
                InlineKeyboardButton("🔄 Change TMDB ID", callback_data="movie_set_tmdb")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="movie_cancel")
            ]
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def tmdb_fetch_error() -> InlineKeyboardMarkup:
        """
        Build TMDB fetch error keyboard
        
        Shown when TMDB API fails or movie not found.
        
        Returns:
            InlineKeyboardMarkup with retry and cancel buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("🔄 Try Again", callback_data="movie_set_tmdb"),
                InlineKeyboardButton("❌ Cancel", callback_data="movie_cancel")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)


def get_movie_status_emoji(movie_state: Dict[str, Any]) -> str:
    """
    Get status emoji based on movie upload state
    
    Args:
        movie_state: Dict with movie state
        
    Returns:
        Status emoji string
    """
    if not movie_state.get('tmdb_id'):
        return "❌"
    elif not movie_state.get('embed_url'):
        return "⚠️"
    else:
        return "✅"


def format_movie_state_summary(movie_state: Dict[str, Any]) -> str:
    """
    Format movie state into summary text
    
    Args:
        movie_state: Dict with movie state
        
    Returns:
        Formatted summary string
    """
    lines = ["┌─────────────────────────────────┐"]
    lines.append("│ 🎥 Upload Movie                 │")
    lines.append("│                                 │")
    
    # TMDB ID
    if movie_state.get('tmdb_id'):
        lines.append(f"│ TMDB ID: ✅ {movie_state['tmdb_id']}                 │")
        
        # Title (if available)
        if movie_state.get('tmdb_data'):
            title = movie_state['tmdb_data'].get('title', 'Unknown')
            year = movie_state['tmdb_data'].get('year', 'N/A')
            lines.append(f"│ Title: {title} ({year})        │")
    else:
        lines.append("│ TMDB ID: [Not Set]              │")
    
    # Embed URL
    embed_status = "✅ Set" if movie_state.get('embed_url') else "[Not Set]"
    lines.append(f"│ Embed URL: {embed_status}               │")
    
    # Download URL
    download_status = "✅ Set" if movie_state.get('download_url') else "[Optional]"
    lines.append(f"│ Download URL: {download_status}        │")
    
    lines.append("│                                 │")
    
    # Status
    status_emoji = get_movie_status_emoji(movie_state)
    status_text = "Ready" if status_emoji == "✅" else "Pending" if status_emoji == "⚠️" else "Incomplete"
    lines.append(f"│ Status: {status_emoji} {status_text}           │")
    
    lines.append("└─────────────────────────────────┘")
    
    return "\n".join(lines)
