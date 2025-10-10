"""
Chat Finder utility untuk mencari channel/group by name.
Support fuzzy matching untuk flexibility.
"""

import logging
from typing import Optional, List
from telethon.tl.types import Chat, Channel, User
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class ChatFinder:
    """
    Utility untuk find chat entities (channels, groups) by name.
    """
    
    def __init__(self, telegram_client):
        """
        Initialize ChatFinder.
        
        Args:
            telegram_client: TelegramClient instance dari Telethon
        """
        self.client = telegram_client
        self._dialogs_cache: Optional[List] = None
    
    async def find_by_name(
        self, 
        name: str, 
        exact_match: bool = False,
        refresh_cache: bool = False
    ):
        """
        Find chat entity by name.
        
        Args:
            name: Nama channel/group yang dicari
            exact_match: True untuk exact match, False untuk fuzzy match
            refresh_cache: True untuk refresh dialogs cache
            
        Returns:
            Chat entity jika ditemukan, None jika tidak
        """
        try:
            # Get dialogs (dengan cache)
            dialogs = await self._get_dialogs(refresh_cache)
            
            name_lower = name.lower()
            best_match = None
            best_score = 0
            
            for dialog in dialogs:
                entity = dialog.entity
                entity_name = self._get_entity_name(entity)
                
                if not entity_name:
                    continue
                
                entity_name_lower = entity_name.lower()
                
                # Exact match
                if exact_match:
                    if entity_name_lower == name_lower:
                        logger.info(f"Found exact match: {entity_name}")
                        return entity
                else:
                    # Fuzzy match
                    score = self._calculate_similarity(name_lower, entity_name_lower)
                    
                    if score > best_score:
                        best_score = score
                        best_match = entity
            
            # Return best match jika similarity > 0.6
            if best_match and best_score > 0.6:
                logger.info(
                    f"Found fuzzy match: {self._get_entity_name(best_match)} "
                    f"(similarity: {best_score:.2f})"
                )
                return best_match
            
            logger.warning(f"No match found for: {name}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to find chat by name '{name}': {e}")
            raise
    
    async def find_user_by_username(self, username: str):
        """
        Find user by username.
        
        Args:
            username: Username (tanpa @)
            
        Returns:
            User entity jika ditemukan
            
        Raises:
            Exception: Jika user tidak ditemukan
        """
        try:
            # Remove @ jika ada
            username = username.lstrip('@')
            
            # Get entity by username
            entity = await self.client.get_entity(username)
            
            if isinstance(entity, User):
                logger.info(f"Found user: @{username}")
                return entity
            else:
                raise Exception(f"Entity @{username} is not a user")
                
        except Exception as e:
            logger.error(f"Failed to find user @{username}: {e}")
            raise
    
    async def _get_dialogs(self, refresh: bool = False) -> List:
        """
        Get dialogs dengan caching.
        
        Args:
            refresh: True untuk refresh cache
            
        Returns:
            List of dialogs
        """
        if refresh or self._dialogs_cache is None:
            logger.info("Fetching dialogs from Telegram...")
            self._dialogs_cache = await self.client.get_dialogs()
            logger.info(f"Cached {len(self._dialogs_cache)} dialogs")
        
        return self._dialogs_cache
    
    def _get_entity_name(self, entity) -> Optional[str]:
        """
        Get name dari entity.
        
        Args:
            entity: Telegram entity
            
        Returns:
            Entity name atau None
        """
        if isinstance(entity, (Chat, Channel)):
            return entity.title
        elif isinstance(entity, User):
            if entity.username:
                return entity.username
            elif entity.first_name:
                name = entity.first_name
                if entity.last_name:
                    name += f" {entity.last_name}"
                return name
        
        return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity score antara dua string.
        
        Args:
            str1: String pertama
            str2: String kedua
            
        Returns:
            Similarity score (0.0 - 1.0)
        """
        return SequenceMatcher(None, str1, str2).ratio()
    
    def clear_cache(self):
        """Clear dialogs cache."""
        self._dialogs_cache = None
        logger.info("Dialogs cache cleared")
    
    async def get_all_chats(self, refresh: bool = False) -> List[dict]:
        """
        Get list semua chats (untuk debugging/listing).
        
        Args:
            refresh: True untuk refresh cache
            
        Returns:
            List of dict dengan chat info
        """
        dialogs = await self._get_dialogs(refresh)
        
        chats = []
        for dialog in dialogs:
            entity = dialog.entity
            entity_name = self._get_entity_name(entity)
            
            if entity_name:
                chat_info = {
                    'name': entity_name,
                    'type': type(entity).__name__,
                    'id': entity.id
                }
                
                if isinstance(entity, Channel):
                    chat_info['is_broadcast'] = entity.broadcast
                    chat_info['is_megagroup'] = entity.megagroup
                
                chats.append(chat_info)
        
        return chats


def create_chat_finder(telegram_client) -> ChatFinder:
    """
    Factory function untuk create ChatFinder instance.
    
    Args:
        telegram_client: TelegramClient instance
        
    Returns:
        ChatFinder instance
    """
    return ChatFinder(telegram_client)
