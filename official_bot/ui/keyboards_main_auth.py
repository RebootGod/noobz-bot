"""
Module: UI Keyboards - Main Menu & Authentication
Purpose: Inline keyboard builders for main menu and auth flows

Provides keyboard layouts for:
- Main menu (after successful login)
- Authentication retry/cancel
- Master vs regular user menus

Author: RebootGod
Date: 2025
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional


class MainMenuKeyboards:
    """
    Keyboard builders for main menu and authentication
    
    All keyboards use callback_data for button actions.
    """

    @staticmethod
    def main_menu(is_master: bool = False) -> InlineKeyboardMarkup:
        """
        Build main menu keyboard
        
        Args:
            is_master: True if user has master password access
            
        Returns:
            InlineKeyboardMarkup with main menu buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("🎥 Upload Movie", callback_data="menu_movie"),
                InlineKeyboardButton("📺 Upload Series", callback_data="menu_series")
            ],
            [
                InlineKeyboardButton("📊 My Stats", callback_data="menu_stats"),
                InlineKeyboardButton("❓ Help", callback_data="menu_help")
            ]
        ]
        
        # Add password manager button for master users
        if is_master:
            keyboard.insert(1, [
                InlineKeyboardButton("🔐 Password Manager", callback_data="menu_password_manager")
            ])
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def auth_retry() -> InlineKeyboardMarkup:
        """
        Build authentication retry keyboard
        
        Shown when password is incorrect.
        
        Returns:
            InlineKeyboardMarkup with retry/cancel buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("🔄 Retry", callback_data="auth_retry"),
                InlineKeyboardButton("❌ Cancel", callback_data="auth_cancel")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def cancel_only() -> InlineKeyboardMarkup:
        """
        Build cancel-only keyboard
        
        Generic cancel button for various flows.
        
        Returns:
            InlineKeyboardMarkup with single cancel button
        """
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_and_home() -> InlineKeyboardMarkup:
        """
        Build back and home keyboard
        
        Navigation buttons for sub-menus.
        
        Returns:
            InlineKeyboardMarkup with back and home buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 Back", callback_data="back"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def continue_or_menu() -> InlineKeyboardMarkup:
        """
        Build continue or main menu keyboard
        
        Used after successful operations.
        
        Returns:
            InlineKeyboardMarkup with continue and menu buttons
        """
        keyboard = [
            [
                InlineKeyboardButton("📤 Upload Another", callback_data="upload_another"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)


class HelpKeyboards:
    """
    Keyboard builders for help and info screens
    """

    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """
        Build help menu keyboard
        
        Returns:
            InlineKeyboardMarkup with help topics
        """
        keyboard = [
            [
                InlineKeyboardButton("🎬 Movie Upload Help", callback_data="help_movie"),
                InlineKeyboardButton("📺 Series Upload Help", callback_data="help_series")
            ],
            [
                InlineKeyboardButton("📦 Bulk Upload Help", callback_data="help_bulk"),
                InlineKeyboardButton("✍️ Manual Mode Help", callback_data="help_manual")
            ],
            [
                InlineKeyboardButton("🔐 Password Manager Help", callback_data="help_password")
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def help_back() -> InlineKeyboardMarkup:
        """
        Build help back button
        
        Returns to help menu.
        
        Returns:
            InlineKeyboardMarkup with back to help button
        """
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Help", callback_data="menu_help")]
        ]
        
        return InlineKeyboardMarkup(keyboard)


class StatsKeyboards:
    """
    Keyboard builders for statistics screens
    """

    @staticmethod
    def stats_menu() -> InlineKeyboardMarkup:
        """
        Build stats menu keyboard
        
        Returns:
            InlineKeyboardMarkup with stats options
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 My Uploads", callback_data="stats_my_uploads"),
                InlineKeyboardButton("📈 Recent Activity", callback_data="stats_recent")
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def stats_back() -> InlineKeyboardMarkup:
        """
        Build stats back button
        
        Returns to stats menu.
        
        Returns:
            InlineKeyboardMarkup with back to stats button
        """
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Stats", callback_data="menu_stats")]
        ]
        
        return InlineKeyboardMarkup(keyboard)


def build_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str,
    extra_buttons: Optional[List[List[InlineKeyboardButton]]] = None
) -> InlineKeyboardMarkup:
    """
    Build pagination keyboard
    
    Args:
        current_page: Current page number (1-based)
        total_pages: Total number of pages
        callback_prefix: Prefix for pagination callbacks (e.g., "page_")
        extra_buttons: Optional additional button rows
        
    Returns:
        InlineKeyboardMarkup with pagination controls
    """
    keyboard = []
    
    # Pagination row
    pagination_row = []
    
    if current_page > 1:
        pagination_row.append(
            InlineKeyboardButton("⬅️ Previous", callback_data=f"{callback_prefix}{current_page - 1}")
        )
    
    pagination_row.append(
        InlineKeyboardButton(f"📄 {current_page}/{total_pages}", callback_data="page_info")
    )
    
    if current_page < total_pages:
        pagination_row.append(
            InlineKeyboardButton("Next ➡️", callback_data=f"{callback_prefix}{current_page + 1}")
        )
    
    keyboard.append(pagination_row)
    
    # Add extra buttons if provided
    if extra_buttons:
        keyboard.extend(extra_buttons)
    
    return InlineKeyboardMarkup(keyboard)


def build_confirmation_keyboard(
    confirm_callback: str,
    cancel_callback: str = "cancel",
    confirm_text: str = "✅ Confirm",
    cancel_text: str = "❌ Cancel"
) -> InlineKeyboardMarkup:
    """
    Build confirmation keyboard
    
    Generic confirm/cancel keyboard for various operations.
    
    Args:
        confirm_callback: Callback data for confirm button
        cancel_callback: Callback data for cancel button
        confirm_text: Text for confirm button
        cancel_text: Text for cancel button
        
    Returns:
        InlineKeyboardMarkup with confirm and cancel buttons
    """
    keyboard = [
        [
            InlineKeyboardButton(confirm_text, callback_data=confirm_callback),
            InlineKeyboardButton(cancel_text, callback_data=cancel_callback)
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)
