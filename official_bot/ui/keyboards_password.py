"""
Module: UI Keyboards - Password Manager
Purpose: Inline keyboard builders for password management (Master only)

Provides keyboard layouts for:
- Password manager main menu
- Add new password
- Revoke password
- View statistics
- Password type selection

Author: RebootGod
Date: 2025
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any, Optional


class PasswordManagerKeyboards:
    """
    Keyboard builders for password management (Master access only)
    """

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Build password manager main menu keyboard
        
        Returns:
            InlineKeyboardMarkup with password management options
        """
        keyboard = [
            [
                InlineKeyboardButton("➕ Add Password", callback_data="password_add"),
                InlineKeyboardButton("🗑️ Revoke Password", callback_data="password_revoke")
            ],
            [
                InlineKeyboardButton("📊 View Stats", callback_data="password_stats")
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def password_type_selection() -> InlineKeyboardMarkup:
        """
        Build password type selection keyboard
        
        Returns:
            InlineKeyboardMarkup with master and admin options
        """
        keyboard = [
            [
                InlineKeyboardButton("👑 Master Password", callback_data="password_type_master"),
                InlineKeyboardButton("👤 Admin Password", callback_data="password_type_admin")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="password_cancel")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def password_creation_actions() -> InlineKeyboardMarkup:
        """
        Build password creation input actions keyboard
        
        Returns:
            InlineKeyboardMarkup with cancel button
        """
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="password_cancel")]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def password_created_actions() -> InlineKeyboardMarkup:
        """
        Build password created success keyboard
        
        Returns:
            InlineKeyboardMarkup with back to manager and main menu
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Back to Manager", callback_data="menu_password_manager"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def password_list_for_revoke(
        passwords: List[Dict[str, Any]],
        exclude_current: bool = True
    ) -> InlineKeyboardMarkup:
        """
        Build password list keyboard for revocation
        
        Args:
            passwords: List of password dicts with keys:
                - id: int
                - password_hint: str
                - password_type: str
                - last_used_at: str or None
                - total_uploads: int
            exclude_current: Exclude current user's password
                
        Returns:
            InlineKeyboardMarkup with password buttons
        """
        keyboard = []
        
        for password in passwords:
            password_id = password.get('id')
            hint = password.get('password_hint', '****????')
            password_type = password.get('password_type', 'admin')
            last_used = password.get('last_used_at', 'Never')
            uploads = password.get('total_uploads', 0)
            
            # Format last used
            if last_used and last_used != 'Never':
                # Simplified time display
                last_used_display = "recently" if "ago" in last_used.lower() else last_used
            else:
                last_used_display = "Never"
            
            button_text = f"🔑 {hint} ({password_type.title()})"
            sub_text = f"   Last: {last_used_display} • Uploads: {uploads}"
            
            keyboard.append([
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"password_revoke_confirm_{password_id}"
                )
            ])
        
        # Add cancel button
        keyboard.append([
            InlineKeyboardButton("❌ Cancel", callback_data="password_cancel")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def revoke_confirmation(password_data: Dict[str, Any]) -> InlineKeyboardMarkup:
        """
        Build password revoke confirmation keyboard
        
        Args:
            password_data: Dict with password information
                
        Returns:
            InlineKeyboardMarkup with confirm and cancel buttons
        """
        password_id = password_data.get('id')
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm Revoke", callback_data=f"password_revoke_execute_{password_id}"),
                InlineKeyboardButton("❌ Cancel", callback_data="password_cancel")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def revoke_success() -> InlineKeyboardMarkup:
        """
        Build password revoke success keyboard
        
        Returns:
            InlineKeyboardMarkup with back to manager and main menu
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Back to Manager", callback_data="menu_password_manager"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def stats_back() -> InlineKeyboardMarkup:
        """
        Build stats back keyboard
        
        Returns:
            InlineKeyboardMarkup with back to manager button
        """
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Manager", callback_data="menu_password_manager")]
        ]
        
        return InlineKeyboardMarkup(keyboard)


class PasswordStatsKeyboards:
    """
    Keyboard builders for password statistics
    """

    @staticmethod
    def stats_menu() -> InlineKeyboardMarkup:
        """
        Build password stats menu keyboard
        
        Returns:
            InlineKeyboardMarkup with stats options
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Overall Stats", callback_data="password_stats_overall"),
                InlineKeyboardButton("👥 By Password", callback_data="password_stats_by_password")
            ],
            [
                InlineKeyboardButton("📈 Recent Activity", callback_data="password_stats_recent")
            ],
            [
                InlineKeyboardButton("🔙 Back to Manager", callback_data="menu_password_manager")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def stats_detail_back() -> InlineKeyboardMarkup:
        """
        Build stats detail back keyboard
        
        Returns:
            InlineKeyboardMarkup with back to stats button
        """
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Stats", callback_data="password_stats")]
        ]
        
        return InlineKeyboardMarkup(keyboard)


def format_password_list(passwords: List[Dict[str, Any]]) -> str:
    """
    Format password list into display text
    
    Args:
        passwords: List of password dicts
        
    Returns:
        Formatted password list string
    """
    lines = ["┌─────────────────────────────────┐"]
    lines.append("│ 🔐 Password Management          │")
    lines.append("│                                 │")
    lines.append(f"│ Active Passwords: {len(passwords)}             │")
    lines.append("│                                 │")
    
    for password in passwords:
        hint = password.get('password_hint', '****????')
        password_type = password.get('password_type', 'admin')
        created_at = password.get('created_at', 'Unknown')
        last_used = password.get('last_used_at', 'Never')
        uploads = password.get('total_uploads', 0)
        is_current = password.get('is_current', False)
        
        type_emoji = "👑" if password_type == 'master' else "👤"
        current_marker = " - You" if is_current else ""
        
        lines.append(f"│ {type_emoji} {hint} ({password_type.title()}){current_marker}      │")
        lines.append(f"│    Created: {created_at[:10]}        │")
        lines.append(f"│    Last used: {last_used}       │")
        
        if not is_current:
            lines.append(f"│    Uploads: {uploads}                  │")
        
        lines.append("│                                 │")
    
    lines.append("└─────────────────────────────────┘")
    
    return "\n".join(lines)


def format_password_stats(stats: Dict[str, Any]) -> str:
    """
    Format password statistics into display text
    
    Args:
        stats: Dict with keys:
            - total_uploads: int
            - by_type: dict
            - by_password: list
            - recent_activity: list
        
    Returns:
        Formatted stats string
    """
    lines = ["┌─────────────────────────────────┐"]
    lines.append("│ 📊 Upload Statistics            │")
    lines.append("│                                 │")
    lines.append(f"│ Total Uploads: {stats.get('total_uploads', 0)}               │")
    lines.append("│                                 │")
    
    # By type
    by_type = stats.get('by_type', {})
    lines.append("│ By Type:                        │")
    lines.append(f"│ 🎬 Movies: {by_type.get('movie', 0)}                   │")
    lines.append(f"│ 📺 Series: {by_type.get('series', 0)}                    │")
    lines.append(f"│ 📹 Episodes: {by_type.get('episode', 0)}                 │")
    lines.append("│                                 │")
    
    # By password
    by_password = stats.get('by_password', [])
    if by_password:
        lines.append("│ By Password:                    │")
        for pwd_stat in by_password[:4]:  # Show top 4
            hint = pwd_stat.get('hint', '****????')
            password_type = pwd_stat.get('type', 'admin')
            uploads = pwd_stat.get('uploads', 0)
            lines.append(f"│ {hint} ({password_type}): {uploads}           │")
        lines.append("│                                 │")
    
    # Recent activity
    recent = stats.get('recent_activity', [])
    if recent:
        lines.append("│ Recent Activity:                │")
        for activity in recent[:3]:  # Show last 3
            date = activity.get('date', '')
            upload_type = activity.get('type', 'upload')
            lines.append(f"│ {date} - {upload_type}   │")
    
    lines.append("└─────────────────────────────────┘")
    
    return "\n".join(lines)


def format_revoke_confirmation(password_data: Dict[str, Any]) -> str:
    """
    Format password revoke confirmation text
    
    Args:
        password_data: Dict with password information
        
    Returns:
        Formatted confirmation text
    """
    hint = password_data.get('password_hint', '****????')
    password_type = password_data.get('password_type', 'admin')
    created_at = password_data.get('created_at', 'Unknown')
    total_uploads = password_data.get('total_uploads', 0)
    last_used = password_data.get('last_used_at', 'Never')
    
    lines = ["⚠️ Confirm Revocation\n"]
    lines.append(f"Password: {hint} ({password_type.title()})")
    lines.append(f"Created: {created_at}")
    lines.append(f"Total Uploads: {total_uploads}")
    lines.append(f"Last Used: {last_used}\n")
    lines.append("This action cannot be undone.")
    lines.append("Active sessions will be terminated.")
    
    return "\n".join(lines)
