"""
Module: UI Keyboards - Series Upload
Purpose: Inline keyboard builders for series/season/episode upload flow

Provides keyboard layouts for:
- Series creation
- Season selection
- Episode status display
- Bulk/single episode upload mode
- Episode upload actions

Author: RebootGod
Date: 2025
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, List, Optional


class SeriesUploadKeyboards:
    """
    Keyboard builders for series upload flow
    """

    @staticmethod
    def series_form(series_state: Dict[str, Any]) -> InlineKeyboardMarkup:
        """
        Build series creation form keyboard
        
        Args:
            series_state: Dict with keys:
                - tmdb_id: int or None
                - tmdb_data: dict or None (series info from TMDB)
                
        Returns:
            InlineKeyboardMarkup with form buttons
        """
        keyboard = []
        
        # TMDB ID button
        tmdb_text = "📝 Set TMDB ID" if not series_state.get('tmdb_id') else "✅ Change TMDB ID"
        keyboard.append([
            InlineKeyboardButton(tmdb_text, callback_data="series_set_tmdb")
        ])
        
        # Cancel button
        keyboard.append([
            InlineKeyboardButton("❌ Cancel", callback_data="series_cancel")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def season_selection(seasons: List[Dict[str, Any]], max_per_row: int = 2) -> InlineKeyboardMarkup:
        """
        Build season selection keyboard
        
        Args:
            seasons: List of season dicts with keys:
                - season_number: int
                - episode_count: int
                - name: str
            max_per_row: Maximum buttons per row (default: 2)
                
        Returns:
            InlineKeyboardMarkup with season buttons
        """
        keyboard = []
        current_row = []
        
        for season in seasons:
            season_num = season.get('season_number', 0)
            episode_count = season.get('episode_count', 0)
            
            # Skip season 0 (specials)
            if season_num == 0:
                continue
            
            button_text = f"{season_num}️⃣ Season {season_num} ({episode_count} ep)"
            button = InlineKeyboardButton(
                button_text, 
                callback_data=f"series_season_{season_num}"
            )
            
            current_row.append(button)
            
            if len(current_row) >= max_per_row:
                keyboard.append(current_row)
                current_row = []
        
        # Add remaining buttons
        if current_row:
            keyboard.append(current_row)
        
        # Add main menu button
        keyboard.append([
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def episode_status_actions(has_incomplete: bool = False) -> InlineKeyboardMarkup:
        """
        Build episode status actions keyboard
        
        Args:
            has_incomplete: True if there are episodes that need upload
                
        Returns:
            InlineKeyboardMarkup with upload mode options
        """
        keyboard = []
        
        if has_incomplete:
            keyboard.append([
                InlineKeyboardButton("📦 Bulk Upload", callback_data="episode_bulk_mode"),
                InlineKeyboardButton("📝 Single Episode", callback_data="episode_single_mode")
            ])
        
        keyboard.extend([
            [InlineKeyboardButton("🔄 Refresh Status", callback_data="episode_refresh")],
            [
                InlineKeyboardButton("🔙 Back to Seasons", callback_data="series_back_to_seasons"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def manual_mode_actions() -> InlineKeyboardMarkup:
        """
        Build manual mode actions keyboard
        
        Shown when TMDB data is incomplete.
        
        Returns:
            InlineKeyboardMarkup with manual mode options
        """
        keyboard = [
            [
                InlineKeyboardButton("✍️ Manual Mode", callback_data="episode_manual_mode"),
                InlineKeyboardButton("🔙 Back", callback_data="series_back_to_seasons")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def bulk_upload_actions() -> InlineKeyboardMarkup:
        """
        Build bulk upload input actions keyboard
        
        Returns:
            InlineKeyboardMarkup with template and cancel buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("📋 Copy Template", callback_data="bulk_copy_template"),
                InlineKeyboardButton("❌ Cancel", callback_data="bulk_cancel")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def bulk_upload_confirmation(episode_count: int) -> InlineKeyboardMarkup:
        """
        Build bulk upload confirmation keyboard
        
        Args:
            episode_count: Number of episodes to upload
                
        Returns:
            InlineKeyboardMarkup with confirm and cancel buttons
        """
        keyboard = [
            [
                InlineKeyboardButton(f"✅ Upload {episode_count} Episodes", callback_data="bulk_upload_execute"),
                InlineKeyboardButton("❌ Cancel", callback_data="bulk_cancel")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def bulk_upload_complete(has_more: bool = True) -> InlineKeyboardMarkup:
        """
        Build bulk upload complete keyboard
        
        Args:
            has_more: True if there are more episodes to upload
                
        Returns:
            InlineKeyboardMarkup with continue options
        """
        keyboard = []
        
        if has_more:
            keyboard.append([
                InlineKeyboardButton("📤 Upload More", callback_data="episode_bulk_mode"),
                InlineKeyboardButton("🔄 Change Season", callback_data="series_back_to_seasons")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🔄 Choose Another Season", callback_data="series_back_to_seasons")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)


class ManualModeKeyboards:
    """
    Keyboard builders for manual episode upload mode
    """

    @staticmethod
    def manual_mode_choice() -> InlineKeyboardMarkup:
        """
        Build manual mode format choice keyboard
        
        Returns:
            InlineKeyboardMarkup with full and quick mode options
        """
        keyboard = [
            [
                InlineKeyboardButton("📝 Full Mode", callback_data="manual_full_mode"),
                InlineKeyboardButton("⚡ Quick Mode", callback_data="manual_quick_mode")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="manual_cancel")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def manual_upload_actions() -> InlineKeyboardMarkup:
        """
        Build manual upload input actions keyboard
        
        Returns:
            InlineKeyboardMarkup with template and cancel buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("📋 Copy Template", callback_data="manual_copy_template"),
                InlineKeyboardButton("❌ Cancel", callback_data="manual_cancel")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)


class EpisodeProgressKeyboards:
    """
    Keyboard builders for episode upload progress
    """

    @staticmethod
    def upload_in_progress() -> InlineKeyboardMarkup:
        """
        Build upload in progress keyboard
        
        Empty keyboard - user should wait.
        
        Returns:
            Empty InlineKeyboardMarkup
        """
        return InlineKeyboardMarkup([])

    @staticmethod
    def single_episode_complete() -> InlineKeyboardMarkup:
        """
        Build single episode upload complete keyboard
        
        Returns:
            InlineKeyboardMarkup with continue options
        """
        keyboard = [
            [
                InlineKeyboardButton("📤 Upload Next Episode", callback_data="episode_single_mode"),
                InlineKeyboardButton("🔄 Change Season", callback_data="series_back_to_seasons")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)


def build_episode_list_keyboard(
    episodes: List[Dict[str, Any]],
    callback_prefix: str = "episode_select_"
) -> InlineKeyboardMarkup:
    """
    Build episode selection keyboard
    
    Args:
        episodes: List of episode dicts with keys:
            - episode_number: int
            - title: str
            - complete: bool
        callback_prefix: Prefix for episode selection callbacks
            
    Returns:
        InlineKeyboardMarkup with episode buttons
    """
    keyboard = []
    
    for episode in episodes:
        episode_num = episode.get('episode_number', 0)
        title = episode.get('title', f'Episode {episode_num}')
        complete = episode.get('complete', False)
        
        # Truncate long titles
        if len(title) > 30:
            title = title[:27] + "..."
        
        emoji = "✅" if complete else "❌"
        button_text = f"{emoji} E{episode_num:02d} - {title}"
        
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"{callback_prefix}{episode_num}"
            )
        ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("🔙 Back", callback_data="series_back_to_seasons")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def format_episode_status_summary(
    series_title: str,
    season_number: int,
    episodes: List[Dict[str, Any]]
) -> str:
    """
    Format episode status into summary text
    
    Args:
        series_title: Series title
        season_number: Season number
        episodes: List of episode dicts with status
        
    Returns:
        Formatted summary string
    """
    complete_count = len([e for e in episodes if e.get('complete')])
    total_count = len(episodes)
    
    lines = ["┌─────────────────────────────────┐"]
    lines.append(f"│ 📺 {series_title[:25]}")
    lines.append(f"│ Season {season_number} - {total_count} Episodes")
    lines.append("│                                 │")
    lines.append("│ Status:                         │")
    
    for episode in episodes[:7]:  # Show first 7 episodes
        episode_num = episode.get('episode_number', 0)
        title = episode.get('title', f'Episode {episode_num}')
        complete = episode.get('complete', False)
        needs_update = episode.get('needs_update', False)
        
        # Truncate long titles
        if len(title) > 20:
            title = title[:17] + "..."
        
        if complete:
            emoji = "✅"
            status = "(Complete)"
        elif needs_update:
            emoji = "⚠️"
            status = "(No URLs)"
        else:
            emoji = "❌"
            status = ""
        
        lines.append(f"│ {emoji} E{episode_num:02d} - {title} {status}")
    
    if len(episodes) > 7:
        lines.append(f"│ ... and {len(episodes) - 7} more episodes")
    
    lines.append("│                                 │")
    lines.append(f"│ Progress: {complete_count}/{total_count} complete          │")
    lines.append("└─────────────────────────────────┘")
    
    return "\n".join(lines)
